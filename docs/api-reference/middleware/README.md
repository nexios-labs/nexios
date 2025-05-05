# Middleware API Reference

## Basic Structure
```python
async def middleware(req: Request, res: Response, next: Callable) -> Optional[Response]:
    # Pre-processing logic here
    await next()  # Pass to next middleware/handler
    # Post-processing logic here
```

## Key Methods

### 1. Application Middleware
```python
app.add_middleware(middleware_func)  # Global middleware
```

### 2. Route-Specific Middleware
```python
@app.route("/path", "GET", middlewares=[mw1, mw2])
async def handler(req, res): ...
```

### 3. Router Middleware
```python
router = Router()
router.add_middleware(mw1)  # Applies to all routes in this router
```

### 4. Class-Based Middleware
```python
class AuthMiddleware(BaseMiddleware):
    async def process_request(self, req, res, cnext):
        # Pre-processing
        await cnext(req, res)
    
    async def process_response(self, req, res):
        # Post-processing
        return res
```

## Execution Flow
1. Middleware executes in registration order
2. Each middleware can:
   - Modify `req` before handler
   - Modify `res` after handler
   - Short-circuit by returning early

## Common Patterns

### Authentication
```python
async def auth_middleware(req, res, next):
    if not req.headers.get("Authorization"):
        return res.status(401).json({"error": "Unauthorized"})
    await next()
```

### Logging
```python
async def logger_middleware(req, res, next):
    start = time.time()
    await next()
    duration = time.time() - start
    print(f"{req.method} {req.path} - {res.status_code} ({duration:.2f}s)")
```

### Error Handling
```python
async def error_middleware(req, res, next):
    try:
        await next()
    except Exception as e:
        return res.status(500).json({"error": str(e)})
```