import pytest

from nexios import NexiosApp, get_application
from nexios.dependencies import Context, Depend
from nexios.http import Request, Response
from nexios.routing import Router
from nexios.testing import Client
from nexios.views import APIView

app: NexiosApp = get_application()
router = Router("/mounted")


@app.get("/func/home")
async def homepage(req: Request, res: Response):

    return res.text("Hello from nexios")


class ClassBasedHandler(APIView):

    async def get(self, req: Request, res: Response):
        return res.text("Hello from nexios")


@router.get("/check")
async def mounted_route_handler(req: Request, res: Response):
    return res.text("Hello from nexios")


@router.get("/hello/{name}")
@app.get("/hello/{name}")
async def route_prams(req: Request, res: Response):
    name = req.path_params.name  # type: ignore
    return res.text(f"hello, {name}")


app.add_route(ClassBasedHandler.as_route("/class/home"))
app.mount_router(router=router)


@pytest.fixture
async def async_client():
    async with Client(app) as c:
        yield c


async def test_func_route(async_client: Client):
    response = await async_client.get("/func/home")
    assert response.status_code == 200
    assert response.text == "Hello from nexios"


async def test_class_route(async_client: Client):
    response = await async_client.get("/class/home")
    assert response.status_code == 200
    assert response.text == "Hello from nexios"


async def test_mounted_router(async_client: Client):
    response = await async_client.get("/mounted/check")
    assert response.status_code == 200
    assert response.text == "Hello from nexios"


async def test_route_path_params(async_client: Client):
    response = await async_client.get("/hello/dunamis")
    assert response.status_code == 200
    assert response.text == "hello, dunamis"


async def test_mounted_route_path_params(async_client: Client):
    response = await async_client.get("/mounted/hello/dunamis")
    assert response.status_code == 200
    assert response.text == "hello, dunamis"


async def test_405(async_client: Client):
    response = await async_client.post("/func/home")
    assert response.status_code == 405


@app.get("/test-context")
async def context_handler(req: Request, res: Response, context=Context()):
    # context should be injected automatically
    return res.json({"path": context.request.url.path})


async def context_dep(context=Context()):
    # context should be injected automatically
    return context.request.url.path


@app.get("/test-context-dep")
async def context_dep_handler(req: Request, res: Response, path=Depend(context_dep)):
    return res.json({"path": path})


async def test_context_injection(async_client: Client):
    response = await async_client.get("/test-context")
    assert response.status_code == 200
    assert response.json()["path"] == "/test-context"


async def test_context_dep_injection(async_client: Client):
    response = await async_client.get("/test-context-dep")
    assert response.status_code == 200
    assert response.json()["path"] == "/test-context-dep"
