import uvicorn
from fastapi import FastAPI, Request

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/json")
async def json_endpoint():
    return {
        "string": "Hello World",
        "number": 42,
        "boolean": True,
        "array": [1, 2, 3],
        "object": {"key": "value"},
    }


@app.post("/echo")
async def echo(request: Request):
    data = await request.json()
    return data


@app.get("/delay/{seconds}")
async def delay(seconds: float):
    import asyncio

    await asyncio.sleep(seconds)
    return {"message": f"Delayed for {seconds} seconds"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")
