import asyncio

import hypercorn.asyncio
import hypercorn.config
from quart import Quart, request

app = Quart(__name__)


@app.route("/")
async def root():
    return {"message": "Hello World"}


@app.route("/json")
async def json_endpoint():
    return {
        "string": "Hello World",
        "number": 42,
        "boolean": True,
        "array": [1, 2, 3],
        "object": {"key": "value"},
    }


@app.route("/echo", methods=["POST"])
async def echo():
    data = await request.get_json()
    return data


@app.route("/delay/<float:seconds>")
async def delay(seconds):
    await asyncio.sleep(seconds)
    return {"message": f"Delayed for {seconds} seconds"}


if __name__ == "__main__":
    config = hypercorn.config.Config()
    config.bind = ["127.0.0.1:8003"]
    config.worker_class = "asyncio"
    config.workers = 4
    config.use_reloader = False
    asyncio.run(hypercorn.asyncio.serve(app, config))
