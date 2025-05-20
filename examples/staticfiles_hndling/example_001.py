from nexios import NexiosApp
from nexios.static import StaticFilesHandler
from nexios.routing import Routes

app = NexiosApp()

static_handler = StaticFilesHandler(directory="static", url_prefix="/static/")

app.add_route(Routes("/static/{path:path}", static_handler))


@app.get("/download")
async def download_file(req, res):
    return res.file("file.txt", content_disposition_type="attachment")
