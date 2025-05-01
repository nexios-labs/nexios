from nexios import get_application

app = get_application()


@app.get("/api/items")
async def get_items(req, res):
    items = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]
    return res.json(items)


@app.get("/api/items/{item_id:int}")
async def get_item(req, res):
    item_id = req.path_params.item_id
    return res.json({"id": item_id, "name": f"Item {item_id}"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=5000, reload=True)
