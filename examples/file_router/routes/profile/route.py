from typing import Callable

from nexios.file_router.html import render
from nexios.http import Request, Response


@render("temps.html")
async def get(req: Request, res: Response):
    return {}


async def post_middleware(req: Request, res: Response, next: Callable):
    print(f"Received request: {req.method} {req.path}")
    await next()
    # raise Exception("AuthenticationRequired")


async def post(req: Request, res: Response):
    res.json({"ok": True})
