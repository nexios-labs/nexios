from nexios.http import Request, Response
from nexios.plugins.file_router.html import render


@render()
async def get(req: Request, res: Response):
    return {
        "todos": [
            {
                "id": 1,
                "title": "Implement File Router Plugin",
                "completed": True,
            },
            {
                "id": 2,
                "title": "Implement HTML Router Router",
                "completed": False,
            },
        ]
    }
