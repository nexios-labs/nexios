# Integrating Tortoise ORM with Nexios

## Introduction
Tortoise ORM is an asynchronous Object-Relational Mapping (ORM) library for Python, designed for high performance and compatibility with asyncio-based applications. Nexios, being a flexible Python framework, can integrate seamlessly with Tortoise ORM to provide database interaction capabilities.

## Installation
To use Tortoise ORM with Nexios, install the required dependencies:

```bash
pip install tortoise-orm aiosqlite
```

> **Note:** Replace `aiosqlite` with your preferred database driver (e.g., `asyncpg` for PostgreSQL or `aiomysql` for MySQL).

## Setting Up Tortoise ORM in Nexios
Tortoise ORM requires configuration before it can interact with databases. Below is how you configure it within a Nexios application.

### Define the Database Configuration
Create a `config.py` file to store database settings:

```python
DATABASE_CONFIG = {
    "connections": {
        "default": "sqlite://db.sqlite3"  # Change this to match your DB
    },
    "apps": {
        "models": {
            "models": ["app.models"],  # Import your models
            "default_connection": "default",
        }
    }
}
```

### Initialize Tortoise ORM in Nexios
Modify your application’s main file to initialize Tortoise ORM when Nexios starts:

```python
from tortoise import Tortoise
from nexios import get_application
from config import DATABASE_CONFIG

app = get_application()

async def init_db():
    await Tortoise.init(config=DATABASE_CONFIG)
    await Tortoise.generate_schemas()  # Generates tables if they don't exist

@app.on_startup()
async def startup():
    await init_db()

@app.on_shutdown()
async def shutdown():
    await Tortoise.close_connections()
```

## Defining Models
In Tortoise ORM, models define how database tables should be structured. Create a `models.py` file and define your models:

```python
from tortoise.models import Model
from tortoise import fields

class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    email = fields.CharField(max_length=100, unique=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return self.username
```

## Performing Database Operations
### Creating a New Record
To add a new user:

```python
from app.models import User

async def create_user():
    user = await User.create(username="dunamis", email="dunamis@example.com")
    print(user.id)
```

### Querying Data
Fetching all users:

```python
users = await User.all()
for user in users:
    print(user.username)
```

Fetching a specific user:

```python
user = await User.get(username="dunamis")
print(user.email)
```

### Updating Data

```python
user = await User.get(username="dunamis")
user.email = "newemail@example.com"
await user.save()
```

### Deleting Data

```python
user = await User.get(username="dunamis")
await user.delete()
```

## Using Relationships
Tortoise ORM supports relationships between models. Example with a `Post` model related to `User`:

```python
class Post(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=200)
    content = fields.TextField()
    user = fields.ForeignKeyField("models.User", related_name="posts")
```

Fetching related posts:

```python
user = await User.get(username="dunamis").prefetch_related("posts")
for post in user.posts:
    print(post.title)
```


