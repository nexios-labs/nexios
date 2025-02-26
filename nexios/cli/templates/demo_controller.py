from nexios.http import Request,Response
async def index(req :Request, res :Response):
    return res.json({
        "nexios" : "Welcome to nexios"
    })
