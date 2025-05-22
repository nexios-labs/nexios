from nexios import NexiosApp

app = NexiosApp()


@app.route("/")
def index(req, res):
    return {"message": "Hello, World!"}


@app.route("/list")
def list_items(req, res):
    return ["item1", "item2", "item3"]


@app.route("/string")
def string(req, res):
    return "Hello, World!"
