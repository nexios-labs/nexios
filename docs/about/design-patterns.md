---
icon: architecture
---

# Design Patterns

Nexios's architecture is built on proven patterns that promote flexibility and maintainability while keeping things simple.

## Core Architectural Patterns

### Middleware Pipeline
Like Express.js, we use a linear middleware pipeline that's easy to understand and extend:
```python
app = Nexios()
app.use(middleware1)
app.use(middleware2)
```

### Event-Driven Architecture
Our event system lets you decouple components while maintaining clear communication paths:
```python
@app.on("user.created")
async def handle_new_user(event):
    # Handle user creation
    pass
```

### Plugin System
Extend functionality without touching core code:
```python
app.use(session_plugin)
app.use(auth_plugin)
```

## Design Decisions

### Why These Patterns?

1. **Middleware Pipeline**
   - Simple to understand and debug
   - Familiar to Express.js developers
   - Easy to compose and reuse

2. **Event System**
   - Decouples components
   - Makes testing easier
   - Enables easy extensions

3. **Plugin Architecture**
   - Keeps core clean
   - Enables community contributions
   - Maintains flexibility

## Best Practices

When using Nexios, we recommend:

1. Keep middleware focused and composable
2. Use events for cross-cutting concerns
3. Prefer small, focused plugins over monolithic ones
4. Follow Python's idioms while leveraging Express.js patterns

