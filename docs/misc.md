# Nexios Hooks

Hooks in the Nexios framework provide a way to intercept and modify request/response cycles. They allow you to execute code before or after route handlers, add analytics, implement caching, and enforce timeouts.

**Important Warnings**:

- These hooks **do not** replace proper middleware for cross-cutting concerns
- They **do not** provide security features like authentication/authorization
- They **do not** handle database transactions or connection management
- They **do not** guarantee thread safety for shared state modifications

## Available Hooks

### 1. Before Request Hook

Executes before the route handler processes the request.

```python
@before_request(
    func=my_preprocessor,
    log_level="DEBUG",
    only_methods=["POST", "PUT"],
    for_routes=["/api/users"]
)
async def my_handler(request: Request, response: Response):
    # Handler logic
```

**What it does NOT do**:

- Does not modify the incoming request body
- Does not validate request payloads
- Does not authenticate users

### 2. After Request Hook

Executes after the route handler completes but before sending the response.

```python
@after_request(
    func=my_postprocessor,
    log_level="INFO",
    only_methods=["GET"],
    for_routes=["/api/reports"]
)
async def my_handler(request: Request, response: Response):
    # Handler logic
```

**What it does NOT do**:

- Does not modify response headers after they're sent
- Does not handle response streaming
- Does not catch exceptions from the handler

### 3. Analytics Hook

Tracks request timing and basic metrics.

```python
@analytics
async def my_handler(request: Request, response: Response):
    # Handler logic
```

**What it does NOT do**:

- Does not persist analytics data
- Does not track detailed user behavior
- Does not provide performance monitoring

### 4. Response Cache Hook

Caches responses in memory using LRU strategy.

```python
@cache_response(max_size=100)
async def my_handler(request: Request, response: Response):
    # Handler logic
```

**What it does NOT do**:

- Does not invalidate cache automatically
- Does not support distributed caching
- Does not respect cache-control headers

### 5. Request Timeout Hook

Enforces maximum execution time for handlers.

```python
@request_timeout(timeout=30)
async def my_handler(request: Request, response: Response):
    # Handler logic
```

**What it does NOT do**:

- Does not cancel background tasks
- Does not handle resource cleanup
- Does not work with streaming responses

## Best Practices

1. **Use hooks for simple, route-specific logic** - Keep hook logic minimal and focused
2. **Combine with middleware for complex cases** - Use middleware for cross-cutting concerns
3. **Avoid state modification** - Hooks should generally be stateless
4. **Document hook usage** - Clearly annotate why and how hooks are used

## Performance Considerations

- Hooks add overhead to each request
- Multiple hooks execute sequentially
- Cache hooks consume application memory
- Timeout hooks don't stop CPU-bound operations

## Example Usage

```python
from nexios.hooks import before_request, after_request, analytics

@before_request(log_level="DEBUG")
@after_request(log_level="INFO")
@analytics
async def user_profile(request: Request, response: Response):
    # Business logic here
    return response.json({"user": profile_data})
```

Remember that hooks are powerful but limited tools. For complex requirements, consider implementing custom middleware or extending the framework's core functionality.
