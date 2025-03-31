from nexios.http.request import Request
from nexios.http import Response


async def get(req:Request, res :Response):
    
    return res.json("Hello world")