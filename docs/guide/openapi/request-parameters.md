# Request Parameters

Request parameters are query parameters or path parameters that are used to filter or identify specific resources it also includes headers .

## Path Parameters

By default Nexios automatically detects path parameters from your route path and documents them in OpenAPI. For example:

```python
from nexios import NexiosApp

app = NexiosApp()

@app.get("/users/{user_id}")
async def get_user(req, res):
    user_id = req.path_params.user_id
    ...
```

<img src="./path-params.png">


## Query Parameters

Nexios Does not automatically detect query parameters, but you can add them using the `parameters` argument:

```python
from nexios import NexiosApp
from nexios.openapi.models import Query
app = NexiosApp()

@app.get("/users", parameters=[Query(name="user_id"), Query(name="user_type")])
async def get_user(req, res):
    user_id = req.query_params.user_id
    user_type = req.query_params.user_type
    ...
```
<img src="./query-params.png">


## Headers

Nexios Does not automatically detect headers, but you can add them using the `parameters` argument:

```python
from nexios import NexiosApp
from nexios.openapi.models import Header
app = NexiosApp()

@app.get("/users", parameters=[Header(name="token")])
async def get_user(req, res):
    token = req.headers.get("token")
    ...
```
<img src="./headers.png"> 

_more docs to come_