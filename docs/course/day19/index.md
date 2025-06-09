# Day 19: API Gateway

Welcome to Day 19! Today we'll learn about implementing an API Gateway for our microservices architecture.

## Understanding API Gateway

Key aspects:
- Request Routing
- Authentication
- Authorization
- Rate Limiting
- Request/Response Transformation
- Caching
- API Documentation
- Monitoring
- Security
- Version Management

## API Gateway Implementation

```python
from nexios import NexiosApp
from nexios.http import Request, Response
import aiohttp
import asyncio
from typing import Dict, List, Any, Optional
import jwt
import time
import logging
from dataclasses import dataclass
import uuid
import json
from enum import Enum
import yaml
import aioredis
from openapi_spec_validator import validate_spec
import prometheus_client
from prometheus_client import Counter, Histogram

@dataclass
class RouteConfig:
    service: str
    path: str
    methods: List[str]
    auth_required: bool = False
    rate_limit: Optional[int] = None
    cache_ttl: Optional[int] = None
    transform_request: Optional[Dict] = None
    transform_response: Optional[Dict] = None

@dataclass
class ServiceConfig:
    name: str
    url: str
    version: str
    health_check: str
    timeout: float = 30.0

class APIGateway:
    def __init__(
        self,
        config_file: str,
        redis_url: str
    ):
        # Load configuration
        with open(config_file) as f:
            self.config = yaml.safe_load(f)
        
        # Setup components
        self.routes: Dict[str, RouteConfig] = {}
        self.services: Dict[str, List[ServiceConfig]] = {}
        self.cache = aioredis.from_url(redis_url)
        self.logger = logging.getLogger("gateway")
        
        # Setup metrics
        self.request_count = Counter(
            "gateway_requests_total",
            "Total request count",
            ["method", "path", "status"]
        )
        
        self.request_latency = Histogram(
            "gateway_request_latency_seconds",
            "Request latency in seconds",
            ["method", "path"]
        )
        
        # Load routes and services
        self._load_routes()
        self._load_services()
        
        # Validate OpenAPI spec
        self._validate_openapi()
    
    def _load_routes(self):
        """Load route configuration"""
        for route in self.config["routes"]:
            self.routes[route["path"]] = RouteConfig(
                service=route["service"],
                path=route["path"],
                methods=route["methods"],
                auth_required=route.get("auth_required", False),
                rate_limit=route.get("rate_limit"),
                cache_ttl=route.get("cache_ttl"),
                transform_request=route.get("transform_request"),
                transform_response=route.get("transform_response")
            )
    
    def _load_services(self):
        """Load service configuration"""
        for service in self.config["services"]:
            name = service["name"]
            if name not in self.services:
                self.services[name] = []
            
            for instance in service["instances"]:
                self.services[name].append(
                    ServiceConfig(
                        name=name,
                        url=instance["url"],
                        version=instance["version"],
                        health_check=instance["health_check"],
                        timeout=instance.get("timeout", 30.0)
                    )
                )
    
    def _validate_openapi(self):
        """Validate OpenAPI specification"""
        try:
            validate_spec(self.config["openapi"])
            self.logger.info("OpenAPI spec validated")
        except Exception as e:
            self.logger.error(
                f"OpenAPI validation error: {str(e)}"
            )
    
    async def route_request(
        self,
        request: Request,
        **kwargs
    ) -> Response:
        """Route request to appropriate service"""
        start_time = time.time()
        
        try:
            # Find route
            route = self._find_route(request)
            if not route:
                return Response(
                    json={"error": "Route not found"},
                    status_code=404
                )
            
            # Check authentication
            if route.auth_required:
                user = await self._authenticate(request)
                if not user:
                    return Response(
                        json={"error": "Unauthorized"},
                        status_code=401
                    )
                request.state.user = user
            
            # Check rate limit
            if route.rate_limit:
                if not await self._check_rate_limit(
                    request,
                    route
                ):
                    return Response(
                        json={"error": "Rate limit exceeded"},
                        status_code=429
                    )
            
            # Check cache
            if (
                route.cache_ttl and
                request.method == "GET"
            ):
                cached = await self._get_cache(request)
                if cached:
                    return Response(
                        body=cached["body"],
                        headers=cached["headers"],
                        status_code=200
                    )
            
            # Transform request
            if route.transform_request:
                await self._transform_request(
                    request,
                    route.transform_request
                )
            
            # Get service
            service = await self._get_service(route.service)
            if not service:
                return Response(
                    json={"error": "Service unavailable"},
                    status_code=503
                )
            
            # Forward request
            response = await self._forward_request(
                service,
                request,
                **kwargs
            )
            
            # Transform response
            if route.transform_response:
                await self._transform_response(
                    response,
                    route.transform_response
                )
            
            # Cache response
            if (
                route.cache_ttl and
                request.method == "GET" and
                response.status_code == 200
            ):
                await self._set_cache(
                    request,
                    response,
                    route.cache_ttl
                )
            
            # Update metrics
            duration = time.time() - start_time
            self.request_count.labels(
                method=request.method,
                path=request.url.path,
                status=response.status_code
            ).inc()
            
            self.request_latency.labels(
                method=request.method,
                path=request.url.path
            ).observe(duration)
            
            return response
            
        except Exception as e:
            self.logger.error(
                f"Routing error: {str(e)}",
                exc_info=True
            )
            
            return Response(
                json={"error": "Internal server error"},
                status_code=500
            )
    
    def _find_route(
        self,
        request: Request
    ) -> Optional[RouteConfig]:
        """Find matching route"""
        for path, route in self.routes.items():
            if (
                request.url.path.startswith(path) and
                request.method in route.methods
            ):
                return route
        return None
    
    async def _authenticate(
        self,
        request: Request
    ) -> Optional[Dict]:
        """Authenticate request"""
        token = request.headers.get("Authorization")
        if not token:
            return None
        
        try:
            return jwt.decode(
                token,
                self.config["security"]["jwt_secret"],
                algorithms=["HS256"]
            )
        except jwt.InvalidTokenError:
            return None
    
    async def _check_rate_limit(
        self,
        request: Request,
        route: RouteConfig
    ) -> bool:
        """Check rate limit"""
        key = f"ratelimit:{request.client.host}:{route.path}"
        
        # Get current count
        count = await self.cache.get(key)
        count = int(count) if count else 0
        
        if count >= route.rate_limit:
            return False
        
        # Increment count
        pipe = self.cache.pipeline()
        pipe.incr(key)
        pipe.expire(key, 60)  # 1 minute window
        await pipe.execute()
        
        return True
    
    async def _get_cache(
        self,
        request: Request
    ) -> Optional[Dict]:
        """Get cached response"""
        key = f"cache:{request.url.path}"
        data = await self.cache.get(key)
        return json.loads(data) if data else None
    
    async def _set_cache(
        self,
        request: Request,
        response: Response,
        ttl: int
    ):
        """Cache response"""
        key = f"cache:{request.url.path}"
        data = {
            "body": response.body,
            "headers": dict(response.headers)
        }
        await self.cache.set(
            key,
            json.dumps(data),
            ex=ttl
        )
    
    async def _get_service(
        self,
        name: str
    ) -> Optional[ServiceConfig]:
        """Get service instance"""
        if name not in self.services:
            return None
        
        # Simple round-robin
        services = self.services[name]
        service = services[0]
        services.append(services.pop(0))
        
        return service
    
    async def _forward_request(
        self,
        service: ServiceConfig,
        request: Request,
        **kwargs
    ) -> Response:
        """Forward request to service"""
        # Setup timeout
        timeout = aiohttp.ClientTimeout(
            total=service.timeout
        )
        
        # Forward request
        async with aiohttp.ClientSession(
            timeout=timeout
        ) as session:
            url = f"{service.url}{request.url.path}"
            
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
    
    async def _transform_request(
        self,
        request: Request,
        transform: Dict
    ):
        """Transform request"""
        # Add headers
        if "headers" in transform:
            request.headers.update(transform["headers"])
        
        # Transform body
        if "body" in transform and request.body:
            data = await request.json()
            for key, value in transform["body"].items():
                if key in data:
                    data[value] = data.pop(key)
            request._body = json.dumps(data).encode()
    
    async def _transform_response(
        self,
        response: Response,
        transform: Dict
    ):
        """Transform response"""
        # Add headers
        if "headers" in transform:
            response.headers.update(transform["headers"])
        
        # Transform body
        if "body" in transform and response.body:
            data = json.loads(response.body)
            for key, value in transform["body"].items():
                if key in data:
                    data[value] = data.pop(key)
            response.body = json.dumps(data).encode()

# Create gateway app
app = NexiosApp()
gateway = APIGateway(
    "gateway-config.yml",
    "redis://localhost"
)

# Routes
@app.route("/{path:path}")
async def proxy(request: Request, response: Response):
    return await gateway.route_request(request)

# OpenAPI documentation
@app.get("/docs")
async def get_docs(request: Request, response: Response):
    return response.json(gateway.config["openapi"])

# Metrics endpoint
@app.get("/metrics")
async def get_metrics(request: Request, response: Response):
    return response.raw(
        prometheus_client.generate_latest(),
        media_type="text/plain"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Gateway Configuration

```yaml
# gateway-config.yml
routes:
  - path: /api/users
    service: user-service
    methods: [GET, POST, PUT, DELETE]
    auth_required: true
    rate_limit: 100
    cache_ttl: 300
    transform_request:
      headers:
        X-Gateway-Version: "1.0"
      body:
        username: user_name
        email: user_email
    transform_response:
      headers:
        X-Response-Time: "${response_time}"
      body:
        user_name: username
        user_email: email

  - path: /api/orders
    service: order-service
    methods: [GET, POST]
    auth_required: true
    rate_limit: 50
    transform_request:
      headers:
        X-User-ID: "${user.id}"

  - path: /api/products
    service: product-service
    methods: [GET]
    cache_ttl: 600
    transform_response:
      body:
        product_name: name
        product_price: price

services:
  - name: user-service
    instances:
      - url: http://localhost:8001
        version: "1.0"
        health_check: /health
        timeout: 30.0
      - url: http://localhost:8011
        version: "1.0"
        health_check: /health
        timeout: 30.0

  - name: order-service
    instances:
      - url: http://localhost:8002
        version: "1.0"
        health_check: /health
        timeout: 30.0
      - url: http://localhost:8012
        version: "1.0"
        health_check: /health
        timeout: 30.0

  - name: product-service
    instances:
      - url: http://localhost:8003
        version: "1.0"
        health_check: /health
        timeout: 30.0
      - url: http://localhost:8013
        version: "1.0"
        health_check: /health
        timeout: 30.0

security:
  jwt_secret: your-secret-key
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

caching:
  enabled: true
  redis_url: redis://localhost
  default_ttl: 300

rate_limiting:
  enabled: true
  redis_url: redis://localhost
  default_limit: 100
  window: 60

monitoring:
  metrics:
    enabled: true
    path: /metrics
  logging:
    level: INFO
    format: json

openapi:
  openapi: "3.0.0"
  info:
    title: API Gateway
    version: "1.0.0"
    description: API Gateway for microservices
  servers:
    - url: http://localhost:8000
      description: Local development server
  paths:
    /api/users:
      get:
        summary: List users
        security:
          - BearerAuth: []
        responses:
          200:
            description: List of users
          401:
            description: Unauthorized
          429:
            description: Rate limit exceeded
      post:
        summary: Create user
        security:
          - BearerAuth: []
        requestBody:
          required: true
          content:
            application/json:
              schema:
                type: object
                properties:
                  username:
                    type: string
                  email:
                    type: string
        responses:
          201:
            description: User created
          401:
            description: Unauthorized
          429:
            description: Rate limit exceeded
    
    /api/orders:
      get:
        summary: List orders
        security:
          - BearerAuth: []
        responses:
          200:
            description: List of orders
          401:
            description: Unauthorized
          429:
            description: Rate limit exceeded
      post:
        summary: Create order
        security:
          - BearerAuth: []
        requestBody:
          required: true
          content:
            application/json:
              schema:
                type: object
                properties:
                  items:
                    type: array
                    items:
                      type: object
                      properties:
                        product_id:
                          type: integer
                        quantity:
                          type: integer
        responses:
          201:
            description: Order created
          401:
            description: Unauthorized
          429:
            description: Rate limit exceeded
    
    /api/products:
      get:
        summary: List products
        responses:
          200:
            description: List of products
          429:
            description: Rate limit exceeded
  
  components:
    securitySchemes:
      BearerAuth:
        type: http
        scheme: bearer
        bearerFormat: JWT
```

## Mini-Project: API Gateway Dashboard

Create a dashboard to monitor and manage the API Gateway:

1. Route Management:
   - Route configuration
   - Service mapping
   - Authentication settings
   - Rate limiting rules

2. Traffic Monitoring:
   - Request volume
   - Response times
   - Error rates
   - Cache hit rates

3. Service Status:
   - Service health
   - Instance availability
   - Response times
   - Error rates

4. Security:
   - Authentication status
   - Rate limit violations
   - CORS violations
   - JWT token management

## Key Concepts Learned

- API Gateway Pattern
- Request Routing
- Authentication
- Rate Limiting
- Request/Response Transformation
- Caching
- API Documentation
- Monitoring
- Security
- Configuration

## Additional Resources

- [Kong Documentation](https://docs.konghq.com/)
- [AWS API Gateway](https://aws.amazon.com/api-gateway/)
- [Azure API Management](https://azure.microsoft.com/en-us/services/api-management/)
- [OpenAPI Specification](https://swagger.io/specification/)

## Homework

1. Implement Gateway Features:
   - Request routing
   - Authentication
   - Rate limiting
   - Caching

2. Create Management UI:
   - Route configuration
   - Service management
   - Monitoring
   - Documentation

3. Add Security Features:
   - JWT validation
   - CORS
   - Rate limiting
   - Request validation

## Next Steps

Tomorrow, we'll explore [Day 20: Event-Driven Architecture](../day20/index.md). 