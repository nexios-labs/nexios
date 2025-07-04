# Day 1: Welcome to Nexios - Building Your First Async Web App

Welcome to the first day of your 28-day journey to mastering Nexios! Today, we're starting with the absolute basics to build a solid foundation. By the end of this lesson, you'll have your first Nexios application up and running.

## What You'll Learn Today
- **What Nexios is** and why it's a great choice for modern web development.
- **Core features** that make Nexios powerful and efficient.
- How to **set up your development environment** for a Nexios project.
- How to create and run your very **first Nexios application**.
- The basic **project structure** of a Nexios app.

---

## 1. What is Nexios?

Nexios is a modern, high-performance Python web framework for building asynchronous APIs and web applications. If you're familiar with Flask or FastAPI, you'll find some similarities, but Nexios is built from the ground up to be async-first, leveraging modern Python features to offer incredible speed and a developer-friendly experience.

### Why Choose Nexios?
- **Speed:** Built on top of Starlette and Pydantic, Nexios is one of the fastest Python frameworks available.
- **Async First:** It's designed for concurrency, allowing you to handle many connections at once without blocking.
- **Intuitive:** The API is designed to be simple and expressive, so you can write clean, readable code.
- **Type-Safe:** Full support for Python type hints helps you catch errors early and build robust applications.

## 2. Setting Up Your Development Environment

Let's get your computer ready for Nexios development.

### Prerequisites
- **Python 3.9 or higher:** Nexios uses modern Python features. You can check your version with `python --version`.
- **pip:** The standard Python package manager. It comes with modern Python installations.
- **A code editor:** We recommend [VS Code](https://code.visualstudio.com/) with the official Python extension.

### Installation Steps

#### Step 1: Create a Project Directory
First, let's create a folder for our new project.
```bash
mkdir my-nexios-app
cd my-nexios-app
```

#### Step 2: Set Up a Virtual Environment
A virtual environment is a self-contained directory that holds all the Python packages for a specific project. This is a crucial best practice to avoid conflicts between projects.

::: code-group
```bash [Linux/macOS]
# Create the virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate
```

```bash [Windows]
# Create the virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate
```
:::

> **Pro-Tip:** Once activated, you'll see `(venv)` at the beginning of your terminal prompt. This shows that your virtual environment is active.

#### Step 3: Install Nexios and Uvicorn
Now, let's install Nexios and an ASGI server called Uvicorn to run our app.

```bash
pip install "nexios[standard]"
```

> **What is Uvicorn?**
> Uvicorn is a lightning-fast ASGI (Asynchronous Server Gateway Interface) server. It's the component that actually receives HTTP requests and passes them to our Nexios application to be processed.

---

## 3. Your First Nexios Application: "Hello, World!"

Time to write some code!

### Basic Project Structure
For now, our project structure is very simple:
```
my-nexios-app/
├── venv/       # Our virtual environment
└── app.py      # Our application code will go here
```

### Create `app.py`
Create a file named `app.py` in your project directory and add the following code:

```python
# 1. Import the necessary components from Nexios
from nexios import NexiosApp
from nexios.http import Request, Response

# 2. Create an instance of the NexiosApp
app = NexiosApp()

# 3. Define a "route" using a decorator
@app.get("/")
async def hello(request: Request, response: Response):
    """
    This is our main endpoint. It will handle GET requests to the root URL ("/").
    """
    # 4. Return a JSON response
    return response.json({
        "message": "Hello, World!",
        "framework": "Nexios"
    })

# 5. Run the application server
if __name__ == "__main__":
    import uvicorn
    # This will run the app on http://127.0.0.1:5000
    # reload=True will automatically restart the server when you save the file
    uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True)
```

> **Understanding `if __name__ == "__main__"`**
> This is a standard Python construct. It ensures that the `uvicorn.run()` command is only executed when you run the script directly (`python app.py`), not when it's imported as a module into another script.

### Run Your Application
Save the `app.py` file and run it from your terminal:
```bash
python app.py
```

> **Tip:** You can also run Nexios projects using the CLI:
> ```bash
> nexios run
> ```
> The CLI will use `nexios.config.py` if present, or you can pass options directly as CLI arguments (e.g., `nexios run --app-path app:app --port 5000`). CLI args always override config file values. See the [CLI Guide](../../guide/cli.md) and [Configuration Guide](../../guide/configuration.md) for more details.

You should see output similar to this:
```
INFO:     Uvicorn running on http://127.0.0.1:5000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345]
INFO:     Started server process [12347]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### See Your App in Action!
Open your web browser and navigate to `http://127.0.0.1:5000`. You should see the JSON response:
```json
{
  "message": "Hello, World!",
  "framework": "Nexios"
}
```

Congratulations, you've just built and run your first Nexios web application!

---

## 4. Working with Different Responses

Nexios makes it easy to return different types of web content. Here are a few examples. You can add these to your `app.py` to try them out.

::: code-group
```python [JSON Response]
# Add this to your app.py
@app.get("/api/data")
async def json_handler(req: Request, res: Response):
    return res.json({"status": "success", "data": [1, 2, 3]})
```

```python [Plain Text Response]
# Add this to your app.py
@app.get("/text")
async def text_handler(req: Request, res: Response):
    return res.text("This is a simple text response.")
```

```python [HTML Response]
# Add this to your app.py
@app.get("/html")
async def html_handler(req: Request, res: Response):
    return res.html("<h1>This is an HTML Response</h1>")
```
:::

After adding these, save the file. The `reload=True` option in `uvicorn.run()` will automatically restart your server. You can now visit `/api/data`, `/text`, and `/html` in your browser to see the results.

## 5. Homework and Practice

Time to put your new knowledge to the test!

### Your Task
Your assignment is to build a simple "About Me" API.

1.  **Create a new Nexios application** (or modify the existing `app.py`).
2.  **Add an endpoint at `/about`** that returns a JSON object with information about you (e.g., name, city, hobbies).
3.  **Add another endpoint at `/status`** that returns a plain text response, like "I am learning Nexios!".
4.  **Bonus:** Create a third endpoint that returns a simple HTML page with a heading and a paragraph.
5.  **Test your endpoints** by visiting them in your browser or using a tool like [Postman](https://www.postman.com/) or the VS Code "REST Client" extension.

Feel free to experiment! The more you code, the more comfortable you'll become.

---

## Additional Resources
- [Official Nexios Documentation](https://nexios.dev)
- [Python's `asyncio` Documentation](https://docs.python.org/3/library/asyncio.html)
- [A great visualizer for async/await in Python](https://pythontutor.com/visualize.html)

## Next Steps

Tomorrow, we'll dive deeper into one of the most important parts of any web framework: **Routing**.

➡️ **[Continue to Day 2: First Application & Routing](../day02/)**
