from nexios import get_application, NexiosApp
from nexios.routing import Routes, Router
from nexios.views import APIView
import pytest
from nexios.http import Request, Response
from nexios.testing import Client

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
