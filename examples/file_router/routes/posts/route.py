from nexios.file_router import mark_as_route
from nexios.http import Request, Response


@mark_as_route(
    path="/homelander",
    methods=["post", "delete", "patch", "put"],
    summary="Home Lander",
)
async def get(req: Request, res: Response):
    pass
