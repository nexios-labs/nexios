# Day 14: Advanced Features

Welcome to Day 14! Today we'll explore advanced features and patterns in Nexios.

## Advanced Topics

- Dependency Injection
- Event Systems
- Plugin Architecture
- Service Discovery
- Circuit Breakers
- Background Tasks
- GraphQL Integration
- Microservices
- API Gateways

## Dependency Injection

```python
from typing import Any, Dict, Type, TypeVar
from dataclasses import dataclass
import inspect

T = TypeVar("T")

class Container:
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, callable] = {}
    
    def register(self, service_type: Type[T], instance: T):
        """Register a service instance"""
        self._services[service_type] = instance
    
    def register_factory(
        self,
        service_type: Type[T],
        factory: callable
    ):
        """Register a service factory"""
        self._factories[service_type] = factory
    
    def resolve(self, service_type: Type[T]) -> T:
        """Resolve a service"""
        # Check for instance
        if service_type in self._services:
            return self._services[service_type]
        
        # Check for factory
        if service_type in self._factories:
            factory = self._factories[service_type]
            
            # Get factory dependencies
            sig = inspect.signature(factory)
            deps = {}
            
            for name, param in sig.parameters.items():
                if param.annotation != inspect.Parameter.empty:
                    deps[name] = self.resolve(param.annotation)
            
            # Create instance
            instance = factory(**deps)
            self._services[service_type] = instance
            return instance
        
        raise KeyError(f"No registration for {service_type}")

# Example services
@dataclass
class Config:
    database_url: str
    redis_url: str

class Database:
    def __init__(self, config: Config):
        self.url = config.database_url

class Cache:
    def __init__(self, config: Config):
        self.url = config.redis_url

class UserService:
    def __init__(self, db: Database, cache: Cache):
        self.db = db
        self.cache = cache

# Setup container
container = Container()

# Register services
container.register(Config, Config(
    database_url="postgresql://localhost/db",
    redis_url="redis://localhost"
))

container.register_factory(Database, Database)
container.register_factory(Cache, Cache)
container.register_factory(UserService, UserService)

# Use in application
@app.on_event("startup")
async def startup():
    app.state.container = container

@app.get("/users/{user_id}")
async def get_user(
    request: Request,
    response: Response,
    user_id: int
):
    user_service = request.app.state.container.resolve(
        UserService
    )
    # Use user_service...
```

## Event System

```python
from typing import Callable, List, Dict, Any
import asyncio
import inspect
from datetime import datetime
import logging

class Event:
    def __init__(self, name: str, data: Dict[str, Any] = None):
        self.name = name
        self.data = data or {}
        self.timestamp = datetime.utcnow()

class EventBus:
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
        self._middleware: List[Callable] = []
        self.logger = logging.getLogger(__name__)
    
    def subscribe(self, event_name: str, handler: Callable):
        """Subscribe to an event"""
        if event_name not in self._handlers:
            self._handlers[event_name] = []
        self._handlers[event_name].append(handler)
    
    def add_middleware(self, middleware: Callable):
        """Add event middleware"""
        self._middleware.append(middleware)
    
    async def publish(self, event: Event):
        """Publish an event"""
        # Apply middleware
        for middleware in self._middleware:
            try:
                event = await self._call_async(middleware, event)
                if not event:
                    return
            except Exception as e:
                self.logger.error(
                    f"Middleware error: {str(e)}",
                    exc_info=True
                )
                return
        
        # Call handlers
        handlers = self._handlers.get(event.name, [])
        tasks = []
        
        for handler in handlers:
            task = asyncio.create_task(
                self._call_handler(handler, event)
            )
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks)
    
    async def _call_handler(self, handler: Callable, event: Event):
        """Call event handler safely"""
        try:
            await self._call_async(handler, event)
        except Exception as e:
            self.logger.error(
                f"Handler error: {str(e)}",
                exc_info=True
            )
    
    async def _call_async(self, func: Callable, *args, **kwargs):
        """Call function, handling both sync and async"""
        if inspect.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        return func(*args, **kwargs)

# Example usage
event_bus = EventBus()

# Logging middleware
async def logging_middleware(event: Event) -> Event:
    print(f"Event: {event.name} at {event.timestamp}")
    return event

event_bus.add_middleware(logging_middleware)

# Event handlers
async def user_created_handler(event: Event):
    user = event.data["user"]
    # Send welcome email...

async def user_created_stats_handler(event: Event):
    # Update statistics...
    pass

event_bus.subscribe("user.created", user_created_handler)
event_bus.subscribe("user.created", user_created_stats_handler)

# Use in application
@app.post("/users")
async def create_user(request: Request, response: Response):
    data = await request.json()
    
    # Create user...
    user = {"id": 1, "name": data["name"]}
    
    # Publish event
    await event_bus.publish(Event(
        "user.created",
        {"user": user}
    ))
    
    return response.json(user)
```

## Plugin System

```python
from typing import Dict, Type, List
import importlib
import pkgutil
import inspect
import logging
from abc import ABC, abstractmethod

class Plugin(ABC):
    @abstractmethod
    def initialize(self, app: "NexiosApp"):
        """Initialize plugin"""
        pass
    
    @abstractmethod
    def cleanup(self):
        """Cleanup plugin"""
        pass

class PluginManager:
    def __init__(self):
        self._plugins: Dict[str, Plugin] = {}
        self.logger = logging.getLogger(__name__)
    
    def register(self, name: str, plugin: Plugin):
        """Register a plugin"""
        self._plugins[name] = plugin
    
    def get(self, name: str) -> Plugin:
        """Get a plugin"""
        return self._plugins[name]
    
    def discover(self, package: str):
        """Discover plugins in package"""
        try:
            package_module = importlib.import_module(package)
        except ImportError as e:
            self.logger.error(f"Package not found: {str(e)}")
            return
        
        for _, name, _ in pkgutil.iter_modules(
            package_module.__path__
        ):
            try:
                module = importlib.import_module(
                    f"{package}.{name}"
                )
                
                # Find plugin classes
                for item_name, item in inspect.getmembers(
                    module,
                    inspect.isclass
                ):
                    if (
                        issubclass(item, Plugin) and
                        item != Plugin
                    ):
                        plugin = item()
                        self.register(name, plugin)
                        self.logger.info(
                            f"Discovered plugin: {name}"
                        )
            
            except Exception as e:
                self.logger.error(
                    f"Plugin load error: {str(e)}",
                    exc_info=True
                )
    
    async def initialize(self, app: "NexiosApp"):
        """Initialize all plugins"""
        for name, plugin in self._plugins.items():
            try:
                await self._call_async(
                    plugin.initialize,
                    app
                )
                self.logger.info(
                    f"Initialized plugin: {name}"
                )
            except Exception as e:
                self.logger.error(
                    f"Plugin init error: {str(e)}",
                    exc_info=True
                )
    
    async def cleanup(self):
        """Cleanup all plugins"""
        for name, plugin in self._plugins.items():
            try:
                await self._call_async(plugin.cleanup)
                self.logger.info(
                    f"Cleaned up plugin: {name}"
                )
            except Exception as e:
                self.logger.error(
                    f"Plugin cleanup error: {str(e)}",
                    exc_info=True
                )
    
    async def _call_async(self, func, *args, **kwargs):
        """Call function, handling both sync and async"""
        if inspect.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        return func(*args, **kwargs)

# Example plugin
class CachePlugin(Plugin):
    def __init__(self):
        self.cache = None
    
    async def initialize(self, app: "NexiosApp"):
        self.cache = await aioredis.from_url(
            "redis://localhost"
        )
        
        # Add to app state
        app.state.cache = self.cache
    
    async def cleanup(self):
        if self.cache:
            await self.cache.close()

# Use in application
plugin_manager = PluginManager()

# Register plugins
plugin_manager.register("cache", CachePlugin())

# Or discover plugins
plugin_manager.discover("my_plugins")

@app.on_event("startup")
async def startup():
    await plugin_manager.initialize(app)

@app.on_event("shutdown")
async def shutdown():
    await plugin_manager.cleanup()
```

## Circuit Breaker

```python
from enum import Enum
from typing import Callable, Any
import time
import asyncio
from dataclasses import dataclass
import logging

class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing fast
    HALF_OPEN = "half_open"  # Testing recovery

@dataclass
class CircuitConfig:
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    half_open_calls: int = 3

class CircuitBreaker:
    def __init__(self, config: CircuitConfig = None):
        self.config = config or CircuitConfig()
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.last_failure = 0
        self.successful_calls = 0
        self.logger = logging.getLogger(__name__)
    
    async def call(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute function with circuit breaker"""
        if not self._can_execute():
            raise Exception("Circuit is OPEN")
        
        try:
            result = await self._call_async(
                func,
                *args,
                **kwargs
            )
            
            await self._on_success()
            return result
            
        except Exception as e:
            await self._on_failure()
            raise
    
    def _can_execute(self) -> bool:
        """Check if execution is allowed"""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            if (
                time.time() - self.last_failure >
                self.config.recovery_timeout
            ):
                self.state = CircuitState.HALF_OPEN
                self.logger.info("Circuit HALF-OPEN")
                return True
            return False
        
        # HALF_OPEN
        return True
    
    async def _on_success(self):
        """Handle successful call"""
        if self.state == CircuitState.HALF_OPEN:
            self.successful_calls += 1
            if (
                self.successful_calls >=
                self.config.half_open_calls
            ):
                self.state = CircuitState.CLOSED
                self.failures = 0
                self.successful_calls = 0
                self.logger.info("Circuit CLOSED")
    
    async def _on_failure(self):
        """Handle failed call"""
        self.failures += 1
        self.last_failure = time.time()
        
        if (
            self.state == CircuitState.CLOSED and
            self.failures >= self.config.failure_threshold
        ):
            self.state = CircuitState.OPEN
            self.logger.warning("Circuit OPEN")
        
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            self.successful_calls = 0
            self.logger.warning(
                "Circuit OPEN (from HALF-OPEN)"
            )
    
    async def _call_async(self, func, *args, **kwargs):
        """Call function, handling both sync and async"""
        if inspect.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        return func(*args, **kwargs)

# Example usage
async def external_service():
    # Simulate external call
    await asyncio.sleep(0.1)
    if random.random() < 0.3:  # 30% failure rate
        raise Exception("Service error")
    return "success"

breaker = CircuitBreaker()

@app.get("/service")
async def call_service(request: Request, response: Response):
    try:
        result = await breaker.call(external_service)
        return response.json({"result": result})
    except Exception as e:
        return response.json({
            "error": str(e)
        }, status_code=503)
```

## GraphQL Integration

```python
import strawberry
from strawberry.asgi import GraphQL
from typing import List, Optional
from dataclasses import dataclass

# Types
@dataclass
class User:
    id: int
    name: str
    email: str

@dataclass
class Post:
    id: int
    title: str
    content: str
    author_id: int

# GraphQL types
@strawberry.type
class UserType:
    id: int
    name: str
    email: str
    
    @strawberry.field
    async def posts(self) -> List["PostType"]:
        return await get_user_posts(self.id)

@strawberry.type
class PostType:
    id: int
    title: str
    content: str
    
    @strawberry.field
    async def author(self) -> UserType:
        return await get_user(self.author_id)

# Queries
@strawberry.type
class Query:
    @strawberry.field
    async def user(
        self,
        id: int
    ) -> Optional[UserType]:
        return await get_user(id)
    
    @strawberry.field
    async def users(
        self,
        limit: int = 10,
        offset: int = 0
    ) -> List[UserType]:
        return await get_users(limit, offset)
    
    @strawberry.field
    async def posts(
        self,
        limit: int = 10,
        offset: int = 0
    ) -> List[PostType]:
        return await get_posts(limit, offset)

# Mutations
@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_user(
        self,
        name: str,
        email: str
    ) -> UserType:
        return await create_user(name, email)
    
    @strawberry.mutation
    async def create_post(
        self,
        title: str,
        content: str,
        author_id: int
    ) -> PostType:
        return await create_post(
            title,
            content,
            author_id
        )

# Create schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation
)

# Create GraphQL app
graphql_app = GraphQL(schema)

# Mount in Nexios
app.mount("/graphql", graphql_app)

# Example query
"""
query {
    users(limit: 5) {
        id
        name
        posts {
            title
            content
        }
    }
}
"""

# Example mutation
"""
mutation {
    createUser(name: "John", email: "john@example.com") {
        id
        name
        email
    }
}
"""
```

## Service Discovery

```python
from typing import Dict, List, Optional
import aiohttp
import asyncio
import json
import time
from dataclasses import dataclass
import random

@dataclass
class ServiceInstance:
    id: str
    name: str
    url: str
    health: str
    last_check: float

class ServiceRegistry:
    def __init__(self):
        self._services: Dict[str, List[ServiceInstance]] = {}
        self._lock = asyncio.Lock()
    
    async def register(
        self,
        name: str,
        instance: ServiceInstance
    ):
        """Register service instance"""
        async with self._lock:
            if name not in self._services:
                self._services[name] = []
            self._services[name].append(instance)
    
    async def unregister(
        self,
        name: str,
        instance_id: str
    ):
        """Unregister service instance"""
        async with self._lock:
            if name in self._services:
                self._services[name] = [
                    inst for inst in self._services[name]
                    if inst.id != instance_id
                ]
    
    async def get_instance(
        self,
        name: str
    ) -> Optional[ServiceInstance]:
        """Get service instance (with load balancing)"""
        instances = self._services.get(name, [])
        healthy = [
            inst for inst in instances
            if inst.health == "healthy"
        ]
        
        if not healthy:
            return None
        
        return random.choice(healthy)
    
    async def health_check(self):
        """Check health of all services"""
        while True:
            async with self._lock:
                for instances in self._services.values():
                    for instance in instances:
                        try:
                            async with aiohttp.ClientSession() as session:
                                async with session.get(
                                    f"{instance.url}/health"
                                ) as response:
                                    if response.status == 200:
                                        instance.health = "healthy"
                                    else:
                                        instance.health = "unhealthy"
                        except:
                            instance.health = "unhealthy"
                        
                        instance.last_check = time.time()
            
            await asyncio.sleep(30)  # Check every 30s

# Example usage
registry = ServiceRegistry()

# Register this service
@app.on_event("startup")
async def register_service():
    instance = ServiceInstance(
        id=str(uuid.uuid4()),
        name="api",
        url="http://localhost:8000",
        health="healthy",
        last_check=time.time()
    )
    
    await registry.register("api", instance)
    
    # Start health checks
    asyncio.create_task(registry.health_check())

# Service client
class ServiceClient:
    def __init__(
        self,
        registry: ServiceRegistry,
        service_name: str
    ):
        self.registry = registry
        self.service_name = service_name
    
    async def request(
        self,
        method: str,
        path: str,
        **kwargs
    ):
        instance = await self.registry.get_instance(
            self.service_name
        )
        
        if not instance:
            raise Exception(f"No healthy {self.service_name} instances")
        
        url = f"{instance.url}{path}"
        
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method,
                url,
                **kwargs
            ) as response:
                return await response.json()

# Use service client
auth_client = ServiceClient(registry, "auth")

@app.get("/protected")
async def protected_route(request: Request, response: Response):
    token = request.headers.get("Authorization")
    
    # Call auth service
    try:
        user = await auth_client.request(
            "POST",
            "/verify",
            json={"token": token}
        )
        return response.json({"user": user})
    except Exception as e:
        return response.json({
            "error": str(e)
        }, status_code=401)
```

## Mini-Project: Advanced API Gateway

```python
from nexios import NexiosApp
from nexios.http import Request, Response
import aiohttp
import asyncio
from typing import Dict, List, Optional
import time
import jwt
import logging
from dataclasses import dataclass
import uuid

# Configuration
@dataclass
class GatewayConfig:
    jwt_secret: str
    rate_limit: int = 100
    circuit_timeout: float = 60.0
    cache_ttl: int = 300

# Service registry
registry = ServiceRegistry()

# Circuit breaker
breaker = CircuitBreaker(CircuitConfig(
    failure_threshold=5,
    recovery_timeout=60.0,
    half_open_calls=3
))

# Rate limiter
rate_limiter = RateLimiter()

# Cache
cache = CacheManager(
    aioredis.from_url("redis://localhost")
)

# Initialize app
app = NexiosApp()

# Middleware
@app.middleware("http")
async def gateway_middleware(
    request: Request,
    response: Response,
    call_next: Callable
):
    # Rate limiting
    client_ip = request.client.host
    if not await rate_limiter.is_allowed(
        client_ip,
        RateLimit(100, 60)
    ):
        return response.json({
            "error": "Rate limit exceeded"
        }, status_code=429)
    
    # Authentication
    token = request.headers.get("Authorization")
    if token:
        try:
            payload = jwt.decode(
                token,
                config.jwt_secret,
                algorithms=["HS256"]
            )
            request.state.user = payload
        except jwt.InvalidTokenError:
            return response.json({
                "error": "Invalid token"
            }, status_code=401)
    
    return await call_next()

# Service routing
async def route_request(
    service: str,
    request: Request,
    **kwargs
) -> Response:
    # Get service instance
    instance = await registry.get_instance(service)
    if not instance:
        return Response(
            json={"error": f"Service {service} unavailable"},
            status_code=503
        )
    
    # Build URL
    url = f"{instance.url}{request.url.path}"
    
    # Forward request
    try:
        async with aiohttp.ClientSession() as session:
            async with session.request(
                request.method,
                url,
                headers=request.headers,
                **kwargs
            ) as response:
                return Response(
                    body=await response.read(),
                    status_code=response.status,
                    headers=dict(response.headers)
                )
    except Exception as e:
        return Response(
            json={"error": str(e)},
            status_code=500
        )

# Routes
@app.get("/users/{user_id}")
@cached("user", expire=300)
async def get_user(
    request: Request,
    response: Response,
    user_id: int
):
    return await route_request(
        "user-service",
        request
    )

@app.post("/orders")
async def create_order(request: Request, response: Response):
    # Verify authentication
    if not hasattr(request.state, "user"):
        return response.json({
            "error": "Authentication required"
        }, status_code=401)
    
    # Get order data
    data = await request.json()
    
    # Call inventory service
    inventory_result = await breaker.call(
        route_request,
        "inventory-service",
        request,
        json={"items": data["items"]}
    )
    
    if inventory_result.status_code != 200:
        return inventory_result
    
    # Call order service
    order_result = await breaker.call(
        route_request,
        "order-service",
        request,
        json={
            **data,
            "user_id": request.state.user["id"]
        }
    )
    
    if order_result.status_code == 201:
        # Publish event
        await event_bus.publish(Event(
            "order.created",
            {"order": await order_result.json()}
        ))
    
    return order_result

@app.get("/products")
@cached("products", expire=300)
async def list_products(
    request: Request,
    response: Response
):
    return await route_request(
        "product-service",
        request
    )

# WebSocket proxy
@app.websocket("/ws/{service}")
async def websocket_proxy(
    websocket: WebSocket,
    service: str
):
    await websocket.accept()
    
    # Get service instance
    instance = await registry.get_instance(service)
    if not instance:
        await websocket.close(1003, "Service unavailable")
        return
    
    # Connect to service
    service_ws = await websocket.connect(
        f"{instance.url}/ws"
    )
    
    try:
        # Forward messages both ways
        while True:
            done, pending = await asyncio.wait(
                [
                    websocket.receive_text(),
                    service_ws.receive_text()
                ],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            for task in pending:
                task.cancel()
            
            for task in done:
                message = await task
                if task == websocket.receive_text():
                    await service_ws.send_text(message)
                else:
                    await websocket.send_text(message)
    
    except Exception as e:
        logging.error(f"WebSocket error: {str(e)}")
    
    finally:
        await websocket.close()
        await service_ws.close()

# Health check
@app.get("/health")
async def health_check(request: Request, response: Response):
    services = {}
    
    for name, instances in registry._services.items():
        healthy = sum(
            1 for i in instances
            if i.health == "healthy"
        )
        total = len(instances)
        
        services[name] = {
            "healthy": healthy,
            "total": total,
            "status": "up" if healthy > 0 else "down"
        }
    
    return response.json({
        "status": "healthy",
        "services": services
    })

# Metrics
@app.get("/metrics")
async def metrics(request: Request, response: Response):
    metrics = {
        "requests_total": REQUEST_COUNT._value.get(),
        "request_latency": {
            "avg": REQUEST_LATENCY._sum.get() / max(REQUEST_LATENCY._count.get(), 1),
            "count": REQUEST_LATENCY._count.get()
        },
        "circuit_breaker": {
            "state": breaker.state.value,
            "failures": breaker.failures
        },
        "rate_limiter": {
            "blocked": rate_limiter.blocked_count
        },
        "cache": {
            "hits": cache.hits,
            "misses": cache.misses
        }
    }
    
    return response.json(metrics)

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

- Dependency Injection
- Event Systems
- Plugin Architecture
- Service Discovery
- Circuit Breakers
- GraphQL Integration
- API Gateway Patterns
- Microservices Communication
- Advanced Middleware

## Additional Resources

- [Microservices Patterns](https://microservices.io/patterns/)
- [GraphQL Documentation](https://graphql.org/learn/)
- [Event-Driven Architecture](https://www.confluent.io/learn/event-driven-architecture/)
- [Service Mesh](https://istio.io/latest/docs/concepts/what-is-istio/)

## Homework

1. Build a plugin system:
   - Plugin discovery
   - Hot reloading
   - Configuration
   - Event handling

2. Create a service mesh:
   - Service discovery
   - Load balancing
   - Circuit breaking
   - Monitoring

3. Implement GraphQL API:
   - Schema design
   - Resolvers
   - Subscriptions
   - Caching

## Next Steps

Tomorrow, we'll explore [Day 15: Microservices Architecture](../day15/index.md). 