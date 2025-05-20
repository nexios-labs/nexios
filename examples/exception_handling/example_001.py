from nexios import NexiosApp
from nexios.exceptions import HTTPException

app = NexiosApp()


@app.route("/error")
async def error_handler(req, res):
    raise HTTPException(status_code=400, detail="error occurred")


@app.add_exception_handler(HTTPException)
async def http_error_handler(req, res, exc):
    return await res.json({"error": exc.detail}, status_code=exc.status_code)


# app.add_exception_handler(ValueError, handle_value_error)
# app.add_exception_handler(404, handle_not_found)
