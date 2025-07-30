import pytest

from nexios import get_application
from nexios.http import Request, Response
from nexios.testing import Client


@pytest.fixture
async def test_client():
    app = get_application()
    async with Client(app) as client:
        yield client, app


async def test_request_properties(test_client):
    client, app = test_client

    @app.get("/test-properties")
    async def handler(req: Request, res: Response):
        return res.json(
            {
                "method": req.method,
                "path": req.path,
                "client_host": req.client.host if req.client else None,
                "client_port": req.client.port if req.client else None,
            }
        )

    response = await client.get("/test-properties")
    data = response.json()
    assert data["method"] == "GET"
    assert data["path"] == "/test-properties"
    assert data["client_host"] is not None
    assert data["client_port"] is not None


async def test_query_params(test_client):
    client, app = test_client

    @app.get("/test-query")
    async def handler(req: Request, res: Response):
        return res.json(
            {"name": req.query_params.get("name"), "age": req.query_params.get("age")}
        )

    response = await client.get("/test-query?name=test&age=25")
    data = response.json()
    assert data["name"] == "test"
    assert data["age"] == "25"


async def test_path_params(test_client):
    client, app = test_client

    @app.get("/test-path/{user_id}")
    async def handler(req: Request, res: Response):
        return res.json({"user_id": req.path_params["user_id"]})

    response = await client.get("/test-path/123")
    data = response.json()
    assert data["user_id"] == "123"


async def test_headers(test_client):
    client, app = test_client

    @app.get("/test-headers")
    async def handler(req: Request, res: Response):
        return res.json(
            {
                "content_type": req.headers.get("content-type"),
                "user_agent": req.headers.get("user-agent"),
            }
        )

    response = await client.get(
        "/test-headers",
        headers={"content-type": "application/json", "user-agent": "test-agent"},
    )
    data = response.json()
    assert data["content_type"] == "application/json"
    assert data["user_agent"] == "test-agent"


async def test_cookies(test_client):
    client, app = test_client

    @app.get("/test-cookies")
    async def handler(req: Request, res: Response):
        return res.json(
            {"session": req.cookies.get("session"), "user": req.cookies.get("user")}
        )

    response = await client.get(
        "/test-cookies", cookies={"session": "abc123", "user": "test"}
    )
    data = response.json()
    assert data["session"] == "abc123"
    assert data["user"] == "test"


async def test_state(test_client):
    client, app = test_client

    @app.get("/test-state")
    async def handler(req: Request, res: Response):
        req.state.test_value = "state_value"
        return res.text(req.state.test_value)

    response = await client.get("/test-state")
    assert response.text == "state_value"


async def test_json_body(test_client):
    client, app = test_client

    @app.post("/test-json-body")
    async def handler(req: Request, res: Response):
        data = await req.json
        return res.json(data)

    test_data = {"key": "value"}
    response = await client.post("/test-json-body", json=test_data)
    assert response.json() == test_data


async def test_text_body(test_client):
    client, app = test_client

    @app.post("/test-text-body")
    async def handler(req: Request, res: Response):
        text = await req.text
        return res.text(text)

    test_text = "plain text body"
    response = await client.post("/test-text-body", content=test_text)
    assert response.text == test_text


async def test_form_data(test_client):
    client, app = test_client

    @app.post("/test-form-data")
    async def handler(req: Request, res: Response):
        form_data = await req.form_data
        return res.json(
            {"field1": form_data.get("field1"), "field2": form_data.get("field2")}
        )

    form_data = {"field1": "value1", "field2": "value2"}
    response = await client.post("/test-form-data", data=form_data)
    data = response.json()
    assert data["field1"] == "value1"
    assert data["field2"] == "value2"


async def test_user_property(test_client):
    client, app = test_client

    @app.get("/test-user")
    async def handler(req: Request, res: Response):
        req.user = "testuser"
        return res.text(req.user)

    response = await client.get("/test-user")
    assert response.text == "testuser"


async def test_valid_method(test_client):
    client, app = test_client

    @app.route("/test-valid", methods=["GET", "POST"])
    async def handler(req: Request, res: Response):
        return res.text(str(req.valid()))

    # Test valid method
    response = await client.get("/test-valid")
    assert response.text == "True"

    # Test invalid method
    response = await client.delete("/test-valid")
    assert response.status_code == 405


async def test_form_urlencoded(test_client):
    client, app = test_client

    @app.post("/test-form-urlencoded")
    async def handler(req: Request, res: Response):
        form_data = await req.form
        return res.json({"form": dict(form_data)})

    response = await client.post(
        "/test-form-urlencoded",
        data={"username": "testuser", "password": "testpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    data = response.json()
    assert data["form"]["username"] == "testuser"
    assert data["form"]["password"] == "testpass"


async def test_form_multipart(test_client):
    client, app = test_client

    @app.post("/test-form-multipart")
    async def handler(req: Request, res: Response):
        form_data = await req.form
        files = await req.files
        return res.json({
            "form": dict(form_data),
            "files": {k: v.filename for k, v in files.items()}
        })

    # Create a sample file to upload
    files = {"file": ("test.txt", b"test content", "text/plain")}
    
    response = await client.post(
        "/test-form-multipart",
        data={"field1": "value1"},
        files=files,
    )
    data = response.json()
    assert data["form"]["field1"] == "value1"
    assert data["files"]["file"] == "test.txt"


async def test_form_empty(test_client):
    client, app = test_client

    @app.post("/test-form-empty")
    async def handler(req: Request, res: Response):
        form_data = await req.form
        return res.json({"form": dict(form_data)})

    response = await client.post(
        "/test-form-empty",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    data = response.json()
    assert data["form"] == {}
