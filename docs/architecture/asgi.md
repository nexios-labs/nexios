
# ⚡ Understanding ASGI 

Whether you’re using Nexios, FastAPI, or Starlette, you’re relying on ASGI — the **Asynchronous Server Gateway Interface**. It’s the async evolution of WSGI, designed for modern Python apps that need **speed**, **concurrency**, and **WebSocket support**.

---

## 🔥 ASGI vs WSGI — Why the Change?

| Feature          | WSGI                  | ASGI                                |
| ---------------- | --------------------- | ----------------------------------- |
| Concurrency      | Synchronous only 🐌   | Asynchronous + concurrent ⚡         |
| WebSockets       | ❌ Not supported       | ✅ Native support                    |
| Background tasks | Tricky to manage      | Easy with `asyncio.create_task()`   |
| Ideal for        | Simple APIs, websites | Real-time apps, APIs, async systems |

### TL;DR:

**WSGI** = great for blogs, admin panels, or simple APIs.
**ASGI** = ideal for real-time dashboards, video calls, live chats, and fast APIs. That's why Nexios is async-first.

---

## 🧪 What Is ASGI Really?

At its core, ASGI is just a **specification**: a way your Python app can interact with an async server like [Uvicorn](https://www.uvicorn.org/) or [Daphne](https://github.com/django/daphne). It defines how the app should:

* Accept **connections** (`scope`)
* Receive **messages** (`receive`)
* Send **responses** or **events** (`send`)

---

## 🧩 The Core ASGI App (No Framework)

Here’s a raw ASGI app, no fluff:

```python
# app.py
async def app(scope, receive, send):
    if scope["type"] != "http":
        return

    await receive()  # Wait for incoming request

    await send({
        "type": "http.response.start",
        "status": 200,
        "headers": [
            [b"content-type", b"text/plain"]
        ]
    })

    await send({
        "type": "http.response.body",
        "body": b"Hello from raw ASGI!"
    })
```

Start it with:

```bash
uvicorn app:app --reload
```

Boom — You’ve got a web server, no Django, no Flask, just you and ASGI.

---

## 🚀 ASGI Frameworks in Real Life

You *could* build a full app with raw ASGI... but you'd lose your sanity. That’s why we have ASGI frameworks:

| Framework     | Description                                                                                             | Link                                                       |
| ------------- | ------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| **Nexios**    | Lightweight ASGI framework built for speed and freedom. Supports JWT, auth layers, custom routing, etc. | [Nexios on GitHub](https://github.com/nexios-labs/Nexios)  |
| **FastAPI**   | Declarative, powerful API builder with Pydantic and async built-in. Great for REST APIs.                | [fastapi.tiangolo.com](https://fastapi.tiangolo.com)       |
| **Starlette** | FastAPI’s foundation — gives you routing, middlewares, and tools for building async web apps.           | [starlette.io](https://www.starlette.io)                   |
| **Quart**     | Flask-compatible but async. If you're coming from Flask and want async, this helps.                     | [pgjones.gitlab.io/quart](https://pgjones.gitlab.io/quart) |

🧠 **Note:** Nexios gives you full freedom without being too magic-heavy like FastAPI. You control routing, responses, middlewares — just like Express.js but async-native.

---

## 🧠 How Uvicorn and Granian Fit In

* **[Uvicorn](https://www.uvicorn.org/)**: ASGI web server based on `uvloop`. Lightweight, fast, and compatible with most frameworks. Runs your app.

* **[Granian](https://github.com/emmett-framework/granian)**: A newer Rust-powered ASGI server. Slightly faster than Uvicorn on benchmarks, with multi-threading options.

🔧 Nexios supports both — Uvicorn for default setups, Granian for performance-heavy deployments.

---

## ✨ A Bit Smarter Example

Let’s add some path-based routing manually:

```python
async def app(scope, receive, send):
    if scope["type"] != "http":
        return

    await receive()

    path = scope["path"]
    content = {
        "/": b"🏠 Welcome Home",
        "/about": b"📘 About ASGI",
    }.get(path, b"❓ Page Not Found")

    await send({
        "type": "http.response.start",
        "status": 200,
        "headers": [[b"content-type", b"text/plain"]]
    })
    await send({
        "type": "http.response.body",
        "body": content
    })
```

---

## 💡 Why Nexios Chooses ASGI

* It's **async-native**, meaning Nexios can handle thousands of concurrent requests without threads.
* Real-time apps (video calls, WebSocket chat, etc.) become first-class citizens.
* Easier performance tuning with Uvicorn or Granian.
* No GIL-bound threadpool hacks — true Pythonic concurrency.

