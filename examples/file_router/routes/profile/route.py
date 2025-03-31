from typing import Callable

from nexios.http import Request, Response


async def get(req: Request, res: Response):
    pass


async def post_middleware(req: Request, res: Response, next: Callable):
    print(f"Received request: {req.method} {req.path}")
    await next()
    # raise Exception("AuthenticationRequired")


async def post(req: Request, res: Response):
    res.json({"ok": True})
