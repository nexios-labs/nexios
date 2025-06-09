# Day 18: Service Mesh

Welcome to Day 18! Today we'll learn about implementing a service mesh for our microservices architecture.

## Understanding Service Mesh

Key aspects:
- Service Discovery
- Load Balancing
- Circuit Breaking
- Retry Logic
- Rate Limiting
- Traffic Management
- Security
- Observability
- Configuration

## Service Mesh Implementation

```python
from nexios import NexiosApp
from nexios.http import Request, Response
import aiohttp
import asyncio
from typing import Dict, List, Any, Optional
import time
import jwt
import logging
from dataclasses import dataclass
import uuid
import ssl
import json
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class ServiceConfig:
    name: str
    url: str
    health_check: str
    circuit_timeout: float = 60.0
    retry_count: int = 3
    retry_delay: float = 1.0
    rate_limit: int = 100
    timeout: float = 30.0

class ServiceMesh:
    def __init__(self):
        self.services: Dict[str, List[ServiceConfig]] = {}
        self.circuit_states: Dict[str, CircuitState] = {}
        self.failure_counts: Dict[str, int] = {}
        self.last_failures: Dict[str, float] = {}
        self.rate_limits: Dict[str, List[float]] = {}
        self.logger = logging.getLogger("mesh")
    
    async def register_service(
        self,
        service: ServiceConfig
    ):
        """Register a service"""
        if service.name not in self.services:
            self.services[service.name] = []
        
        self.services[service.name].append(service)
        self.circuit_states[service.url] = CircuitState.CLOSED
        self.failure_counts[service.url] = 0
        self.rate_limits[service.url] = []
        
        self.logger.info(
            f"Registered service: {service.name} at {service.url}"
        )
    
    async def get_service(
        self,
        name: str
    ) -> Optional[ServiceConfig]:
        """Get service instance with load balancing"""
        if name not in self.services:
            return None
        
        # Get healthy services
        healthy = [
            s for s in self.services[name]
            if self.circuit_states[s.url] != CircuitState.OPEN
        ]
        
        if not healthy:
            return None
        
        # Round-robin selection
        service = healthy[0]
        self.services[name].append(
            self.services[name].pop(0)
        )
        
        return service
    
    async def call_service(
        self,
        service: ServiceConfig,
        method: str,
        path: str,
        **kwargs
    ) -> aiohttp.ClientResponse:
        """Call service with circuit breaking and retries"""
        # Check circuit breaker
        if not await self._can_execute(service):
            raise Exception(f"Circuit is OPEN for {service.url}")
        
        # Check rate limit
        if not self._check_rate_limit(service):
            raise Exception(f"Rate limit exceeded for {service.url}")
        
        # Add tracing headers
        headers = kwargs.get("headers", {})
        headers["X-Request-ID"] = str(uuid.uuid4())
        kwargs["headers"] = headers
        
        # Setup timeout
        timeout = aiohttp.ClientTimeout(total=service.timeout)
        
        # Try with retries
        for attempt in range(service.retry_count):
            try:
                async with aiohttp.ClientSession(
                    timeout=timeout
                ) as session:
                    async with session.request(
                        method,
                        f"{service.url}{path}",
                        **kwargs
                    ) as response:
                        # Success
                        if response.status < 500:
                            await self._on_success(service)
                            return response
                        
                        # Server error
                        await self._on_failure(service)
                        
                        if attempt < service.retry_count - 1:
                            await asyncio.sleep(
                                service.retry_delay * (attempt + 1)
                            )
                        
            except Exception as e:
                await self._on_failure(service)
                
                if attempt < service.retry_count - 1:
                    await asyncio.sleep(
                        service.retry_delay * (attempt + 1)
                    )
                else:
                    raise
        
        raise Exception(f"All retries failed for {service.url}")
    
    async def _can_execute(
        self,
        service: ServiceConfig
    ) -> bool:
        """Check if execution is allowed"""
        state = self.circuit_states[service.url]
        
        if state == CircuitState.CLOSED:
            return True
        
        if state == CircuitState.OPEN:
            # Check if timeout has passed
            if (
                time.time() - self.last_failures[service.url] >
                service.circuit_timeout
            ):
                self.circuit_states[service.url] = (
                    CircuitState.HALF_OPEN
                )
                self.logger.info(
                    f"Circuit HALF-OPEN for {service.url}"
                )
                return True
            return False
        
        # HALF_OPEN
        return True
    
    async def _on_success(self, service: ServiceConfig):
        """Handle successful call"""
        if (
            self.circuit_states[service.url] ==
            CircuitState.HALF_OPEN
        ):
            self.circuit_states[service.url] = CircuitState.CLOSED
            self.failure_counts[service.url] = 0
            self.logger.info(
                f"Circuit CLOSED for {service.url}"
            )
    
    async def _on_failure(self, service: ServiceConfig):
        """Handle failed call"""
        self.failure_counts[service.url] += 1
        self.last_failures[service.url] = time.time()
        
        if (
            self.circuit_states[service.url] ==
            CircuitState.CLOSED and
            self.failure_counts[service.url] >= 5
        ):
            self.circuit_states[service.url] = CircuitState.OPEN
            self.logger.warning(
                f"Circuit OPEN for {service.url}"
            )
        
        if (
            self.circuit_states[service.url] ==
            CircuitState.HALF_OPEN
        ):
            self.circuit_states[service.url] = CircuitState.OPEN
            self.logger.warning(
                f"Circuit OPEN for {service.url}"
            )
    
    def _check_rate_limit(
        self,
        service: ServiceConfig
    ) -> bool:
        """Check rate limit"""
        now = time.time()
        window = self.rate_limits[service.url]
        
        # Remove old requests
        while window and now - window[0] > 60:
            window.pop(0)
        
        # Check limit
        if len(window) >= service.rate_limit:
            return False
        
        # Add request
        window.append(now)
        return True
    
    async def check_health(self):
        """Check health of all services"""
        while True:
            for services in self.services.values():
                for service in services:
                    try:
                        async with aiohttp.ClientSession() as session:
                            async with session.get(
                                f"{service.url}{service.health_check}"
                            ) as response:
                                if response.status != 200:
                                    await self._on_failure(service)
                                else:
                                    await self._on_success(service)
                    except:
                        await self._on_failure(service)
            
            await asyncio.sleep(30)

# Example usage
mesh = ServiceMesh()

# Register services
await mesh.register_service(ServiceConfig(
    name="user-service",
    url="http://localhost:8001",
    health_check="/health",
    circuit_timeout=60.0,
    retry_count=3,
    retry_delay=1.0,
    rate_limit=100,
    timeout=30.0
))

await mesh.register_service(ServiceConfig(
    name="order-service",
    url="http://localhost:8002",
    health_check="/health",
    circuit_timeout=60.0,
    retry_count=3,
    retry_delay=1.0,
    rate_limit=100,
    timeout=30.0
))

# Start health checks
asyncio.create_task(mesh.check_health())

# Example API Gateway using Service Mesh
class Gateway:
    def __init__(
        self,
        mesh: ServiceMesh,
        jwt_secret: str
    ):
        self.mesh = mesh
        self.jwt_secret = jwt_secret
        self.logger = logging.getLogger("gateway")
    
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
    
    async def route_request(
        self,
        service_name: str,
        request: Request,
        **kwargs
    ) -> Response:
        """Route request through service mesh"""
        # Get service
        service = await self.mesh.get_service(service_name)
        if not service:
            return Response(
                json={"error": "Service unavailable"},
                status_code=503
            )
        
        try:
            # Call service
            response = await self.mesh.call_service(
                service,
                request.method,
                request.url.path,
                **kwargs
            )
            
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
                json={"error": str(e)},
                status_code=503
            )

# Create gateway
app = NexiosApp()
gateway = Gateway(mesh, "your-secret-key")

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
    data = await request.json()
    data["user_id"] = request.state.user["id"]
    
    return await gateway.route_request(
        "order-service",
        request,
        json=data
    )

# WebSocket proxy
@app.websocket("/ws/{service}")
async def websocket_proxy(
    websocket: WebSocket,
    service: str
):
    await websocket.accept()
    
    # Get service
    service_config = await mesh.get_service(service)
    if not service_config:
        await websocket.close(1003, "Service unavailable")
        return
    
    try:
        # Connect to service
        service_ws = await websocket.connect(
            f"{service_config.url}/ws"
        )
        
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
        self.logger.error(
            f"WebSocket error: {str(e)}",
            exc_info=True
        )
    
    finally:
        await websocket.close()
        await service_ws.close()

# Metrics endpoint
@app.get("/metrics")
async def get_metrics(request: Request, response: Response):
    metrics = {
        "services": {},
        "circuits": {},
        "rate_limits": {}
    }
    
    for name, services in mesh.services.items():
        metrics["services"][name] = [
            {
                "url": s.url,
                "status": mesh.circuit_states[s.url].value,
                "failures": mesh.failure_counts[s.url],
                "rate_limit": {
                    "current": len(mesh.rate_limits[s.url]),
                    "limit": s.rate_limit
                }
            }
            for s in services
        ]
    
    return response.json(metrics)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Service Mesh Configuration

```yaml
# mesh-config.yml
mesh:
  services:
    user-service:
      instances:
        - url: http://localhost:8001
          health_check: /health
          circuit_timeout: 60.0
          retry_count: 3
          retry_delay: 1.0
          rate_limit: 100
          timeout: 30.0
        - url: http://localhost:8011
          health_check: /health
          circuit_timeout: 60.0
          retry_count: 3
          retry_delay: 1.0
          rate_limit: 100
          timeout: 30.0
    
    order-service:
      instances:
        - url: http://localhost:8002
          health_check: /health
          circuit_timeout: 60.0
          retry_count: 3
          retry_delay: 1.0
          rate_limit: 100
          timeout: 30.0
        - url: http://localhost:8012
          health_check: /health
          circuit_timeout: 60.0
          retry_count: 3
          retry_delay: 1.0
          rate_limit: 100
          timeout: 30.0
    
    product-service:
      instances:
        - url: http://localhost:8003
          health_check: /health
          circuit_timeout: 60.0
          retry_count: 3
          retry_delay: 1.0
          rate_limit: 100
          timeout: 30.0
        - url: http://localhost:8013
          health_check: /health
          circuit_timeout: 60.0
          retry_count: 3
          retry_delay: 1.0
          rate_limit: 100
          timeout: 30.0

  security:
    jwt_secret: your-secret-key
    ssl:
      enabled: true
      cert_file: certs/server.crt
      key_file: certs/server.key
    
    cors:
      enabled: true
      allow_origins:
        - http://localhost:3000
        - https://example.com
      allow_methods:
        - GET
        - POST
        - PUT
        - DELETE
      allow_headers:
        - Authorization
        - Content-Type
    
    rate_limiting:
      enabled: true
      default_limit: 100
      window: 60
    
    authentication:
      enabled: true
      protected_paths:
        - /api/
        - /admin/
  
  observability:
    metrics:
      enabled: true
      path: /metrics
      interval: 15
    
    tracing:
      enabled: true
      jaeger_host: localhost
      jaeger_port: 6831
    
    logging:
      level: INFO
      format: json
      output: stdout
  
  resilience:
    circuit_breaker:
      enabled: true
      failure_threshold: 5
      timeout: 60.0
    
    retry:
      enabled: true
      max_attempts: 3
      delay: 1.0
    
    timeout:
      enabled: true
      default: 30.0
  
  load_balancing:
    strategy: round_robin
    health_check:
      enabled: true
      interval: 30
      timeout: 5
```

## Mini-Project: Service Mesh Dashboard

Create a dashboard to monitor and manage the service mesh:

1. Service Overview:
   - Service status
   - Instance health
   - Circuit breaker status
   - Rate limiting metrics

2. Traffic Management:
   - Request routing
   - Load balancing
   - Circuit breaker controls
   - Rate limit configuration

3. Security:
   - Authentication status
   - SSL certificates
   - CORS settings
   - Rate limit violations

4. Observability:
   - Service metrics
   - Trace visualization
   - Log aggregation
   - Health check results

## Key Concepts Learned

- Service Mesh Architecture
- Traffic Management
- Circuit Breaking
- Rate Limiting
- Load Balancing
- Service Discovery
- Security
- Observability
- Configuration
- Resilience

## Additional Resources

- [Istio Documentation](https://istio.io/latest/docs/)
- [Linkerd Documentation](https://linkerd.io/2.11/overview/)
- [Consul Documentation](https://www.consul.io/docs)
- [Envoy Documentation](https://www.envoyproxy.io/docs)

## Homework

1. Implement Service Mesh:
   - Service discovery
   - Load balancing
   - Circuit breaking
   - Rate limiting

2. Create Management UI:
   - Service status
   - Configuration
   - Metrics
   - Controls

3. Add Security Features:
   - Authentication
   - Authorization
   - SSL/TLS
   - CORS

## Next Steps

Tomorrow, we'll explore [Day 19: API Gateway](../day19/index.md). 