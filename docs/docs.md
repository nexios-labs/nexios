---
title : Nexios
description : A fast and simple framework for building APIs with Python
icon : 😁
icon_color : #ff7f00
---

# Happy , You made it !

a lightweight, high-performance Python web framework built for speed, simplicity, and flexibility. Inspired by the ease of Express.js and powered by async capabilities .


---
Nexios allows you to create scalable applications quickly without compromising on performance. Whether you're building a microservice or a full-stack solution, Nexios gives you the tools to ship clean, efficient code with ease.

## Simple Example

```python {3}
from nexios import Nexios

app = Nexios()

@app.get("/")
async def home(request: Request, response: Response):
    """Simple endpoint to verify the app is running"""
    return {"message": "Hello, World!"}


```

That's it! You can create API endpoints with just a few lines of code. 🚀



## Where To Start 😕

Getting started with Nexios is quick and simple. Whether you’re building your first web app or integrating Nexios into an existing project, you’ll find it easy to hit the ground running. Here’s how you can get started:

---

### Installation Guide ⬇️

First things first, you need to install Nexios. It’s as easy as running the following command:

::: tip
Always install dependencies in a virtual environment for project isolation.
:::

```bash
pip install nexios
```

This will install the latest version of Nexios and all its dependencies. You’re now ready to start building! For more clarity on the installation process, visit our detailed [installation guide](/docs/getting-started/installation-guide/).

---

### Create Your First Application 🚀

Now that you have Nexios installed, it's time to create your first application. Here's how you can do that:

```bash
nexios new myproject
cd myproject
```

This will create a new directory called `myproject` and install the necessary dependencies. You can then start building your application using the command `nexios run` in your terminal.

### Run Your Application

```bash
nexios run
```
To run your application, you can use the command `nexios run` in your terminal. This will start the development server and make your application available at http://localhost:4000.

That's it! You're all set to start building your web app with Nexios. Have fun!



## Features

- Fast and simple framework for building APIs with Python 🚀

-  Auto OpenAPI documentation 📃

-  Authentication  🔒

-  CORS support 🚧

-  Async support 💞

- Asgi Compatiblity 🧑‍💻

- Inbuilt Cli Tools 🛠  ️


## Who is Nexios For?

- **Beginners**: If you're new to web development, Nexios is a great place to start. It's easy to use and has a clean and simple API that's easy to understand.

- **Professionals**: If you're looking for a fast and efficient framework to build APIs, Nexios is a great choice. It's easy to use and has a clean and simple API that's easy to understand.

- **Enterprise**: If you're looking for a fast and efficient framework to build APIs, Nexios is a great choice. It's easy to use and has a clean and simple API that's easy to understand.


## Why Use Nexios?

- **Simple**: Nexios is easy to use and has a clean and simple API that's easy to understand.

- **Fast**: Nexios is fast and efficient, making it perfect for building APIs.

- **Flexible**: Nexios is flexible and can be customized to meet your specific needs.

