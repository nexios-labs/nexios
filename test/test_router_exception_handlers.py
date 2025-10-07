import pytest
from typing import Tuple, Optional

from nexios import NexiosApp
from nexios.http import Request, Response
from nexios.routing.http import Router
from nexios.testing import Client
from nexios.exceptions import HTTPException, NotFoundException


class CustomRouterException(Exception):
    pass


class SpecificRouterException(Exception):
    pass


@pytest.fixture
async def router_client():
    app = NexiosApp()
    router = Router()
    
    # Add a global exception handler to the app
    @app.add_exception_handler(404)
    async def global_not_found_handler(req: Request, res: Response, exc: Exception):
        return res.json({"error": "Global not found"}, status_code=404)
    
    # Add routes to the router
    @router.route("/router-route")
    async def router_route(req: Request, res: Response):
        raise CustomRouterException("Router level error")
    
    @router.route("/specific-exception")
    async def specific_route(req: Request, res: Response):
        raise SpecificRouterException("Specific router error")
    
    @router.route("/not-found")
    async def not_found_route(req: Request, res: Response):
        raise NotFoundException()
    
    # Add router-level exception handlers
    @router.add_exception_handler(CustomRouterException)
    async def handle_router_exception(req: Request, res: Response, exc: CustomRouterException):
        return res.json({"error": str(exc), "handled_by": "router"}, status_code=400)
    
    @router.add_exception_handler(SpecificRouterException)
    async def handle_specific_exception(req: Request, res: Response, exc: SpecificRouterException):
        return res.json({"error": str(exc), "handled_by": "router"}, status_code=422)
    
    # Mount the router
    app.mount_router(router, "/api")
    
    # Add a direct route to the app for comparison
    @app.get("/app-route")
    async def app_route(req: Request, res: Response):
        raise CustomRouterException("App level error")
    
    # Add a global handler for CustomRouterException in the app
    @app.add_exception_handler(CustomRouterException)
    async def handle_app_exception(req: Request, res: Response, exc: CustomRouterException):
        return res.json({"error": str(exc), "handled_by": "app"}, status_code=400)
    
    async with Client(app) as client:
        yield client

async def test_router_level_exception_handling(router_client: Client):
    """Test that router-level exception handlers take precedence over app-level ones."""
    # This should be handled by the router's exception handler
    response = await router_client.get("/api/router-route")
    assert response.status_code == 400
    assert response.json() == {"error": "Router level error", "handled_by": "router"}
    
    # This should be handled by the app's exception handler
    response = await router_client.get("/app-route")
    assert response.status_code == 400
    assert response.json() == {"error": "App level error", "handled_by": "app"}


async def test_specific_router_exception(router_client: Client):
    """Test that specific exceptions in the router are handled correctly."""
    response = await router_client.get("/api/specific-exception")
    assert response.status_code == 422
    assert response.json() == {"error": "Specific router error", "handled_by": "router"}



async def test_nested_router_exception_handling():
    """Test exception handling with nested routers."""
    app = NexiosApp()
    
    # Parent router
    parent_router = Router()
    
    # Child router
    child_router = Router()
    
    # Add a route to the child router that raises an exception
    @child_router.route("/child-route")
    async def child_route(req: Request, res: Response):
        raise CustomRouterException("Child router error")
    
    # Add an exception handler to the child router
    @child_router.add_exception_handler(CustomRouterException)
    async def handle_child_exception(req: Request, res: Response, exc: CustomRouterException):
        return res.json({"error": str(exc), "handled_by": "child_router"}, status_code=400)
    
    # Add an exception handler to the parent router (should be overridden by child's handler)
    @parent_router.add_exception_handler(CustomRouterException)
    async def handle_parent_exception(req: Request, res: Response, exc: CustomRouterException):
        return res.json({"error": "This should not be called"}, status_code=500)
    
    # Mount the child router under the parent router
    parent_router.mount_router(child_router, "/child")
    
    # Mount the parent router under the app
    app.mount_router(parent_router, "/api")
    
    # Test that the child router's handler is used
    async with Client(app) as client:
        response = await client.get("/api/child/child-route")
        assert response.status_code == 400
        assert response.json() == {"error": "Child router error", "handled_by": "child_router"}


async def test_status_code_handling_in_router():
    """Test that status code handlers work in routers."""
    app = NexiosApp()
    router = Router()
    
    # Add a route that raises an HTTPException
    @router.route("/teapot")
    async def teapot_route(req: Request, res: Response):
        raise HTTPException(status_code=418, detail="I'm a teapot")
    
    # Add a status code handler to the router
    @router.add_exception_handler(418)
    async def handle_teapot(req: Request, res: Response, exc: HTTPException):
        return res.json({"message": "Router: This is a teapot"}, status_code=418)
    
    # Add a different handler to the app
    @app.add_exception_handler(418)
    async def app_handle_teapot(req: Request, res: Response, exc: HTTPException):
        return res.json({"message": "App: This is a teapot"}, status_code=418)
    
    # Mount the router
    app.mount_router(router, "/api")
    
    # The router's handler should take precedence
    async with Client(app) as client:
        response = await client.get("/api/teapot")
        assert response.status_code == 418
        assert response.json() == {"message": "Router: This is a teapot"}
        
        # The app's handler should be used for non-router routes
        @app.get("/app-teapot")
        async def app_teapot(req: Request, res: Response):
            raise HTTPException(status_code=418, detail="I'm a teapot")
        
        response = await client.get("/app-teapot")
        assert response.status_code == 418
        assert response.json() == {"message": "App: This is a teapot"}
