from nexios import NexiosApp
from nexios.exceptions import HTTPException


class CustomException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Custom Exception")


app = NexiosApp()


@app.get("/test-custom-exception")
async def test_route(req, res):
    raise CustomException()


async def handle_custom_exception(req, res, exc):
    return res.json({"error": str(exc)})


app.add_exception_handler(CustomException, handle_custom_exception)
