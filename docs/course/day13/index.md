# Day 13: Performance Optimization

Welcome to Day 13! Today we'll learn how to optimize Nexios applications for maximum performance.

## Understanding Performance

Key performance aspects:
- Response time
- Throughput
- Resource usage
- Caching
- Database optimization
- Asynchronous operations
- Load balancing
- Memory management

## Caching System

```python
from nexios import NexiosApp
from nexios.http import Request, Response
import aioredis
import json
from typing import Optional, Any, Union
from datetime import datetime
import pickle
import hashlib

class CacheManager:
    def __init__(self, redis_url: str):
        self.redis = aioredis.from_url(redis_url)
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        data = await self.redis.get(key)
        if data:
            return pickle.loads(data)
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        expire: int = 300
    ) -> bool:
        """Set value in cache with expiration"""
        try:
            data = pickle.dumps(value)
            await self.redis.set(key, data, ex=expire)
            return True
        except:
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        return await self.redis.delete(key) > 0
    
    async def clear(self, pattern: str = "*") -> int:
        """Clear cache entries matching pattern"""
        keys = await self.redis.keys(pattern)
        if keys:
            return await self.redis.delete(*keys)
        return 0

# Initialize app and cache
app = NexiosApp()
cache = CacheManager("redis://localhost")

def cache_key(prefix: str, *args: Any) -> str:
    """Generate cache key from arguments"""
    key_parts = [prefix] + [str(arg) for arg in args]
    return hashlib.md5(
        ":".join(key_parts).encode()
    ).hexdigest()

# Cache decorator
def cached(prefix: str, expire: int = 300):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key = cache_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_value = await cache.get(key)
            if cached_value is not None:
                return cached_value
            
            # Get fresh value
            value = await func(*args, **kwargs)
            
            # Cache value
            await cache.set(key, value, expire)
            
            return value
        return wrapper
    return decorator

# Example usage
@app.get("/users/{user_id}")
@cached("user", expire=60)
async def get_user(request: Request, response: Response, user_id: int):
    # Simulate database query
    await asyncio.sleep(0.1)
    return response.json({
        "id": user_id,
        "name": f"User {user_id}"
    })
```

## Database Optimization

```python
from databases import Database
from sqlalchemy import create_engine, text
from typing import List, Dict, Any
import asyncio
import time

class OptimizedDatabase:
    def __init__(self, url: str):
        self.db = Database(url)
        self.engine = create_engine(url)
    
    async def execute_batch(
        self,
        query: str,
        values: List[Dict[str, Any]],
        batch_size: int = 1000
    ):
        """Execute batch insert/update"""
        results = []
        for i in range(0, len(values), batch_size):
            batch = values[i:i + batch_size]
            async with self.db.transaction():
                result = await self.db.execute_many(
                    query=query,
                    values=batch
                )
                results.append(result)
        return sum(results)
    
    async def fetch_chunked(
        self,
        query: str,
        params: Dict[str, Any] = None,
        chunk_size: int = 1000
    ):
        """Fetch large result sets in chunks"""
        offset = 0
        while True:
            chunked_query = f"""
                {query}
                LIMIT {chunk_size}
                OFFSET {offset}
            """
            chunk = await self.db.fetch_all(
                query=chunked_query,
                values=params
            )
            if not chunk:
                break
            
            for row in chunk:
                yield row
            
            offset += chunk_size
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze query performance"""
        with self.engine.connect() as conn:
            # Get query plan
            explain = conn.execute(
                text(f"EXPLAIN ANALYZE {query}")
            ).fetchall()
            
            # Parse execution time
            for row in explain:
                if "Execution Time:" in row[0]:
                    time_ms = float(
                        row[0].split(":")[-1].strip().split(" ")[0]
                    )
                    return {
                        "execution_time_ms": time_ms,
                        "plan": [row[0] for row in explain]
                    }
            
            return {
                "execution_time_ms": None,
                "plan": [row[0] for row in explain]
            }

# Example usage
db = OptimizedDatabase("postgresql://user:pass@localhost/db")

# Batch insert
users = [
    {"name": f"User {i}", "email": f"user{i}@example.com"}
    for i in range(10000)
]

await db.execute_batch(
    query="INSERT INTO users (name, email) VALUES (:name, :email)",
    values=users
)

# Chunked fetch
async for user in db.fetch_chunked(
    query="SELECT * FROM users ORDER BY id"
):
    process_user(user)

# Query analysis
analysis = db.analyze_query(
    "SELECT users.*, posts.* FROM users JOIN posts ON users.id = posts.user_id"
)
print(f"Execution time: {analysis['execution_time_ms']}ms")
```

## Connection Pooling

```python
from asyncio import Queue, Lock
from typing import Dict, Set, Optional
import time
import asyncio

class ConnectionPool:
    def __init__(
        self,
        create_connection,
        min_size: int = 5,
        max_size: int = 20,
        max_idle: int = 300
    ):
        self.create_connection = create_connection
        self.min_size = min_size
        self.max_size = max_size
        self.max_idle = max_idle
        
        self.pool: Queue = Queue()
        self.size = 0
        self.lock = Lock()
        
        # Connection tracking
        self.in_use: Set = set()
        self.last_used: Dict = {}
    
    async def initialize(self):
        """Initialize minimum connections"""
        for _ in range(self.min_size):
            conn = await self.create_connection()
            await self.pool.put(conn)
            self.size += 1
    
    async def acquire(self):
        """Get a connection from the pool"""
        async with self.lock:
            # Try to get existing connection
            try:
                while True:
                    conn = await self.pool.get_nowait()
                    
                    # Check if connection is too old
                    last_used = self.last_used.get(id(conn))
                    if (
                        last_used and
                        time.time() - last_used > self.max_idle
                    ):
                        await self.close_connection(conn)
                        continue
                    
                    self.in_use.add(conn)
                    return conn
            except asyncio.QueueEmpty:
                pass
            
            # Create new connection if possible
            if self.size < self.max_size:
                conn = await self.create_connection()
                self.size += 1
                self.in_use.add(conn)
                return conn
            
            # Wait for available connection
            conn = await self.pool.get()
            self.in_use.add(conn)
            return conn
    
    async def release(self, conn):
        """Return a connection to the pool"""
        self.in_use.remove(conn)
        self.last_used[id(conn)] = time.time()
        await self.pool.put(conn)
    
    async def close_connection(self, conn):
        """Close a connection"""
        await conn.close()
        self.size -= 1
        if id(conn) in self.last_used:
            del self.last_used[id(conn)]
    
    async def cleanup(self):
        """Clean up idle connections"""
        while True:
            await asyncio.sleep(60)  # Check every minute
            
            current_time = time.time()
            to_close = []
            
            # Find idle connections
            async with self.lock:
                for _ in range(self.pool.qsize()):
                    try:
                        conn = self.pool.get_nowait()
                        last_used = self.last_used.get(id(conn))
                        
                        if (
                            last_used and
                            current_time - last_used > self.max_idle and
                            self.size > self.min_size
                        ):
                            to_close.append(conn)
                        else:
                            await self.pool.put(conn)
                    except asyncio.QueueEmpty:
                        break
            
            # Close idle connections
            for conn in to_close:
                await self.close_connection(conn)

# Example usage
async def create_db_connection():
    return await Database("postgresql://user:pass@localhost/db")

pool = ConnectionPool(create_db_connection)
await pool.initialize()

# Start cleanup task
asyncio.create_task(pool.cleanup())

async def execute_query(query: str, params: dict = None):
    conn = await pool.acquire()
    try:
        return await conn.fetch_all(query, params)
    finally:
        await pool.release(conn)
```

## Response Compression

```python
import gzip
import zlib
from typing import Optional

class CompressionMiddleware:
    def __init__(
        self,
        min_size: int = 1000,
        compression_level: int = 6
    ):
        self.min_size = min_size
        self.compression_level = compression_level
    
    def should_compress(
        self,
        accept_encoding: str,
        content_type: str,
        content_length: int
    ) -> Optional[str]:
        """Determine if and how to compress response"""
        if content_length < self.min_size:
            return None
        
        # Check content type
        compressible_types = {
            "text/",
            "application/json",
            "application/xml",
            "application/javascript"
        }
        
        if not any(
            t in content_type
            for t in compressible_types
        ):
            return None
        
        # Check accepted encoding
        if "gzip" in accept_encoding:
            return "gzip"
        elif "deflate" in accept_encoding:
            return "deflate"
        
        return None
    
    async def __call__(
        self,
        request: Request,
        response: Response,
        call_next: Callable
    ):
        response = await call_next()
        
        # Get response content
        content = response.body
        if not content:
            return response
        
        # Check compression
        encoding = self.should_compress(
            request.headers.get("Accept-Encoding", ""),
            response.headers.get("Content-Type", ""),
            len(content)
        )
        
        if not encoding:
            return response
        
        # Compress content
        if encoding == "gzip":
            compressed = gzip.compress(
                content,
                self.compression_level
            )
        else:  # deflate
            compressed = zlib.compress(
                content,
                self.compression_level
            )
        
        # Update response
        response.body = compressed
        response.headers.update({
            "Content-Encoding": encoding,
            "Content-Length": str(len(compressed)),
            "Vary": "Accept-Encoding"
        })
        
        return response

app.add_middleware(CompressionMiddleware())
```

## Asynchronous Task Processing

```python
from typing import Callable, Dict, List
import asyncio
import time
import logging

class TaskQueue:
    def __init__(
        self,
        max_workers: int = 10,
        max_queue_size: int = 1000
    ):
        self.queue: asyncio.Queue = asyncio.Queue(max_queue_size)
        self.max_workers = max_workers
        self.workers: List[asyncio.Task] = []
        self.running = False
        self.logger = logging.getLogger(__name__)
    
    async def start(self):
        """Start task processors"""
        self.running = True
        for _ in range(self.max_workers):
            worker = asyncio.create_task(self._process_tasks())
            self.workers.append(worker)
    
    async def stop(self):
        """Stop task processors"""
        self.running = False
        await self.queue.join()
        for worker in self.workers:
            worker.cancel()
        self.workers.clear()
    
    async def add_task(
        self,
        func: Callable,
        *args,
        **kwargs
    ):
        """Add task to queue"""
        await self.queue.put((func, args, kwargs))
    
    async def _process_tasks(self):
        """Process tasks from queue"""
        while self.running:
            try:
                func, args, kwargs = await self.queue.get()
                
                start_time = time.time()
                try:
                    await func(*args, **kwargs)
                except Exception as e:
                    self.logger.error(
                        f"Task error: {str(e)}",
                        exc_info=True
                    )
                finally:
                    duration = time.time() - start_time
                    self.logger.info(
                        f"Task completed in {duration:.2f}s"
                    )
                    self.queue.task_done()
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(
                    f"Worker error: {str(e)}",
                    exc_info=True
                )

# Example usage
task_queue = TaskQueue()

async def process_image(image_data: bytes):
    # Simulate image processing
    await asyncio.sleep(1)
    return "processed"

@app.post("/upload")
async def upload_image(request: Request, response: Response):
    data = await request.body()
    
    # Add processing task to queue
    await task_queue.add_task(process_image, data)
    
    return response.json({
        "message": "Processing started"
    })

# Start task queue
@app.on_event("startup")
async def startup():
    await task_queue.start()

# Stop task queue
@app.on_event("shutdown")
async def shutdown():
    await task_queue.stop()
```

## Mini-Project: High-Performance API

```python
from nexios import NexiosApp
from nexios.http import Request, Response
from typing import Optional, Dict, Any
import aioredis
import asyncpg
import ujson
import time
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

# Configuration
@dataclass
class Config:
    redis_url: str = "redis://localhost"
    postgres_url: str = "postgresql://user:pass@localhost/db"
    cache_ttl: int = 300
    pool_min_size: int = 5
    pool_max_size: int = 20
    compression_threshold: int = 1000

# Initialize app
app = NexiosApp()
config = Config()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database pool
async def init_db_pool():
    return await asyncpg.create_pool(
        config.postgres_url,
        min_size=config.pool_min_size,
        max_size=config.pool_max_size
    )

# Redis connection
async def init_redis():
    return aioredis.from_url(config.redis_url)

# Cache manager
class CacheManager:
    def __init__(self, redis):
        self.redis = redis
    
    async def get(self, key: str) -> Optional[Any]:
        data = await self.redis.get(key)
        return ujson.loads(data) if data else None
    
    async def set(
        self,
        key: str,
        value: Any,
        expire: int = None
    ):
        data = ujson.dumps(value)
        await self.redis.set(
            key,
            data,
            ex=expire or config.cache_ttl
        )
    
    async def delete(self, key: str):
        await self.redis.delete(key)

# Performance middleware
class PerformanceMiddleware:
    async def __call__(
        self,
        request: Request,
        response: Response,
        call_next: Callable
    ):
        start_time = time.time()
        
        try:
            response = await call_next()
            
            # Add timing header
            duration = time.time() - start_time
            response.headers["X-Response-Time"] = f"{duration:.4f}s"
            
            # Compress if needed
            if (
                len(response.body) > config.compression_threshold and
                "gzip" in request.headers.get("Accept-Encoding", "")
            ):
                response.body = gzip.compress(response.body)
                response.headers.update({
                    "Content-Encoding": "gzip",
                    "Vary": "Accept-Encoding"
                })
            
            return response
            
        except Exception as e:
            logger.error(f"Request error: {str(e)}", exc_info=True)
            raise

# Initialize services
@app.on_event("startup")
async def startup():
    app.state.db = await init_db_pool()
    app.state.redis = await init_redis()
    app.state.cache = CacheManager(app.state.redis)

# Cleanup
@app.on_event("shutdown")
async def shutdown():
    await app.state.db.close()
    await app.state.redis.close()

# Routes
@app.get("/products")
async def list_products(
    request: Request,
    response: Response,
    category: Optional[str] = None,
    page: int = 1,
    per_page: int = 20
):
    # Generate cache key
    cache_key = f"products:{category}:{page}:{per_page}"
    
    # Try cache
    cached = await app.state.cache.get(cache_key)
    if cached:
        return response.json(cached)
    
    # Build query
    query = """
        SELECT p.*, c.name as category_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE ($1::text IS NULL OR c.name = $1)
        ORDER BY p.created_at DESC
        LIMIT $2 OFFSET $3
    """
    
    # Get total count
    count_query = """
        SELECT COUNT(*)
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE ($1::text IS NULL OR c.name = $1)
    """
    
    async with app.state.db.acquire() as conn:
        # Execute queries in parallel
        count_result, rows = await asyncio.gather(
            conn.fetchval(count_query, category),
            conn.fetch(
                query,
                category,
                per_page,
                (page - 1) * per_page
            )
        )
    
    # Format response
    result = {
        "items": [dict(row) for row in rows],
        "total": count_result,
        "page": page,
        "per_page": per_page,
        "pages": (count_result + per_page - 1) // per_page
    }
    
    # Cache result
    await app.state.cache.set(cache_key, result)
    
    return response.json(result)

@app.get("/products/{product_id}")
async def get_product(
    request: Request,
    response: Response,
    product_id: int
):
    # Try cache
    cache_key = f"product:{product_id}"
    cached = await app.state.cache.get(cache_key)
    if cached:
        return response.json(cached)
    
    # Get product
    query = """
        SELECT p.*, c.name as category_name,
               array_agg(pi.url) as images
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        LEFT JOIN product_images pi ON p.id = pi.product_id
        WHERE p.id = $1
        GROUP BY p.id, c.name
    """
    
    async with app.state.db.acquire() as conn:
        product = await conn.fetchrow(query, product_id)
    
    if not product:
        return response.json(
            {"error": "Product not found"},
            status_code=404
        )
    
    result = dict(product)
    
    # Cache result
    await app.state.cache.set(cache_key, result)
    
    return response.json(result)

@app.post("/products")
async def create_product(request: Request, response: Response):
    data = await request.json()
    
    # Validate input
    required = {"name", "price", "category_id"}
    if not all(field in data for field in required):
        return response.json({
            "error": "Missing required fields"
        }, status_code=400)
    
    # Insert product
    query = """
        INSERT INTO products (name, price, category_id)
        VALUES ($1, $2, $3)
        RETURNING id
    """
    
    async with app.state.db.acquire() as conn:
        async with conn.transaction():
            product_id = await conn.fetchval(
                query,
                data["name"],
                data["price"],
                data["category_id"]
            )
            
            # Insert images if provided
            if "images" in data:
                image_query = """
                    INSERT INTO product_images (product_id, url)
                    VALUES ($1, $2)
                """
                await conn.executemany(
                    image_query,
                    [(product_id, url) for url in data["images"]]
                )
    
    # Invalidate cache
    await app.state.cache.delete("products:*")
    
    return response.json({
        "id": product_id,
        **data
    }, status_code=201)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        workers=4
    )
```

## Key Concepts Learned

- Caching strategies
- Database optimization
- Connection pooling
- Response compression
- Asynchronous processing
- Query optimization
- Memory management
- Load balancing
- Performance monitoring

## Additional Resources

- [ASGI Performance](https://www.python-httpx.org/performance/)
- [PostgreSQL Optimization](https://www.postgresql.org/docs/current/performance-tips.html)
- [Redis Best Practices](https://redis.io/topics/optimization)
- [Async Python](https://docs.python.org/3/library/asyncio.html)

## Homework

1. Create a caching system:
   - Multi-level cache
   - Cache invalidation
   - Cache warming
   - Cache statistics

2. Optimize database operations:
   - Query optimization
   - Index management
   - Connection pooling
   - Batch operations

3. Build a load testing suite:
   - Performance benchmarks
   - Stress testing
   - Bottleneck identification
   - Optimization recommendations

## Next Steps

Tomorrow, we'll explore advanced features in [Day 14: Advanced Features](../day14/index.md). 