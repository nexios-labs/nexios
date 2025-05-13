# Response Models

Nexios depends Pydantic for generating OpenAPI spec files. You can use Pydantic models as response models.

By default Nexios Adds Only A  example response with status code 200. You can add more response models by using the `responses` argument in the `@app.get` decorator.

## Modifying the default Response Model

```python
from nexios import NexiosApp
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age : int

app = NexiosApp()

@app.get("/users", responses=User)
async def get_users(req, res):
    ...
```

<img src="./response.png">

## Adding Multiple Response Models

You can add multiple response modeels for different status codes.
This Can be done by passing a dictionary with status codes as keys and response models as values.
```python
from nexios import NexiosApp
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age : int

class Error(BaseModel):
    message: str

app = NexiosApp()

@app.get("/users", responses={200: User, 404: Error})
async def get_users(req, res):
    ...
```
<img src="./multi-response.png">

## Using `List` as Response Model

You can use `List` as response model to return a list of items.

```python
from nexios import NexiosApp
from pydantic import BaseModel
from typing import List
class User(BaseModel):
    name: str
    age : int

app = NexiosApp()
@app.get("/users", responses={200: List[User]})
async def get_users(req, res):
    ...
``` 

<img src="./response-list.png">