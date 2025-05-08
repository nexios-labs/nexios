# Routers and Sub-Applications

Nexios provides a powerful routing system that allows you to create modular and nested routing structures. Here's an example of how you can use routers and sub-applications in your application


## Creating a Router and Mounting it to the Main Application
```python
from nexios import NexiosApp
from nexios.routing import Router

app = NexiosApp()

v1_router = Router(prefix="/v1")

@v1_router.get("/users")
async def list_users(req, res):
    return res.json({"message": "List of users"})

@v1_router.get("/users/{user_id}")
async def get_user(req, res, user_id):
    return res.json({"user_id": user_id})

app.mount_router(v1_router)

```
::: tip 💡 Tip
when mounting tthe router you can pass in an extra prefix argument that overide the prefix of the router

```python
app.mount_router(v1_router, "/api/v1")
```

:::
This example creates a router with two routes, one for listing users and another for getting a specific user. The router is then mounted to the main application using the `mount_router` method.

This matches `/v1/users` and `/v1/users/{user_id}`

::: warning ⚠️ Bug Alert
Ensure to use `mount_router` after all routes have been defined.
:::

## What is Router?

A Router is a container for routes and sub-applications. It allows you to create a modular and nested routing structure in your application.

Even the `NexiosApp` is also a router, which means you can mount sub-applications to it. and also mount another NexiosApp to it

```python

app = NexiosApp()

app2 = NexiosApp()

app.mount_router(app2, "/api/v1")


```

::: warning ⚠️ Bug Alert
Ensure all mounted sub application or sub-routers have unique prefixes
:::

Nexios Also support nested routers

```python

app = NexiosApp()

v1_router = Router(prefix="/v1")
user_router = Router(prefix="/v2")

v1_router.mount_router(user_router)
app.mount_router(v1_router)
```

The `Router` class also have similar routing methods as `NexiosApp` class