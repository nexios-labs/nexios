import asyncio

from sanic import Sanic, response

app = Sanic("sanic_app")


@app.get("/")
async def root(request):
    return response.json({"message": "Hello World"})


@app.get("/json")
async def json_endpoint(request):
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
async def echo(request):
    return response.json(request.json)


@app.get("/delay/<seconds:float>")
async def delay(request, seconds):
    await asyncio.sleep(seconds)
    return response.json({"message": f"Delayed for {seconds} seconds"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8002, access_log=False, workers=4)
