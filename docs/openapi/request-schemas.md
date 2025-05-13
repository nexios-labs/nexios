# Request Models

Request models in Nexios are built using Pydantic's BaseModel to provide robust request validation, automatic OpenAPI documentation, and type-safe request handling. This documentation covers how to define and use request models in your API endpoints.

## Defining Request Models
Request models are standard Pydantic models that define the expected structure of incoming request data.
To define a request model in your API endpoint, you can use the `request_model` argument in the `@app.get` or `@app.post` decorators. Here's an example:


```python
from nexios import NexiosApp
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age : int

app = NexiosApp()

@app.post("/users", request_model=User)
async def get_users(req, res):
    ...
```


<img src="./request-body.png">

For more information on how to use request models, please refer to the [Pydantic documentation](https://pydantic-docs.helpmanual.io/)