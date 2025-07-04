from nexios import NexiosApp
from nexios.templating import render,TemplateEngine

app = NexiosApp()
engine = TemplateEngine()
engine.setup_environment()

@app.get("/")
async def home(request, response):
    return await render("home.html", {"title": "Welcome"})

if __name__ == "__main__":
    app.run()