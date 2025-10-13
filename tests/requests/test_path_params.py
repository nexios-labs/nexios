"""
Tests for request path parameters
"""
from typing import Callable
import pytest
from nexios import NexiosApp
from nexios.http import Request, Response
from nexios.testclient import TestClient


# ========== Path Parameters Tests ==========

def test_request_path_params_single(test_client_factory: Callable[[NexiosApp], TestClient]):
    """Test single path parameter"""
    app = NexiosApp()
    
    @app.get("/users/{user_id}")
    async def handler(request: Request, response: Response):
        user_id = request.path_params.get("user_id")
        return response.json({"user_id": user_id})
    
    with test_client_factory(app) as client:
        resp = client.get("/users/123")
        assert resp.status_code == 200
        assert resp.json()["user_id"] == "123"


def test_request_path_params_multiple(test_client_factory: Callable[[NexiosApp], TestClient]):
    """Test multiple path parameters"""
    app = NexiosApp()
    
    @app.get("/users/{user_id}/posts/{post_id}")
    async def handler(request: Request, response: Response):
        user_id = request.path_params.get("user_id")
        post_id = request.path_params.get("post_id")
        return response.json({"user_id": user_id, "post_id": post_id})
    
    with test_client_factory(app) as client:
        resp = client.get("/users/456/posts/789")
        data = resp.json()
        assert data["user_id"] == "456"
        assert data["post_id"] == "789"


def test_request_path_params_dict_access(test_client_factory: Callable[[NexiosApp], TestClient]):
    """Test accessing path params as dictionary"""
    app = NexiosApp()
    
    @app.get("/items/{item_id}")
    async def handler(request: Request, response: Response):
        all_params = dict(request.path_params)
        return response.json(all_params)
    
    with test_client_factory(app) as client:
        resp = client.get("/items/abc123")
        data = resp.json()
        assert data["item_id"] == "abc123"


def test_request_path_params_numeric(test_client_factory: Callable[[NexiosApp], TestClient]):
    """Test path parameters with numeric values"""
    app = NexiosApp()
    
    @app.get("/products/{product_id}")
    async def handler(request: Request, response: Response):
        product_id = request.path_params.get("product_id")
        return response.json({
            "product_id": product_id,
            "product_id_int": int(product_id) if product_id else None
        })
    
    with test_client_factory(app) as client:
        resp = client.get("/products/999")
        data = resp.json()
        assert data["product_id"] == "999"
        assert data["product_id_int"] == 999


def test_request_path_params_with_special_chars(test_client_factory: Callable[[NexiosApp], TestClient]):
    """Test path parameters with special characters"""
    app = NexiosApp()
    
    @app.get("/files/{filename}")
    async def handler(request: Request, response: Response):
        filename = request.path_params.get("filename")
        return response.json({"filename": filename})
    
    with test_client_factory(app) as client:
        resp = client.get("/files/document.pdf")
        assert resp.json()["filename"] == "document.pdf"


def test_request_path_params_empty_dict(test_client_factory: Callable[[NexiosApp], TestClient]):
    """Test path params when no parameters defined"""
    app = NexiosApp()
    
    @app.get("/static")
    async def handler(request: Request, response: Response):
        return response.json({
            "has_params": bool(request.path_params),
            "params": dict(request.path_params)
        })
    
    with test_client_factory(app) as client:
        resp = client.get("/static")
        data = resp.json()
        assert data["has_params"] is False
        assert data["params"] == {}


def test_request_path_params_contains(test_client_factory: Callable[[NexiosApp], TestClient]):
    """Test checking if path parameter exists"""
    app = NexiosApp()
    
    @app.get("/api/{version}/users/{user_id}")
    async def handler(request: Request, response: Response):
        has_version = "version" in request.path_params
        has_user_id = "user_id" in request.path_params
        has_missing = "missing" in request.path_params
        return response.json({
            "has_version": has_version,
            "has_user_id": has_user_id,
            "has_missing": has_missing
        })
    
    with test_client_factory(app) as client:
        resp = client.get("/api/v1/users/123")
        data = resp.json()
        assert data["has_version"] is True
        assert data["has_user_id"] is True
        assert data["has_missing"] is False


def test_request_path_params_keys(test_client_factory: Callable[[NexiosApp], TestClient]):
    """Test getting path parameter keys"""
    app = NexiosApp()
    
    @app.get("/org/{org_id}/repo/{repo_id}")
    async def handler(request: Request, response: Response):
        keys = list(request.path_params.keys())
        return response.json({"keys": keys})
    
    with test_client_factory(app) as client:
        resp = client.get("/org/myorg/repo/myrepo")
        keys = resp.json()["keys"]
        assert "org_id" in keys
        assert "repo_id" in keys


def test_request_path_params_values(test_client_factory: Callable[[NexiosApp], TestClient]):
    """Test getting path parameter values"""
    app = NexiosApp()
    
    @app.get("/category/{category}/item/{item}")
    async def handler(request: Request, response: Response):
        values = list(request.path_params.values())
        return response.json({"values": values})
    
    with test_client_factory(app) as client:
        resp = client.get("/category/electronics/item/laptop")
        values = resp.json()["values"]
        assert "electronics" in values
        assert "laptop" in values


def test_request_path_params_uuid_like(test_client_factory: Callable[[NexiosApp], TestClient]):
    """Test path parameters with UUID-like values"""
    app = NexiosApp()
    
    @app.get("/resources/{resource_id}")
    async def handler(request: Request, response: Response):
        resource_id = request.path_params.get("resource_id")
        return response.json({"resource_id": resource_id})
    
    with test_client_factory(app) as client:
        uuid = "550e8400-e29b-41d4-a716-446655440000"
        resp = client.get(f"/resources/{uuid}")
        assert resp.json()["resource_id"] == uuid


def test_request_path_params_with_hyphens(test_client_factory: Callable[[NexiosApp], TestClient]):
    """Test path parameters with hyphens"""
    app = NexiosApp()
    
    @app.get("/posts/{post_slug}")
    async def handler(request: Request, response: Response):
        post_slug = request.path_params.get("post_slug")
        return response.json({"post_slug": post_slug})
    
    with test_client_factory(app) as client:
        resp = client.get("/posts/my-awesome-post")
        assert resp.json()["post_slug"] == "my-awesome-post"


def test_request_path_params_with_underscores(test_client_factory: Callable[[NexiosApp], TestClient]):
    """Test path parameters with underscores"""
    app = NexiosApp()
    
    @app.get("/files/{file_name}")
    async def handler(request: Request, response: Response):
        file_name = request.path_params.get("file_name")
        return response.json({"file_name": file_name})
    
    with test_client_factory(app) as client:
        resp = client.get("/files/my_file_name")
        assert resp.json()["file_name"] == "my_file_name"


def test_request_path_params_nested_resources(test_client_factory: Callable[[NexiosApp], TestClient]):
    """Test path parameters for nested resources"""
    app = NexiosApp()
    
    @app.get("/users/{user_id}/posts/{post_id}/comments/{comment_id}")
    async def handler(request: Request, response: Response):
        return response.json({
            "user_id": request.path_params.get("user_id"),
            "post_id": request.path_params.get("post_id"),
            "comment_id": request.path_params.get("comment_id")
        })
    
    with test_client_factory(app) as client:
        resp = client.get("/users/1/posts/2/comments/3")
        data = resp.json()
        assert data["user_id"] == "1"
        assert data["post_id"] == "2"
        assert data["comment_id"] == "3"


def test_request_path_params_iteration(test_client_factory: Callable[[NexiosApp], TestClient]):
    """Test iterating over path parameters"""
    app = NexiosApp()
    
    @app.get("/a/{param_a}/b/{param_b}")
    async def handler(request: Request, response: Response):
        params_list = [f"{k}={v}" for k, v in request.path_params.items()]
        return response.json({"params": params_list})
    
    with test_client_factory(app) as client:
        resp = client.get("/a/value1/b/value2")
        params = resp.json()["params"]
        assert "param_a=value1" in params
        assert "param_b=value2" in params
