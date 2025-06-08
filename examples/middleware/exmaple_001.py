from nexios import NexiosApp
from nexios.middleware.base import BaseMiddleware


async def logging_middleware(req, res, cnext):
    print(f"Request: {req.method} {req.url}")
    response = await cnext()
    print(f"Response: {res.status_code} {response.body}")
    return response


class LoggingMiddleware(BaseMiddleware):
    async def process_request(self, req, res, cnext):
        print(f"Request: {req.method} {req.url}")
        response = await cnext()
        print(f"Response: {res.status_code} {response.body}")
        return response


app = NexiosApp()
app.add_middleware(LoggingMiddleware())


@app.get("/")
async def index(req, res):
    return res.text("Hello, World!")
