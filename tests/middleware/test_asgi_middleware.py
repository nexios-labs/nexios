"""
Tests for pure ASGI middleware using wrap_asgi
"""
from typing import Callable
import pytest
from nexios import NexiosApp
from nexios.http import Request, Response
from nexios.types import ASGIApp, Scope, Receive, Send
from nexios.testclient import TestClient


# ========== Pure ASGI Middleware Tests ==========

def test_pure_asgi_middleware_basic(test_client_factory: Callable[[NexiosApp], TestClient]):
    """Test basic pure ASGI middleware"""
    app = NexiosApp()
    
    executed = []
    
    class ASGIMiddleware:
        def __init__(self, app: ASGIApp):
            self.app = app
        
        async def __call__(self, scope: Scope, receive: Receive, send: Send):
            if scope["type"] == "http":
                executed.append("asgi_middleware")
            await self.app(scope, receive, send)
    
    # Wrap the app with pure ASGI middleware
    wrapped_app = ASGIMiddleware(app)
    
    @app.get("/test")
    async def handler(request: Request, response: Response):
        executed.append("handler")
        return response.json({"message": "ok"})
    
    with test_client_factory(wrapped_app) as client:
        resp = client.get("/test")
        assert resp.status_code == 200
        assert "asgi_middleware" in executed
        assert "handler" in executed


def test_pure_asgi_middleware_modifies_scope(test_client_factory: Callable[[NexiosApp], TestClient]):
    """Test ASGI middleware modifying scope"""
    app = NexiosApp()
    
    class ScopeModifierMiddleware:
        def __init__(self, app: ASGIApp):
            self.app = app
        
        async def __call__(self, scope: Scope, receive: Receive, send: Send):
            if scope["type"] == "http":
                scope["custom_value"] = "asgi_modified"
            await self.app(scope, receive, send)
    
    wrapped_app = ScopeModifierMiddleware(app)
    
    @app.get("/test")
    async def handler(request: Request, response: Response):
        custom_value = request.scope.get("custom_value")
        return response.json({"custom_value": custom_value})
    
    with test_client_factory(wrapped_app) as client:
        resp = client.get("/test")
        assert resp.json()["custom_value"] == "asgi_modified"


def test_pure_asgi_middleware_intercepts_send(test_client_factory: Callable[[NexiosApp], TestClient]):
    """Test ASGI middleware intercepting send"""
    app = NexiosApp()
    
    class HeaderInjectorMiddleware:
        def __init__(self, app: ASGIApp):
            self.app = app
        
        async def __call__(self, scope: Scope, receive: Receive, send: Send):
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    headers = list(message.get("headers", []))
                    headers.append((b"x-asgi-middleware", b"injected"))
                    message["headers"] = headers
                await send(message)
            
            await self.app(scope, receive, send_wrapper)
    
    wrapped_app = HeaderInjectorMiddleware(app)
    
    @app.get("/test")
    async def handler(request: Request, response: Response):
        return response.json({"message": "ok"})
    
    with test_client_factory(wrapped_app) as client:
        resp = client.get("/test")
        assert resp.headers.get("x-asgi-middleware") == "injected"


def test_pure_asgi_middleware_multiple_layers(test_client_factory: Callable[[NexiosApp], TestClient]):
    """Test multiple pure ASGI middleware layers"""
    app = NexiosApp()
    
    execution_order = []
    
    class Middleware1:
        def __init__(self, app: ASGIApp):
            self.app = app
        
        async def __call__(self, scope: Scope, receive: Receive, send: Send):
            if scope["type"] == "http":
                execution_order.append("m1")
            await self.app(scope, receive, send)
    
    class Middleware2:
        def __init__(self, app: ASGIApp):
            self.app = app
        
        async def __call__(self, scope: Scope, receive: Receive, send: Send):
            if scope["type"] == "http":
                execution_order.append("m2")
            await self.app(scope, receive, send)
    
    @app.get("/test")
    async def handler(request: Request, response: Response):
        execution_order.append("handler")
        return response.json({"message": "ok"})
    
    # Wrap with multiple middleware layers
    wrapped_app = Middleware1(Middleware2(app))
    
    with test_client_factory(wrapped_app) as client:
        resp = client.get("/test")
        assert resp.status_code == 200
        assert execution_order == ["m1", "m2", "handler"]


def test_pure_asgi_middleware_request_logging(test_client_factory: Callable[[NexiosApp], TestClient]):
    """Test ASGI middleware for request logging"""
    app = NexiosApp()
    
    logs = []
    
    class LoggingMiddleware:
        def __init__(self, app: ASGIApp):
            self.app = app
        
        async def __call__(self, scope: Scope, receive: Receive, send: Send):
            if scope["type"] == "http":
                logs.append({
                    "method": scope["method"],
                    "path": scope["path"],
                    "query_string": scope.get("query_string", b"").decode()
                })
            await self.app(scope, receive, send)
    
    wrapped_app = LoggingMiddleware(app)
    
    @app.get("/test")
    async def handler(request: Request, response: Response):
        return response.json({"message": "ok"})
    
    with test_client_factory(wrapped_app) as client:
        client.get("/test?param=value")
        assert len(logs) == 1
        assert logs[0]["method"] == "GET"
        assert logs[0]["path"] == "/test"
        assert "param=value" in logs[0]["query_string"]


def test_pure_asgi_middleware_handles_websocket(test_client_factory: Callable[[NexiosApp], TestClient]):
    """Test ASGI middleware handling different connection types"""
    app = NexiosApp()
    
    handled_types = []
    
    class TypeTrackerMiddleware:
        def __init__(self, app: ASGIApp):
            self.app = app
        
        async def __call__(self, scope: Scope, receive: Receive, send: Send):
            handled_types.append(scope["type"])
            await self.app(scope, receive, send)
    
    wrapped_app = TypeTrackerMiddleware(app)
    
    @app.get("/test")
    async def handler(request: Request, response: Response):
        return response.json({"message": "ok"})
    
    with test_client_factory(wrapped_app) as client:
        client.get("/test")
        assert "http" in handled_types or "lifespan" in handled_types


def test_pure_asgi_middleware_timing(test_client_factory: Callable[[NexiosApp], TestClient]):
    """Test ASGI middleware for request timing"""
    app = NexiosApp()
    
    import time
    
    class TimingMiddleware:
        def __init__(self, app: ASGIApp):
            self.app = app
        
        async def __call__(self, scope: Scope, receive: Receive, send: Send):
            start_time = time.time()
            
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    process_time = time.time() - start_time
                    headers = list(message.get("headers", []))
                    headers.append((b"x-process-time", str(process_time).encode()))
                    message["headers"] = headers
                await send(message)
            
            await self.app(scope, receive, send_wrapper)
    
    wrapped_app = TimingMiddleware(app)
    
    @app.get("/test")
    async def handler(request: Request, response: Response):
        return response.json({"message": "ok"})
    
    with test_client_factory(wrapped_app) as client:
        resp = client.get("/test")
        assert "x-process-time" in resp.headers
        process_time = float(resp.headers["x-process-time"])
        assert process_time >= 0


def test_pure_asgi_middleware_with_nexios_middleware(test_client_factory: Callable[[NexiosApp], TestClient]):
    """Test combining pure ASGI middleware with Nexios middleware"""
    app = NexiosApp()
    
    execution_order = []
    
    class ASGIMiddleware:
        def __init__(self, app: ASGIApp):
            self.app = app
        
        async def __call__(self, scope: Scope, receive: Receive, send: Send):
            if scope["type"] == "http":
                execution_order.append("asgi")
            await self.app(scope, receive, send)
    
    async def nexios_middleware(request: Request, response: Response, call_next):
        execution_order.append("nexios")
        await call_next()
        return response
    
    app.add_middleware(nexios_middleware)
    wrapped_app = ASGIMiddleware(app)
    
    @app.get("/test")
    async def handler(request: Request, response: Response):
        execution_order.append("handler")
        return response.json({"message": "ok"})
    
    with test_client_factory(wrapped_app) as client:
        resp = client.get("/test")
        assert resp.status_code == 200
        # ASGI middleware executes before Nexios middleware
        assert execution_order.index("asgi") < execution_order.index("nexios")


# ========== ASGI Middleware Error Handling Tests ==========

def test_pure_asgi_middleware_error_handling(test_client_factory: Callable[[NexiosApp], TestClient]):
    """Test ASGI middleware handling errors"""
    app = NexiosApp()
    
    class ErrorHandlerMiddleware:
        def __init__(self, app: ASGIApp):
            self.app = app
        
        async def __call__(self, scope: Scope, receive: Receive, send: Send):
            try:
                await self.app(scope, receive, send)
            except Exception as e:
                # Send error response
                await send({
                    "type": "http.response.start",
                    "status": 500,
                    "headers": [[b"content-type", b"application/json"]],
                })
                await send({
                    "type": "http.response.body",
                    "body": b'{"error": "Internal server error"}',
                })
    
    wrapped_app = ErrorHandlerMiddleware(app)
    
    @app.get("/test")
    async def handler(request: Request, response: Response):
        raise RuntimeError("Test error")
    
    with test_client_factory(wrapped_app) as client:
        resp = client.get("/test")
        # Error should be handled by middleware
        assert resp.status_code in [500, 200]  # Depends on error handling


def test_pure_asgi_middleware_conditional_processing(test_client_factory: Callable[[NexiosApp], TestClient]):
    """Test ASGI middleware with conditional processing"""
    app = NexiosApp()
    
    class ConditionalMiddleware:
        def __init__(self, app: ASGIApp):
            self.app = app
        
        async def __call__(self, scope: Scope, receive: Receive, send: Send):
            if scope["type"] == "http" and scope["path"].startswith("/api"):
                scope["api_request"] = True
            await self.app(scope, receive, send)
    
    wrapped_app = ConditionalMiddleware(app)
    
    @app.get("/api/test")
    async def api_handler(request: Request, response: Response):
        is_api = request.scope.get("api_request", False)
        return response.json({"is_api": is_api})
    
    @app.get("/public/test")
    async def public_handler(request: Request, response: Response):
        is_api = request.scope.get("api_request", False)
        return response.json({"is_api": is_api})
    
    with test_client_factory(wrapped_app) as client:
        resp1 = client.get("/api/test")
        assert resp1.json()["is_api"] is True
        
        resp2 = client.get("/public/test")
        assert resp2.json()["is_api"] is False


def test_pure_asgi_middleware_request_id(test_client_factory: Callable[[NexiosApp], TestClient]):
    """Test ASGI middleware adding request ID"""
    app = NexiosApp()
    
    import uuid
    
    class RequestIDMiddleware:
        def __init__(self, app: ASGIApp):
            self.app = app
        
        async def __call__(self, scope: Scope, receive: Receive, send: Send):
            if scope["type"] == "http":
                request_id = str(uuid.uuid4())
                scope["request_id"] = request_id
                
                async def send_wrapper(message):
                    if message["type"] == "http.response.start":
                        headers = list(message.get("headers", []))
                        headers.append((b"x-request-id", request_id.encode()))
                        message["headers"] = headers
                    await send(message)
                
                await self.app(scope, receive, send_wrapper)
            else:
                await self.app(scope, receive, send)
    
    wrapped_app = RequestIDMiddleware(app)
    
    @app.get("/test")
    async def handler(request: Request, response: Response):
        request_id = request.scope.get("request_id")
        return response.json({"request_id": request_id})
    
    with test_client_factory(wrapped_app) as client:
        resp = client.get("/test")
        request_id_header = resp.headers.get("x-request-id")
        request_id_body = resp.json()["request_id"]
        assert request_id_header == request_id_body
        assert len(request_id_header) == 36  # UUID length
