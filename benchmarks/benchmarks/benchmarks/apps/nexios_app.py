import asyncio

import uvicorn

from nexios import NexiosApp
from nexios.http import Request, Response

app = NexiosApp()


@app.get("/")
async def root(request: Request, response: Response):
    return response.json({"message": "Hello World"})


@app.get("/json")
async def json_endpoint(request: Request, response: Response):
    return response.json(
        {
            "string": "Hello World",
            "number": 42,
            "boolean": True,
            "array": [1, 2, 3],
            "object": {"key": "value"},
        }
    )


@app.post("/echo")
async def echo(request: Request, response: Response):
    data = await request.json
    return response.json(data)


@app.get("/delay/{seconds:float}")
async def delay(request: Request, response: Response, seconds: float):
    await asyncio.sleep(int(seconds))
    return response.json({"message": f"Delayed for {seconds} seconds"})


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8005)
