# Day 17: Monitoring and Observability

Welcome to Day 17! Today we'll learn about monitoring and observability in microservices.

## Understanding Observability

Key aspects:
- Metrics
- Logging
- Tracing
- Alerting
- Dashboards
- Health Checks
- Performance Monitoring
- Error Tracking
- Service Dependencies

## Metrics Collection

```python
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Summary,
    Info,
    generate_latest
)
import time
from typing import Dict, Any
import psutil
import os

class Metrics:
    def __init__(self, service_name: str):
        # Request metrics
        self.request_count = Counter(
            "request_total",
            "Total request count",
            ["method", "endpoint", "status"]
        )
        
        self.request_latency = Histogram(
            "request_latency_seconds",
            "Request latency in seconds",
            ["method", "endpoint"],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
        )
        
        # Business metrics
        self.active_users = Gauge(
            "active_users",
            "Number of active users"
        )
        
        self.order_value = Summary(
            "order_value_dollars",
            "Order value in dollars"
        )
        
        # System metrics
        self.cpu_usage = Gauge(
            "cpu_usage_percent",
            "CPU usage percentage"
        )
        
        self.memory_usage = Gauge(
            "memory_usage_bytes",
            "Memory usage in bytes"
        )
        
        # Service info
        self.info = Info(
            "service",
            "Service information"
        )
        self.info.info({
            "name": service_name,
            "version": os.getenv("VERSION", "unknown"),
            "python_version": os.getenv("PYTHON_VERSION", "unknown")
        })
    
    def track_request(
        self,
        method: str,
        endpoint: str,
        status: int,
        duration: float
    ):
        """Track request metrics"""
        self.request_count.labels(
            method=method,
            endpoint=endpoint,
            status=status
        ).inc()
        
        self.request_latency.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    def update_system_metrics(self):
        """Update system metrics"""
        self.cpu_usage.set(psutil.cpu_percent())
        self.memory_usage.set(psutil.Process().memory_info().rss)
    
    def set_active_users(self, count: int):
        """Set active users count"""
        self.active_users.set(count)
    
    def observe_order(self, value: float):
        """Observe order value"""
        self.order_value.observe(value)
    
    def get_metrics(self) -> bytes:
        """Get all metrics"""
        return generate_latest()

# Middleware for request tracking
async def metrics_middleware(
    request: Request,
    response: Response,
    call_next: Callable,
    metrics: Metrics
):
    start_time = time.time()
    
    try:
        response = await call_next()
        
        duration = time.time() - start_time
        metrics.track_request(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code,
            duration=duration
        )
        
        return response
        
    except Exception as e:
        duration = time.time() - start_time
        metrics.track_request(
            method=request.method,
            endpoint=request.url.path,
            status=500,
            duration=duration
        )
        raise

# Background task for system metrics
async def update_system_metrics(metrics: Metrics):
    """Update system metrics periodically"""
    while True:
        metrics.update_system_metrics()
        await asyncio.sleep(15)  # Every 15 seconds

# Example usage
metrics = Metrics("user-service")

@app.on_event("startup")
async def startup():
    # Start system metrics collection
    asyncio.create_task(
        update_system_metrics(metrics)
    )

@app.get("/metrics")
async def get_metrics(request: Request, response: Response):
    return response.raw(
        metrics.get_metrics(),
        media_type="text/plain"
    )
```

## Structured Logging

```python
import logging
import json
from datetime import datetime
import traceback
from typing import Dict, Any, Optional
import sys
import contextvars

request_id = contextvars.ContextVar("request_id")

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        # Base log data
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add request ID if available
        try:
            log_data["request_id"] = request_id.get()
        except LookupError:
            pass
        
        # Add extra fields
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "stacktrace": traceback.format_exception(
                    *record.exc_info
                )
            }
        
        return json.dumps(log_data)

class StructuredLogger:
    def __init__(
        self,
        name: str,
        level: str = "INFO"
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Add JSON handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        self.logger.addHandler(handler)
    
    def log(
        self,
        level: str,
        message: str,
        extra: Dict[str, Any] = None
    ):
        """Log message with extra data"""
        self.logger.log(
            getattr(logging, level),
            message,
            extra={"extra": extra or {}}
        )
    
    def info(self, message: str, **kwargs):
        self.log("INFO", message, kwargs)
    
    def error(self, message: str, **kwargs):
        self.log("ERROR", message, kwargs)
    
    def warning(self, message: str, **kwargs):
        self.log("WARNING", message, kwargs)
    
    def debug(self, message: str, **kwargs):
        self.log("DEBUG", message, kwargs)

# Logging middleware
async def logging_middleware(
    request: Request,
    response: Response,
    call_next: Callable,
    logger: StructuredLogger
):
    # Generate request ID
    req_id = str(uuid.uuid4())
    request_id.set(req_id)
    
    # Log request
    logger.info(
        "Request started",
        method=request.method,
        path=request.url.path,
        query=dict(request.query_params),
        client_ip=request.client.host,
        request_id=req_id
    )
    
    try:
        start_time = time.time()
        response = await call_next()
        duration = time.time() - start_time
        
        # Log response
        logger.info(
            "Request completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration=duration,
            request_id=req_id
        )
        
        return response
        
    except Exception as e:
        # Log error
        logger.error(
            "Request failed",
            method=request.method,
            path=request.url.path,
            error=str(e),
            traceback=traceback.format_exc(),
            request_id=req_id
        )
        raise

# Example usage
logger = StructuredLogger("user-service")

@app.post("/users")
async def create_user(request: Request, response: Response):
    try:
        data = await request.json()
        
        logger.info(
            "Creating user",
            email=data["email"]
        )
        
        # Create user...
        
        logger.info(
            "User created",
            user_id=user.id,
            email=user.email
        )
        
        return response.json(user)
        
    except Exception as e:
        logger.error(
            "User creation failed",
            error=str(e)
        )
        raise
```

## Distributed Tracing

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter
)
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from typing import Optional, Dict, Any
import asyncio
import aiohttp
import time

class Tracer:
    def __init__(
        self,
        service_name: str,
        jaeger_host: str = "localhost",
        jaeger_port: int = 6831
    ):
        # Setup provider
        provider = TracerProvider()
        
        # Console exporter
        console_processor = BatchSpanProcessor(
            ConsoleSpanExporter()
        )
        provider.add_span_processor(console_processor)
        
        # Jaeger exporter
        jaeger_exporter = JaegerExporter(
            agent_host_name=jaeger_host,
            agent_port=jaeger_port
        )
        jaeger_processor = BatchSpanProcessor(
            jaeger_exporter
        )
        provider.add_span_processor(jaeger_processor)
        
        # Set global provider
        trace.set_tracer_provider(provider)
        
        # Get tracer
        self.tracer = trace.get_tracer(service_name)
        
        # Instrument libraries
        RequestsInstrumentor().instrument()
        AioHttpClientInstrumentor().instrument()
        AsyncPGInstrumentor().instrument()
    
    async def trace_request(
        self,
        request: Request,
        response: Response,
        call_next: Callable
    ):
        """Trace HTTP request"""
        with self.tracer.start_as_current_span(
            name=f"{request.method} {request.url.path}",
            kind=trace.SpanKind.SERVER,
            attributes={
                "http.method": request.method,
                "http.url": str(request.url),
                "http.route": request.url.path
            }
        ) as span:
            try:
                response = await call_next()
                
                # Add response attributes
                span.set_attribute(
                    "http.status_code",
                    response.status_code
                )
                
                return response
                
            except Exception as e:
                # Record error
                span.record_exception(e)
                span.set_status(
                    trace.Status(
                        trace.StatusCode.ERROR,
                        str(e)
                    )
                )
                raise
    
    async def trace_operation(
        self,
        name: str,
        kind: trace.SpanKind = trace.SpanKind.INTERNAL,
        attributes: Dict[str, Any] = None
    ):
        """Create trace span"""
        return self.tracer.start_span(
            name=name,
            kind=kind,
            attributes=attributes
        )

# Example usage
tracer = Tracer("user-service")

@app.post("/orders")
async def create_order(request: Request, response: Response):
    data = await request.json()
    
    with tracer.trace_operation(
        "create_order",
        attributes={"user_id": data["user_id"]}
    ) as span:
        try:
            # Check inventory
            with tracer.trace_operation(
                "check_inventory",
                kind=trace.SpanKind.CLIENT
            ) as inventory_span:
                inventory_result = await check_inventory(
                    data["items"]
                )
                inventory_span.set_attribute(
                    "items_count",
                    len(data["items"])
                )
            
            # Process payment
            with tracer.trace_operation(
                "process_payment",
                kind=trace.SpanKind.CLIENT
            ) as payment_span:
                payment_result = await process_payment(
                    data["payment"]
                )
                payment_span.set_attribute(
                    "amount",
                    payment_result["amount"]
                )
            
            # Create order
            with tracer.trace_operation(
                "save_order",
                kind=trace.SpanKind.CLIENT
            ) as db_span:
                order = await save_order(data)
                db_span.set_attribute(
                    "order_id",
                    order["id"]
                )
            
            return response.json(order)
            
        except Exception as e:
            span.record_exception(e)
            span.set_status(
                trace.Status(
                    trace.StatusCode.ERROR,
                    str(e)
                )
            )
            raise
```

## Health Checks

```python
from enum import Enum
from typing import Dict, Any, List
import aiohttp
import asyncpg
import aioredis
import time

class HealthStatus(Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"

class HealthCheck:
    def __init__(self):
        self.checks: Dict[str, Callable] = {}
    
    def add_check(
        self,
        name: str,
        check: Callable
    ):
        """Add health check"""
        self.checks[name] = check
    
    async def check_health(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {}
        status = HealthStatus.HEALTHY
        
        for name, check in self.checks.items():
            try:
                start_time = time.time()
                check_result = await check()
                duration = time.time() - start_time
                
                results[name] = {
                    "status": check_result["status"].value,
                    "details": check_result.get("details", {}),
                    "duration": duration
                }
                
                if check_result["status"] == HealthStatus.UNHEALTHY:
                    status = HealthStatus.UNHEALTHY
                elif (
                    check_result["status"] == HealthStatus.DEGRADED and
                    status != HealthStatus.UNHEALTHY
                ):
                    status = HealthStatus.DEGRADED
                
            except Exception as e:
                results[name] = {
                    "status": HealthStatus.UNHEALTHY.value,
                    "error": str(e)
                }
                status = HealthStatus.UNHEALTHY
        
        return {
            "status": status.value,
            "checks": results,
            "timestamp": datetime.utcnow().isoformat()
        }

# Example health checks
async def check_database(db_pool: asyncpg.Pool):
    """Check database connection"""
    try:
        async with db_pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
            
            return {
                "status": HealthStatus.HEALTHY,
                "details": {
                    "pool_size": db_pool.get_size(),
                    "active_connections": db_pool.get_active_size()
                }
            }
    except Exception as e:
        return {
            "status": HealthStatus.UNHEALTHY,
            "details": {"error": str(e)}
        }

async def check_redis(redis: aioredis.Redis):
    """Check Redis connection"""
    try:
        await redis.ping()
        info = await redis.info()
        
        return {
            "status": HealthStatus.HEALTHY,
            "details": {
                "used_memory": info["used_memory"],
                "connected_clients": info["connected_clients"]
            }
        }
    except Exception as e:
        return {
            "status": HealthStatus.UNHEALTHY,
            "details": {"error": str(e)}
        }

async def check_dependencies(
    registry_url: str
) -> Dict[str, Any]:
    """Check service dependencies"""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                f"{registry_url}/health"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "status": HealthStatus.HEALTHY,
                        "details": data
                    }
                else:
                    return {
                        "status": HealthStatus.UNHEALTHY,
                        "details": {
                            "status_code": response.status
                        }
                    }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "details": {"error": str(e)}
            }

# Example usage
health = HealthCheck()

@app.on_event("startup")
async def startup():
    # Add health checks
    health.add_check(
        "database",
        lambda: check_database(app.state.db)
    )
    health.add_check(
        "redis",
        lambda: check_redis(app.state.redis)
    )
    health.add_check(
        "registry",
        lambda: check_dependencies(app.config.registry_url)
    )

@app.get("/health")
async def health_check(request: Request, response: Response):
    result = await health.check_health()
    
    return response.json(
        result,
        status_code=200 if
        result["status"] != HealthStatus.UNHEALTHY.value
        else 503
    )
```

## Mini-Project: Monitoring Dashboard

Create a monitoring dashboard that displays:

1. Service Health:
   - Status of all services
   - Response times
   - Error rates
   - Resource usage

2. Business Metrics:
   - Active users
   - Order volume
   - Revenue
   - Conversion rates

3. System Metrics:
   - CPU usage
   - Memory usage
   - Network I/O
   - Disk usage

4. Logs and Traces:
   - Log search
   - Trace visualization
   - Error tracking
   - Performance analysis

## Key Concepts Learned

- Metrics Collection
- Structured Logging
- Distributed Tracing
- Health Checks
- Performance Monitoring
- Error Tracking
- Alerting
- Visualization
- System Metrics
- Business Metrics

## Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [ELK Stack Documentation](https://www.elastic.co/guide/index.html)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)

## Homework

1. Setup Monitoring:
   - Prometheus
   - Grafana
   - ELK Stack
   - Jaeger

2. Create Dashboards:
   - Service metrics
   - Business metrics
   - System metrics
   - Logs and traces

3. Implement Alerting:
   - Service health
   - Performance issues
   - Error rates
   - Resource usage

## Next Steps

Tomorrow, we'll explore [Day 18: Service Mesh](../day18/index.md). 