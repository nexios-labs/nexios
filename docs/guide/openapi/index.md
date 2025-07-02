# OpenApi

Nexios provides an easy way to document your API using OpenAPI.

---
By default, Nexios automatically generates OpenAPI documentation for all your routes. The documentation is accessible at `/docs` and the raw OpenAPI specification is available at `/openapi.json`

In this guide, we will walk you through the process of generating a more customized OpenAPI documentation.

---

##  Basic Setup

```python
from nexios import NexiosApp
app = NexiosApp()

@app.get("/", summary="Hello World")
async def get_root(req, res):
    return res.json({"message": "Hello World"})
```

<img src="./basic-config.png">


## Adding Description

```python
from nexios import NexiosApp
app = NexiosApp()

@app.get("/", summary="Hello World", description="This is a description")
async def get_root(req, res):
    return res.json({"message": "Hello World"})
```


<img src="./description.png">