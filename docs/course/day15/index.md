# Day 15: Microservices Architecture

Welcome to Day 15! Today we'll learn about building microservices with Nexios.

## Understanding Microservices

Key aspects:
- Service decomposition
- Inter-service communication
- Data management
- Service discovery
- Load balancing
- Fault tolerance
- Monitoring
- Deployment
- Security

## Service Template

```python
from nexios import NexiosApp
from nexios.http import Request, Response
from typing import Optional, Dict, Any
import asyncpg
import aioredis
import logging
import os
from dataclasses import dataclass

# Configuration
@dataclass
class ServiceConfig:
    name: str
    version: str
    database_url: str
    redis_url: str
    registry_url: str
    log_level: str = "INFO"

    @classmethod
    def from_env(cls):
        return cls(
            name=os.getenv("SERVICE_NAME", "unknown"),
            version=os.getenv("SERVICE_VERSION", "0.1.0"),
            database_url=os.getenv("DATABASE_URL"),
            redis_url=os.getenv("REDIS_URL"),
            registry_url=os.getenv("REGISTRY_URL"),
            log_level=os.getenv("LOG_LEVEL", "INFO")
        )

class Service:
    def __init__(self, config: ServiceConfig):
        self.config = config
        self.app = NexiosApp()
        self.logger = self._setup_logging()
        
        # Setup middleware
        self._setup_middleware()
        
        # Setup routes
        self._setup_routes()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logger = logging.getLogger(self.config.name)
        logger.setLevel(self.config.log_level)
        
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )
        logger.addHandler(handler)
        
        return logger
    
    def _setup_middleware(self):
        """Setup middleware stack"""
        # Logging middleware
        @self.app.middleware("http")
        async def logging_middleware(
            request: Request,
            response: Response,
            call_next: Callable
        ):
            start_time = time.time()
            
            try:
                response = await call_next()
                
                duration = time.time() - start_time
                self.logger.info(
                    f"{request.method} {request.url.path} "
                    f"- {response.status_code} "
                    f"({duration:.3f}s)"
                )
                
                return response
                
            except Exception as e:
                self.logger.error(
                    f"Request error: {str(e)}",
                    exc_info=True
                )
                raise
        
        # Tracing middleware
        @self.app.middleware("http")
        async def tracing_middleware(
            request: Request,
            response: Response,
            call_next: Callable
        ):
            trace_id = request.headers.get(
                "X-Trace-ID",
                str(uuid.uuid4())
            )
            
            request.state.trace_id = trace_id
            response.headers["X-Trace-ID"] = trace_id
            
            return await call_next()
    
    def _setup_routes(self):
        """Setup service routes"""
        @self.app.get("/health")
        async def health_check(
            request: Request,
            response: Response
        ):
            return response.json({
                "service": self.config.name,
                "version": self.config.version,
                "status": "healthy"
            })
        
        @self.app.get("/metrics")
        async def metrics(
            request: Request,
            response: Response
        ):
            # Add your metrics here
            return response.json({
                "service": self.config.name,
                "uptime": time.time() - self.start_time,
                "requests": self.request_count
            })
    
    async def startup(self):
        """Initialize service"""
        # Connect to database
        self.db = await asyncpg.create_pool(
            self.config.database_url
        )
        
        # Connect to Redis
        self.redis = aioredis.from_url(
            self.config.redis_url
        )
        
        # Register with service registry
        await self.register_service()
        
        self.start_time = time.time()
        self.request_count = 0
        
        self.logger.info(
            f"Service {self.config.name} started"
        )
    
    async def shutdown(self):
        """Cleanup service"""
        # Close database connection
        await self.db.close()
        
        # Close Redis connection
        await self.redis.close()
        
        # Unregister from service registry
        await self.unregister_service()
        
        self.logger.info(
            f"Service {self.config.name} stopped"
        )
    
    async def register_service(self):
        """Register with service registry"""
        async with aiohttp.ClientSession() as session:
            await session.post(
                f"{self.config.registry_url}/register",
                json={
                    "name": self.config.name,
                    "version": self.config.version,
                    "url": "http://localhost:8000",  # Replace with actual URL
                    "health_check": "/health"
                }
            )
    
    async def unregister_service(self):
        """Unregister from service registry"""
        async with aiohttp.ClientSession() as session:
            await session.post(
                f"{self.config.registry_url}/unregister",
                json={
                    "name": self.config.name
                }
            )
    
    def run(self):
        """Run the service"""
        import uvicorn
        
        # Setup events
        self.app.on_event("startup")(self.startup)
        self.app.on_event("shutdown")(self.shutdown)
        
        # Run server
        uvicorn.run(
            self.app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )

# Example service implementation
class UserService(Service):
    def _setup_routes(self):
        super()._setup_routes()
        
        @self.app.get("/users/{user_id}")
        async def get_user(
            request: Request,
            response: Response,
            user_id: int
        ):
            async with self.db.acquire() as conn:
                user = await conn.fetchrow(
                    "SELECT * FROM users WHERE id = $1",
                    user_id
                )
                
                if not user:
                    return response.json({
                        "error": "User not found"
                    }, status_code=404)
                
                return response.json(dict(user))
        
        @self.app.post("/users")
        async def create_user(
            request: Request,
            response: Response
        ):
            data = await request.json()
            
            async with self.db.acquire() as conn:
                user = await conn.fetchrow(
                    """
                    INSERT INTO users (name, email)
                    VALUES ($1, $2)
                    RETURNING *
                    """,
                    data["name"],
                    data["email"]
                )
                
                return response.json(
                    dict(user),
                    status_code=201
                )

# Run service
if __name__ == "__main__":
    config = ServiceConfig.from_env()
    service = UserService(config)
    service.run()
```

## Service Registry

```python
from nexios import NexiosApp
from nexios.http import Request, Response
from typing import Dict, List, Optional
import time
import asyncio
import aiohttp
from dataclasses import dataclass
import logging

@dataclass
class ServiceInfo:
    name: str
    version: str
    url: str
    health_check: str
    last_check: float
    status: str = "unknown"

class Registry:
    def __init__(self):
        self.services: Dict[str, List[ServiceInfo]] = {}
        self.lock = asyncio.Lock()
        self.logger = logging.getLogger("registry")
    
    async def register(self, info: ServiceInfo):
        """Register a service"""
        async with self.lock:
            if info.name not in self.services:
                self.services[info.name] = []
            
            # Check for duplicates
            for existing in self.services[info.name]:
                if existing.url == info.url:
                    existing.version = info.version
                    existing.health_check = info.health_check
                    existing.last_check = time.time()
                    return
            
            # Add new service
            info.last_check = time.time()
            self.services[info.name].append(info)
            
            self.logger.info(
                f"Registered service: {info.name} at {info.url}"
            )
    
    async def unregister(self, name: str, url: str):
        """Unregister a service"""
        async with self.lock:
            if name in self.services:
                self.services[name] = [
                    s for s in self.services[name]
                    if s.url != url
                ]
                
                self.logger.info(
                    f"Unregistered service: {name} at {url}"
                )
    
    async def get_service(
        self,
        name: str
    ) -> Optional[ServiceInfo]:
        """Get a service instance (with load balancing)"""
        if name not in self.services:
            return None
        
        # Get healthy services
        healthy = [
            s for s in self.services[name]
            if s.status == "healthy"
        ]
        
        if not healthy:
            return None
        
        # Simple round-robin
        service = healthy[0]
        healthy.append(healthy.pop(0))
        
        return service
    
    async def check_health(self):
        """Check health of all services"""
        while True:
            async with self.lock:
                async with aiohttp.ClientSession() as session:
                    for services in self.services.values():
                        for service in services:
                            try:
                                url = f"{service.url}{service.health_check}"
                                async with session.get(url) as response:
                                    service.status = (
                                        "healthy"
                                        if response.status == 200
                                        else "unhealthy"
                                    )
                            except:
                                service.status = "unhealthy"
                            
                            service.last_check = time.time()
            
            # Remove old services
            await self.cleanup()
            
            await asyncio.sleep(30)
    
    async def cleanup(self):
        """Remove inactive services"""
        async with self.lock:
            now = time.time()
            for name in list(self.services.keys()):
                self.services[name] = [
                    s for s in self.services[name]
                    if now - s.last_check < 90  # 90s timeout
                ]
                
                if not self.services[name]:
                    del self.services[name]

# Create registry app
app = NexiosApp()
registry = Registry()

@app.post("/register")
async def register_service(request: Request, response: Response):
    data = await request.json()
    
    info = ServiceInfo(
        name=data["name"],
        version=data["version"],
        url=data["url"],
        health_check=data["health_check"],
        last_check=time.time()
    )
    
    await registry.register(info)
    
    return response.json({
        "status": "registered"
    })

@app.post("/unregister")
async def unregister_service(request: Request, response: Response):
    data = await request.json()
    
    await registry.unregister(
        data["name"],
        data["url"]
    )
    
    return response.json({
        "status": "unregistered"
    })

@app.get("/services")
async def list_services(request: Request, response: Response):
    services = {}
    
    for name, instances in registry.services.items():
        services[name] = [
            {
                "version": s.version,
                "url": s.url,
                "status": s.status,
                "last_check": s.last_check
            }
            for s in instances
        ]
    
    return response.json(services)

@app.get("/services/{name}")
async def get_service(
    request: Request,
    response: Response,
    name: str
):
    service = await registry.get_service(name)
    
    if not service:
        return response.json({
            "error": "Service not found"
        }, status_code=404)
    
    return response.json({
        "version": service.version,
        "url": service.url,
        "status": service.status
    })

# Start health checks
@app.on_event("startup")
async def startup():
    asyncio.create_task(registry.check_health())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

## Message Queue

```python
from nexios import NexiosApp
from nexios.http import Request, Response
import aioredis
import json
import asyncio
from typing import Dict, List, Any, Callable
import logging
from datetime import datetime

class MessageQueue:
    def __init__(self, redis_url: str):
        self.redis = aioredis.from_url(redis_url)
        self.logger = logging.getLogger("queue")
        self.handlers: Dict[str, List[Callable]] = {}
    
    async def publish(
        self,
        topic: str,
        message: Dict[str, Any]
    ):
        """Publish message to topic"""
        data = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "topic": topic,
            "data": message
        }
        
        await self.redis.rpush(
            f"queue:{topic}",
            json.dumps(data)
        )
        
        self.logger.info(
            f"Published to {topic}: {data['id']}"
        )
    
    async def subscribe(
        self,
        topic: str,
        handler: Callable
    ):
        """Subscribe to topic"""
        if topic not in self.handlers:
            self.handlers[topic] = []
        
        self.handlers[topic].append(handler)
        
        self.logger.info(
            f"Subscribed to {topic}"
        )
    
    async def start_consuming(self):
        """Start consuming messages"""
        while True:
            for topic in self.handlers:
                try:
                    # Get message
                    data = await self.redis.blpop(
                        f"queue:{topic}",
                        timeout=1
                    )
                    
                    if not data:
                        continue
                    
                    # Parse message
                    message = json.loads(data[1])
                    
                    # Call handlers
                    for handler in self.handlers[topic]:
                        try:
                            await handler(message)
                        except Exception as e:
                            self.logger.error(
                                f"Handler error: {str(e)}",
                                exc_info=True
                            )
                
                except Exception as e:
                    self.logger.error(
                        f"Consumer error: {str(e)}",
                        exc_info=True
                    )
            
            await asyncio.sleep(0.1)

# Example usage
queue = MessageQueue("redis://localhost")

# Order service
async def handle_order_created(message: Dict[str, Any]):
    order = message["data"]
    # Process order...
    print(f"Processing order: {order['id']}")

# Start consumer
@app.on_event("startup")
async def startup():
    await queue.subscribe("order.created", handle_order_created)
    asyncio.create_task(queue.start_consuming())

# Publish message
@app.post("/orders")
async def create_order(request: Request, response: Response):
    data = await request.json()
    
    # Create order...
    order = {
        "id": str(uuid.uuid4()),
        "items": data["items"],
        "total": 100.00
    }
    
    # Publish event
    await queue.publish(
        "order.created",
        order
    )
    
    return response.json(order, status_code=201)
```

## API Gateway

```python
from nexios import NexiosApp
from nexios.http import Request, Response
import aiohttp
import asyncio
from typing import Dict, Optional
import jwt
import time
import logging

class Gateway:
    def __init__(
        self,
        registry_url: str,
        jwt_secret: str
    ):
        self.registry_url = registry_url
        self.jwt_secret = jwt_secret
        self.logger = logging.getLogger("gateway")
        
        # Service cache
        self.services: Dict[str, Dict] = {}
        self.last_update = 0
    
    async def get_service(self, name: str) -> Optional[Dict]:
        """Get service URL with caching"""
        now = time.time()
        
        # Update cache if needed
        if now - self.last_update > 30:
            await self.update_services()
        
        return self.services.get(name)
    
    async def update_services(self):
        """Update service cache"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.registry_url}/services"
                ) as response:
                    self.services = await response.json()
                    self.last_update = time.time()
        except Exception as e:
            self.logger.error(
                f"Registry error: {str(e)}",
                exc_info=True
            )
    
    async def route_request(
        self,
        service: str,
        request: Request,
        **kwargs
    ) -> Response:
        """Route request to service"""
        # Get service
        service_info = await self.get_service(service)
        if not service_info:
            return Response(
                json={"error": "Service not found"},
                status_code=404
            )
        
        # Forward request
        url = f"{service_info['url']}{request.url.path}"
        
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
            self.logger.error(
                f"Routing error: {str(e)}",
                exc_info=True
            )
            return Response(
                json={"error": "Service unavailable"},
                status_code=503
            )
    
    def verify_token(
        self,
        token: str
    ) -> Optional[Dict]:
        """Verify JWT token"""
        try:
            return jwt.decode(
                token,
                self.jwt_secret,
                algorithms=["HS256"]
            )
        except jwt.InvalidTokenError:
            return None

# Create gateway app
app = NexiosApp()
gateway = Gateway(
    registry_url="http://localhost:8001",
    jwt_secret="your-secret-key"
)

# Authentication middleware
@app.middleware("http")
async def auth_middleware(
    request: Request,
    response: Response,
    call_next: Callable
):
    # Check protected routes
    protected = request.url.path.startswith("/api/")
    
    if protected:
        # Verify token
        token = request.headers.get("Authorization")
        if not token:
            return response.json({
                "error": "Authentication required"
            }, status_code=401)
        
        payload = gateway.verify_token(token)
        if not payload:
            return response.json({
                "error": "Invalid token"
            }, status_code=401)
        
        request.state.user = payload
    
    return await call_next()

# Routes
@app.get("/api/users/{user_id}")
async def get_user(
    request: Request,
    response: Response,
    user_id: int
):
    return await gateway.route_request(
        "user-service",
        request
    )

@app.post("/api/orders")
async def create_order(
    request: Request,
    response: Response
):
    # Add user ID from token
    data = await request.json()
    data["user_id"] = request.state.user["id"]
    
    return await gateway.route_request(
        "order-service",
        request,
        json=data
    )

@app.get("/api/products")
async def list_products(
    request: Request,
    response: Response
):
    return await gateway.route_request(
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
    
    # Get service
    service_info = await gateway.get_service(service)
    if not service_info:
        await websocket.close(1003, "Service unavailable")
        return
    
    # Connect to service
    service_ws = await websocket.connect(
        f"{service_info['url']}/ws"
    )
    
    try:
        # Forward messages
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Mini-Project: E-commerce Microservices

Create a complete e-commerce system with these services:

1. User Service (Authentication & Profiles)
2. Product Service (Catalog & Inventory)
3. Order Service (Orders & Payments)
4. Cart Service (Shopping Cart)
5. Notification Service (Emails & Notifications)

Each service should:
- Have its own database
- Use message queue for events
- Implement health checks
- Include monitoring
- Handle failures gracefully
- Scale independently

The services should communicate through:
- REST APIs (synchronous)
- Message Queue (asynchronous)
- WebSockets (real-time)

## Key Concepts Learned

- Service Architecture
- Inter-service Communication
- Service Registry
- Message Queues
- API Gateway
- Load Balancing
- Service Discovery
- Fault Tolerance
- Monitoring

## Additional Resources

- [Microservices.io](https://microservices.io/)
- [Martin Fowler's Blog](https://martinfowler.com/articles/microservices.html)
- [The Twelve-Factor App](https://12factor.net/)
- [Kong API Gateway](https://konghq.com/kong/)

## Homework

1. Build User Service:
   - Authentication
   - Profile management
   - Role-based access
   - Event publishing

2. Build Product Service:
   - Product catalog
   - Inventory management
   - Search functionality
   - Cache integration

3. Build Order Service:
   - Order processing
   - Payment integration
   - Event handling
   - Status tracking

## Next Steps

Tomorrow, we'll explore [Day 16: Testing Microservices](../day16/index.md). 