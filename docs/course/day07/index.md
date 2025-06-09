# Day 7: Database Integration

Welcome to Day 7! Today we'll learn how to integrate databases with Nexios using SQLAlchemy and other database tools.

## Understanding Database Integration

Database integration in Nexios involves:
- Setting up database connections
- Defining models
- Creating migrations
- Performing CRUD operations
- Handling transactions
- Managing relationships
- Implementing connection pooling

## Database Setup

First, let's set up our database configuration:

```python
from nexios import NexiosApp
from databases import Database
from sqlalchemy import create_engine, MetaData
import os

# Database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./test.db"
)

# Create database instance
database = Database(DATABASE_URL)
metadata = MetaData()

# Create engine for migrations
engine = create_engine(DATABASE_URL)

app = NexiosApp()

# Add database to app state
app.state.database = database

# Database lifecycle management
@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
```

## Defining Models

Let's create some database models using SQLAlchemy:

```python
from sqlalchemy import (
    Table, Column, Integer, String, ForeignKey,
    DateTime, Boolean, Text, Float
)
from datetime import datetime

# Users table
users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String(50), unique=True, index=True),
    Column("email", String(100), unique=True, index=True),
    Column("hashed_password", String(100)),
    Column("is_active", Boolean, default=True),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("updated_at", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
)

# Posts table
posts = Table(
    "posts",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(200)),
    Column("content", Text),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE")),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("updated_at", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
)

# Create all tables
metadata.create_all(engine)
```

## Database Operations

### Basic CRUD Operations

```python
from nexios.http import Request, Response
from typing import Dict, List

# Create
@app.post("/users")
async def create_user(request: Request, response: Response):
    data = await request.json()
    query = users.insert().values(**data)
    user_id = await database.execute(query)
    return response.json({"id": user_id, **data}, status_code=201)

# Read
@app.get("/users/{user_id}")
async def get_user(request: Request, response: Response, user_id: int):
    query = users.select().where(users.c.id == user_id)
    user = await database.fetch_one(query)
    if user:
        return response.json(dict(user))
    return response.json({"error": "User not found"}, status_code=404)

# Update
@app.put("/users/{user_id}")
async def update_user(request: Request, response: Response, user_id: int):
    data = await request.json()
    query = users.update().where(users.c.id == user_id).values(**data)
    await database.execute(query)
    return response.json({"message": "User updated"})

# Delete
@app.delete("/users/{user_id}")
async def delete_user(request: Request, response: Response, user_id: int):
    query = users.delete().where(users.c.id == user_id)
    await database.execute(query)
    return response.json({"message": "User deleted"})
```

### Advanced Queries

```python
# Complex queries with joins
@app.get("/users/{user_id}/posts")
async def get_user_posts(request: Request, response: Response, user_id: int):
    query = (
        posts.select()
        .where(posts.c.user_id == user_id)
        .order_by(posts.c.created_at.desc())
    )
    user_posts = await database.fetch_all(query)
    return response.json([dict(post) for post in user_posts])

# Pagination
@app.get("/posts")
async def list_posts(
    request: Request,
    response: Response,
    page: int = 1,
    per_page: int = 10
):
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Get total count
    count_query = posts.count()
    total = await database.fetch_val(count_query)
    
    # Get paginated posts
    query = (
        posts.select()
        .offset(offset)
        .limit(per_page)
        .order_by(posts.c.created_at.desc())
    )
    items = await database.fetch_all(query)
    
    return response.json({
        "items": [dict(item) for item in items],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page
    })

# Search and filter
@app.get("/search/posts")
async def search_posts(
    request: Request,
    response: Response,
    q: str = None,
    user_id: int = None,
    sort: str = "recent"
):
    query = posts.select()
    
    # Apply search filter
    if q:
        query = query.where(
            posts.c.title.ilike(f"%{q}%") |
            posts.c.content.ilike(f"%{q}%")
        )
    
    # Apply user filter
    if user_id:
        query = query.where(posts.c.user_id == user_id)
    
    # Apply sorting
    if sort == "recent":
        query = query.order_by(posts.c.created_at.desc())
    elif sort == "title":
        query = query.order_by(posts.c.title)
    
    results = await database.fetch_all(query)
    return response.json([dict(result) for result in results])
```

### Transactions

```python
# Transaction example
@app.post("/posts")
async def create_post(request: Request, response: Response):
    async with database.transaction():
        # Create post
        post_data = await request.json()
        post_query = posts.insert().values(**post_data)
        post_id = await database.execute(post_query)
        
        # Update user's post count
        user_query = users.update().where(
            users.c.id == post_data["user_id"]
        ).values(
            post_count=users.c.post_count + 1
        )
        await database.execute(user_query)
        
        return response.json({"id": post_id, **post_data}, status_code=201)
```

## Database Middleware

```python
from typing import Callable
import time

class DatabaseMetricsMiddleware:
    def __init__(self):
        self.query_count = 0
        self.total_time = 0
    
    async def __call__(
        self,
        request: Request,
        response: Response,
        call_next: Callable
    ):
        # Reset metrics for this request
        start_count = database.query_count
        start_time = time.time()
        
        response = await call_next()
        
        # Calculate metrics
        query_count = database.query_count - start_count
        query_time = time.time() - start_time
        
        # Add metrics to response headers
        response.headers.update({
            "X-Database-Queries": str(query_count),
            "X-Database-Time": f"{query_time:.3f}s"
        })
        
        return response

app.add_middleware(DatabaseMetricsMiddleware())
```

## Connection Pooling

```python
from databases import DatabaseURL
from sqlalchemy.pool import QueuePool

# Configure connection pool
DATABASE_URL = DatabaseURL(os.getenv("DATABASE_URL"))
database = Database(
    str(DATABASE_URL),
    min_size=5,
    max_size=20,
    pool_class=QueuePool,
    pool_pre_ping=True
)

# Monitor pool status
@app.get("/admin/db/status")
async def db_status(request: Request, response: Response):
    pool = database._pool
    return response.json({
        "pool_size": pool.size(),
        "checkedin": pool.checkedin(),
        "overflow": pool.overflow(),
        "checkedout": pool.checkedout()
    })
```

## Exercises

1. **User Management System**:
   Create a complete user management system with roles:
   ```python
   # Additional tables
   roles = Table(
       "roles",
       metadata,
       Column("id", Integer, primary_key=True),
       Column("name", String(50), unique=True),
       Column("description", Text)
   )

   user_roles = Table(
       "user_roles",
       metadata,
       Column("user_id", Integer, ForeignKey("users.id")),
       Column("role_id", Integer, ForeignKey("roles.id")),
       Column("assigned_at", DateTime, default=datetime.utcnow)
   )

   # Role management
   @app.post("/roles")
   async def create_role(request: Request, response: Response):
       data = await request.json()
       query = roles.insert().values(**data)
       role_id = await database.execute(query)
       return response.json({"id": role_id, **data}, status_code=201)

   @app.post("/users/{user_id}/roles/{role_id}")
   async def assign_role(
       request: Request,
       response: Response,
       user_id: int,
       role_id: int
   ):
       query = user_roles.insert().values(
           user_id=user_id,
           role_id=role_id
       )
       await database.execute(query)
       return response.json({"message": "Role assigned"})
   ```

2. **Audit Trail System**:
   Implement an audit trail for database changes:
   ```python
   # Audit table
   audit_logs = Table(
       "audit_logs",
       metadata,
       Column("id", Integer, primary_key=True),
       Column("table_name", String(50)),
       Column("record_id", Integer),
       Column("action", String(10)),
       Column("old_values", Text),
       Column("new_values", Text),
       Column("user_id", Integer),
       Column("created_at", DateTime, default=datetime.utcnow)
   )

   class AuditMiddleware:
       async def __call__(
           self,
           request: Request,
           response: Response,
           call_next: Callable
       ):
           # Store original state
           if request.method in ["PUT", "PATCH", "DELETE"]:
               path_parts = request.url.path.split("/")
               if len(path_parts) >= 3:
                   table_name = path_parts[1]
                   record_id = path_parts[2]
                   
                   # Get original state
                   query = f"SELECT * FROM {table_name} WHERE id = :id"
                   old_values = await database.fetch_one(
                       query=query,
                       values={"id": record_id}
                   )
           
           response = await call_next()
           
           # Record audit log
           if response.status_code < 400 and request.method in ["POST", "PUT", "PATCH", "DELETE"]:
               await database.execute(
                   audit_logs.insert().values(
                       table_name=table_name,
                       record_id=record_id,
                       action=request.method,
                       old_values=str(old_values) if old_values else None,
                       new_values=str(await request.json()) if request.method != "DELETE" else None,
                       user_id=request.user.id if hasattr(request, "user") else None
                   )
               )
           
           return response
   ```

3. **Cache Layer**:
   Add a Redis cache layer for frequently accessed data:
   ```python
   import aioredis
   import json

   # Redis connection
   redis = aioredis.from_url("redis://localhost")

   class CacheMiddleware:
       def __init__(self, expire_time: int = 300):
           self.expire_time = expire_time
       
       async def __call__(
           self,
           request: Request,
           response: Response,
           call_next: Callable
       ):
           # Only cache GET requests
           if request.method != "GET":
               return await call_next()
           
           # Generate cache key
           cache_key = f"cache:{request.url.path}"
           
           # Try to get from cache
           cached = await redis.get(cache_key)
           if cached:
               return response.json(json.loads(cached))
           
           # Get fresh data
           response = await call_next()
           
           # Cache the response
           if response.status_code == 200:
               await redis.set(
                   cache_key,
                   json.dumps(response.body),
                   ex=self.expire_time
               )
           
           return response
   ```

## Mini-Project: Blog API with Database Integration

Create a complete blog API with database integration:

```python
from nexios import NexiosApp
from databases import Database
from sqlalchemy import (
    create_engine, MetaData, Table, Column, Integer,
    String, Text, ForeignKey, DateTime, Boolean
)
from datetime import datetime
import os
import slugify
from typing import Optional, List, Dict

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./blog.db")
database = Database(DATABASE_URL)
metadata = MetaData()

# Models
users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String(50), unique=True),
    Column("email", String(100), unique=True),
    Column("hashed_password", String(100)),
    Column("is_admin", Boolean, default=False),
    Column("created_at", DateTime, default=datetime.utcnow)
)

categories = Table(
    "categories",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), unique=True),
    Column("slug", String(50), unique=True),
    Column("description", Text)
)

posts = Table(
    "posts",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(200)),
    Column("slug", String(200), unique=True),
    Column("content", Text),
    Column("excerpt", Text),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("category_id", Integer, ForeignKey("categories.id")),
    Column("published", Boolean, default=False),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("updated_at", DateTime, default=datetime.utcnow)
)

comments = Table(
    "comments",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("content", Text),
    Column("post_id", Integer, ForeignKey("posts.id")),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("parent_id", Integer, ForeignKey("comments.id")),
    Column("created_at", DateTime, default=datetime.utcnow)
)

tags = Table(
    "tags",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), unique=True),
    Column("slug", String(50), unique=True)
)

post_tags = Table(
    "post_tags",
    metadata,
    Column("post_id", Integer, ForeignKey("posts.id")),
    Column("tag_id", Integer, ForeignKey("tags.id"))
)

# Application setup
app = NexiosApp()
app.state.database = database

@app.on_event("startup")
async def startup():
    await database.connect()
    
    # Create tables
    engine = create_engine(DATABASE_URL)
    metadata.create_all(engine)

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Post routes
@app.post("/posts")
async def create_post(request: Request, response: Response):
    data = await request.json()
    
    # Generate slug
    data["slug"] = slugify.slugify(data["title"])
    
    async with database.transaction():
        # Create post
        post_query = posts.insert().values(**data)
        post_id = await database.execute(post_query)
        
        # Add tags
        if "tags" in data:
            for tag_name in data["tags"]:
                # Create tag if it doesn't exist
                tag_data = {
                    "name": tag_name,
                    "slug": slugify.slugify(tag_name)
                }
                tag_query = tags.insert().values(**tag_data)
                try:
                    tag_id = await database.execute(tag_query)
                except:
                    # Tag already exists, get its ID
                    tag_query = tags.select().where(
                        tags.c.name == tag_name
                    )
                    tag = await database.fetch_one(tag_query)
                    tag_id = tag["id"]
                
                # Link tag to post
                post_tag_query = post_tags.insert().values(
                    post_id=post_id,
                    tag_id=tag_id
                )
                await database.execute(post_tag_query)
    
    return response.json({"id": post_id, **data}, status_code=201)

@app.get("/posts")
async def list_posts(
    request: Request,
    response: Response,
    page: int = 1,
    per_page: int = 10,
    category: str = None,
    tag: str = None,
    search: str = None
):
    # Base query
    query = posts.select()
    
    # Apply filters
    if category:
        category_query = categories.select().where(
            categories.c.slug == category
        )
        category_row = await database.fetch_one(category_query)
        if category_row:
            query = query.where(posts.c.category_id == category_row["id"])
    
    if tag:
        tag_query = tags.select().where(tags.c.slug == tag)
        tag_row = await database.fetch_one(tag_query)
        if tag_row:
            query = (
                query
                .join(post_tags)
                .where(post_tags.c.tag_id == tag_row["id"])
            )
    
    if search:
        query = query.where(
            posts.c.title.ilike(f"%{search}%") |
            posts.c.content.ilike(f"%{search}%")
        )
    
    # Count total
    count_query = query.alias("count_query").count()
    total = await database.fetch_val(count_query)
    
    # Apply pagination
    query = (
        query
        .offset((page - 1) * per_page)
        .limit(per_page)
        .order_by(posts.c.created_at.desc())
    )
    
    # Execute query
    results = await database.fetch_all(query)
    
    # Get related data
    posts_data = []
    for post in results:
        post_dict = dict(post)
        
        # Get author
        author_query = users.select().where(
            users.c.id == post["user_id"]
        )
        author = await database.fetch_one(author_query)
        post_dict["author"] = {
            "id": author["id"],
            "username": author["username"]
        }
        
        # Get category
        if post["category_id"]:
            category_query = categories.select().where(
                categories.c.id == post["category_id"]
            )
            category = await database.fetch_one(category_query)
            post_dict["category"] = dict(category)
        
        # Get tags
        tags_query = (
            tags.select()
            .join(post_tags)
            .where(post_tags.c.post_id == post["id"])
        )
        post_tags_rows = await database.fetch_all(tags_query)
        post_dict["tags"] = [dict(tag) for tag in post_tags_rows]
        
        posts_data.append(post_dict)
    
    return response.json({
        "items": posts_data,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page
    })

@app.get("/posts/{slug}")
async def get_post(request: Request, response: Response, slug: str):
    # Get post
    query = posts.select().where(posts.c.slug == slug)
    post = await database.fetch_one(query)
    
    if not post:
        return response.json(
            {"error": "Post not found"},
            status_code=404
        )
    
    post_data = dict(post)
    
    # Get author
    author_query = users.select().where(
        users.c.id == post["user_id"]
    )
    author = await database.fetch_one(author_query)
    post_data["author"] = {
        "id": author["id"],
        "username": author["username"]
    }
    
    # Get category
    if post["category_id"]:
        category_query = categories.select().where(
            categories.c.id == post["category_id"]
        )
        category = await database.fetch_one(category_query)
        post_data["category"] = dict(category)
    
    # Get tags
    tags_query = (
        tags.select()
        .join(post_tags)
        .where(post_tags.c.post_id == post["id"])
    )
    post_tags_rows = await database.fetch_all(tags_query)
    post_data["tags"] = [dict(tag) for tag in post_tags_rows]
    
    # Get comments
    comments_query = (
        comments.select()
        .where(comments.c.post_id == post["id"])
        .order_by(comments.c.created_at)
    )
    comments_rows = await database.fetch_all(comments_query)
    
    # Organize comments into threads
    comment_threads = []
    comment_map = {}
    
    for comment in comments_rows:
        comment_dict = dict(comment)
        
        # Get comment author
        author_query = users.select().where(
            users.c.id == comment["user_id"]
        )
        author = await database.fetch_one(author_query)
        comment_dict["author"] = {
            "id": author["id"],
            "username": author["username"]
        }
        
        comment_dict["replies"] = []
        comment_map[comment["id"]] = comment_dict
        
        if comment["parent_id"] is None:
            comment_threads.append(comment_dict)
        else:
            parent = comment_map[comment["parent_id"]]
            parent["replies"].append(comment_dict)
    
    post_data["comments"] = comment_threads
    
    return response.json(post_data)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
```

## Key Concepts Learned

- Database connection setup
- Model definition with SQLAlchemy
- CRUD operations
- Transactions
- Connection pooling
- Query optimization
- Database middleware
- Relationship handling
- Pagination
- Search and filtering
- Caching strategies
- Audit trails

## Additional Resources

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Databases Documentation](https://www.encode.io/databases/)
- [Database Design Patterns](https://www.postgresql.org/docs/current/patterns.html)
- [Query Optimization Guide](https://use-the-index-luke.com/)

## Homework

1. Implement a complete e-commerce database schema:
   - Products
   - Categories
   - Orders
   - Customers
   - Reviews
   - Inventory

2. Create a caching system:
   - Redis integration
   - Cache invalidation
   - Cache warming
   - Cache statistics

3. Build a reporting system:
   - Complex queries
   - Aggregations
   - Data exports
   - Scheduled reports

## Next Steps

Tomorrow, we'll explore authentication and authorization in [Day 8: Authentication & Authorization](../day08/index.md). 