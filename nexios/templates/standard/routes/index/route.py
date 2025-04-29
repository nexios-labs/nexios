from nexios.http import Request, Response
from nexios.routing import Router

index_router = Router()


@index_router.get("/")
async def index(request: Request, response: Response):
    """
    Index route for the application.
    """
    return response.json({"message": "Welcome to the Nexios application!"})
