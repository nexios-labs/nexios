---
icon: calendar-star
---

# Events System

## Introduction to the Event System

The Nexios event system provides a powerful way to implement loosely coupled, event-driven architectures in your applications. It allows components to communicate without direct dependencies, making your code more maintainable and flexible.

At its core, Nexios events implement the publish-subscribe (pub-sub) pattern, where:

* **Publishers** emit events without knowing who will receive them
* **Subscribers** listen for events without knowing who emitted them
* **Event objects** carry data and metadata about what happened

This architecture is particularly useful for:

* Decoupling components of your application
* Implementing cross-cutting concerns like logging or analytics
* Building reactive systems that respond to state changes
* Creating extensible applications with plugin architectures

## Basic Event Usage

### Setting Up Events

The Nexios event system is available right out of the box in every application:

```python
from nexios import get_application
from nexios.events import EventEmitter

app = get_application()

# Access the global event emitter
events = app.events
```

### Subscribing to Events

To subscribe to an event, use the `on` method:

```python
from nexios import get_application

app = get_application()

# Define an event handler
async def user_created_handler(user_data):
    print(f"New user created: {user_data['username']}")
    # Perform additional actions like sending welcome email

# Subscribe to an event
app.events.on("user.created", user_created_handler)
```

You can also use the decorator syntax:

```python
@app.events.on("user.created")
async def user_created_handler(user_data):
    print(f"New user created: {user_data['username']}")
```

### Publishing Events

To publish an event, use the `emit` method:

```python
# In your user creation route
@app.post("/users")
async def create_user(req, res):
    user_data = await req.json
    # Save user to database...
    user_id = db.save_user(user_data)
    
    # Emit event with the new user data
    await app.events.emit("user.created", {
        "id": user_id,
        "username": user_data["username"],
        "email": user_data["email"],
        "created_at": datetime.now().isoformat()
    })
    
    return res.json({"id": user_id, "message": "User created successfully"})
```

## Event Types and Patterns

### Naming Conventions

Nexios events follow a hierarchical naming convention using dots as separators. This allows for more granular control when subscribing to events:

```
domain.action[.subaction]
```

Examples:

* `user.created`
* `user.profile.updated`
* `payment.processing.failed`
* `app.startup`
* `app.shutdown`





### Removing Event Listeners

You can remove event listeners when they're no longer needed:

```python
# Define handler
async def temporary_handler(data):
    print(f"Processing data: {data}")

# Add handler
app.events.on("data.received", temporary_handler)

# Later, remove the handler
app.events.off("data.received", temporary_handler)

# Or remove all handlers for an event
app.events.off("data.received")
```

### Event Namespaces

For more complex applications, you can create separate event namespaces:

```python
from nexios.events import EventEmitter

# User-related events
user_events = EventEmitter("user")

@user_events.on("created")  # Equivalent to "user.created"
async def on_user_created(user_data):
    print(f"User created: {user_data['username']}")

# Payment-related events
payment_events = EventEmitter("payment")

@payment_events.on("processed")  # Equivalent to "payment.processed"
async def on_payment_processed(payment_data):
    print(f"Payment processed: {payment_data['id']}")

# Emit events
await user_events.emit("created", {"username": "john_doe"})
await payment_events.emit("processed", {"id": "pay_123456"})
```

## Practical Examples

### Example 1: User Registration Flow

```python
from nexios import get_application
from nexios.events import EventEmitter

app = get_application()

# Event handlers
@app.events.on("user.registered")
async def send_welcome_email(user):
    print(f"Sending welcome email to {user['email']}")
    await email_service.send_template(
        to=user["email"],
        template="welcome",
        context={"username": user["username"]}
    )

@app.events.on("user.registered")
async def assign_default_permissions(user):
    print(f"Assigning default permissions to user {user['username']}")
    await permissions_service.assign_defaults(user["id"])

@app.events.on("user.registered")
async def notify_admins(user):
    print(f"Notifying admins about new user: {user['username']}")
    await notification_service.notify_admins(
        title="New User Registration",
        message=f"User {user['username']} has registered"
    )

# Registration endpoint
@app.post("/auth/register")
async def register_user(req, res):
    user_data = await req.json
    
    # Validate user data...
    # Create user in database...
    
    new_user = {
        "id": "user_123",
        "username": user_data["username"],
        "email": user_data["email"],
        "created_at": datetime.now().isoformat()
    }
    
    # Emit event
    await app.events.emit("user.registered", new_user)
    
    return res.json({"success": True, "user": new_user})
```

### Example 2: Order Processing System

```python
from nexios import get_application
from nexios.events import EventEmitter

app = get_application()

# Event handlers
@app.events.on("order.created")
async def validate_payment(order):
    print(f"Validating payment for order #{order['id']}")
    payment_valid = await payment_service.validate(order["payment_id"])
    
    if payment_valid:
        await app.events.emit("order.payment.valid", order)
    else:
        await app.events.emit("order.payment.invalid", order)

@app.events.on("order.payment.valid")
async def process_order(order):
    print(f"Processing order #{order['id']}")
    await inventory_service.reserve_items(order["items"])
    await app.events.emit("order.processing", order)

@app.events.on("order.processing")
async def notify_warehouse(order):
    print(f"Notifying warehouse about order #{order['id']}")
    await warehouse_service.create_shipment(order)

@app.events.on("order.payment.invalid")
async def handle_invalid_payment(order):
    print(f"Invalid payment for order #{order['id']}")
    await notification_service.notify_customer(
        order["customer_id"],
        "Payment Issue",
        "There was an issue with your payment, please update your payment method"
    )

# Order creation endpoint
@app.post("/orders")
async def create_order(req, res):
    order_data = await req.json
    
    # Validate order data...
    # Save order to database...
    
    new_order = {
        "id": "ord_123456",
        "customer_id": order_data["customer_id"],
        "items": order_data["items"],
        "payment_id": order_data["payment_id"],
        "total": 99.99,
        "created_at": datetime.now().isoformat()
    }
    
    # Emit event
    await app.events.emit("order.created", new_order)
    
    return res.json({"success": True, "order": new_order})
```

## Best Practices

### Event Design Guidelines

1. **Name events hierarchically**: Use dot-notation for a clear event hierarchy (e.g., `user.created`, `payment.failed`).
2. **Event payloads**: Keep event data serializable and include all relevant information the handlers might need.
3. **Event documentation**: Document events (names, payloads, purposes) clearly for other developers.
4. **Single responsibility**: Design event handlers to do one thing well.
5. **Idempotency**: When possible, make event handlers idempotent (safe to execute multiple times).
6. **Error handling**: Always include proper error handling in event subscribers.

```python
@app.events.on("user.created")
async def send_welcome_email(user_data):
    try:
        # Send email logic
        await email_service.send_welcome(user_data["email"])
    except Exception as e:
        # Log the error, but don't crash
        log.error(f"Failed to send welcome email: {e}")
        # Optionally re-emit as error event
        await app.events.emit("error.email.failed", {
            "user_id": user_data["id"],
            "error": str(e)
        })
```

### Performance Considerations

1. **Minimize heavy processing**: Keep event handlers lightweight or offload to background tasks.
2. **Be cautious with wildcard listeners**: They can impact performance if overused.
3. **Consider event queue systems**: For high-volume events, consider using external message queues.

```python
@app.events.on("order.created")
async def process_order_background(order_data):
    # Instead of processing directly, send to a background worker
    await queue.enqueue("process_order", order_data)
```

## Integration with External Systems

Nexios events can be integrated with external message brokers and event systems:

````python
from nexios import get_application
import aio_pika  # AMQP client (RabbitMQ)

app = get_application()

# Connect to RabbitMQ on startup
@app.on_startup
async def setup_rabbitmq():
    app.state.rabbitmq = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    app.state.channel = await app.state.rabbitmq.channel()
    app.state.exchange = await app.state.channel.declare_exchange(
        "nexios_events", aio_pika.ExchangeType.TOPIC
    )

# Forward specific events to RabbitMQ
@app.events.on("user")
async def forward_to_rabbitmq(event_name, data):
    # Only if RabbitMQ is connected
    if hasattr(app.state, "exchange"):
        message = aio_pika.Message(
            body=json.dumps(data).encode(),
            content_type="application/json"
        )
        await app.state.exchange.publish(
            message, routing


Nexios provides a comprehensive event system that enables communication between different parts of your application. The event system is designed to be:

* **Flexible**: Supports synchronous and asynchronous operations
* **Scalable**: Manages thousands of events efficiently
* **Thread-safe**: Safe for use in multi-threaded environments
* **Feature-rich**: Includes priorities, namespaces, weak references, and more

### Core Concepts

#### Events

An `Event` represents a specific occurrence in your application that other parts can listen for and respond to. Each event has:

* A unique name
* A set of listeners (callbacks)
* Configuration options (priority, max listeners, etc.)

#### EventEmitter

The `EventEmitter` class serves as a central hub for creating and managing events. It provides methods to:

* Register and remove listeners
* Trigger events
* Organize events hierarchically using namespaces

#### Event Priorities

Listeners can be assigned one of five priority levels:

1. `EventPriority.HIGHEST`
2. `EventPriority.HIGH`
3. `EventPriority.NORMAL` (default)
4. `EventPriority.LOW`
5. `EventPriority.LOWEST`

Listeners are executed in priority order (highest first) when an event is triggered.

#### Event Phases

Events propagate through three phases:

1. **Capturing Phase**: From parent to child
2. **Target Phase**: On the event target
3. **Bubbling Phase**: From child to parent

### Basic Usage

#### Creating and Triggering Events

```python
from nexios.events import EventEmitter

emitter = EventEmitter()

# Register a listener
@emitter.on("user.created")
def handle_user_created(user):
    print(f"User created: {user['name']}")

# Trigger the event
emitter.emit("user.created", {"name": "Alice", "email": "alice@example.com"})
````

#### One-time Listeners

```python
# This listener will only be called once
@emitter.once("system.ready")
def handle_system_ready():
    print("System is ready!")
```

#### Event Namespaces

```python
# Create a namespace
user_events = emitter.namespace("user")

# Events in this namespace will have names like "user:created"
@user_events.on("created")
def handle_user_created(user):
    print(f"User created: {user['name']}")

# Trigger the namespaced event
user_events.emit("created", {"name": "Bob"})
```

### Advanced Features

#### Asynchronous Events

```python
from nexios import AsyncEventEmitter

emitter = AsyncEventEmitter()

@emitter.on("data.received")
async def process_data(data):
    # Async operations here
    await save_to_database(data)

# Async emit
await emitter.emit_async("data.received", large_dataset)
```

#### Weak References

```python
# Use weak_ref=True to prevent memory leaks
@emitter.on("timer.tick", weak_ref=True)
def handle_tick():
    print("Tick")
```

#### Event Metrics

```python
event = emitter.event("user.updated")
stats = event.get_metrics()
"""
{
    "trigger_count": 42,
    "total_listeners_executed": 126,
    "average_execution_time": 0.002
}
"""
```

#### Event History

```python
history = event.get_history(limit=5)
"""
[
    {
        "timestamp": "2023-01-01T12:00:00",
        "event_id": "abc123...",
        "args": "(user1,)",
        "kwargs": "{}",
        "listeners_executed": 3,
        "execution_time": 0.005,
        "cancelled": False
    },
    ...
]
"""
```

### Error Handling

The event system provides several specialized exceptions:

* `EventError`: Base class for all event-related errors
* `ListenerAlreadyRegisteredError`: Raised when adding a duplicate listener
* `MaxListenersExceededError`: Raised when exceeding max listeners
* `EventCancelledError`: Raised when event propagation is cancelled

```python
try:
    emitter.emit("critical.event")
except EventCancelledError:
    print("Event was cancelled")
except EventError as e:
    print(f"Event error: {e}")
```

### Performance Considerations

#### Benchmarking

```python
from nexios import EventBenchmark

benchmark = EventBenchmark.benchmark(emitter, "test.event", iterations=10000)
"""
{
    "iterations": 10000,
    "total_time": 0.123,
    "average_time": 0.0000123,
    "events_per_second": 81300.81
}
"""
```

#### EventEmitter Methods

* `event(name)`: Get or create an event
* `namespace(name)`: Create a namespace
* `on(event_name, func)`: Register a listener
* `once(event_name, func)`: Register a one-time listener
* `emit(event_name, *args, **kwargs)`: Trigger an event
* `remove_listener(event_name, func)`: Remove a specific listener
* `remove_all_listeners(event_name)`: Remove all listeners for an event

#### Event Methods

* `listen(func)`: Register a listener
* `once(func)`: Register a one-time listener
* `trigger(*args, **kwargs)`: Fire the event
* `remove_listener(func)`: Remove a specific listener
* `remove_all_listeners()`: Remove all listeners
* `get_metrics()`: Get performance metrics
* `get_history()`: Get event trigger history
* `cancel()`: Cancel event propagation
* `prevent_default()`: Prevent default behavior

#### AsyncEventEmitter Methods

* `emit_async()`: Asynchronous version of emit
* `schedule_emit()`: Schedule an event to be triggered
* `shutdown()`: Clean up resources

### Examples

#### Complex Event Hierarchy

```python
# Create hierarchical events
app_events = emitter.namespace("app")
ui_events = app_events.namespace("ui")

@ui_events.on("button.click")
def handle_click(button_id):
    print(f"Button {button_id} clicked")

# This will trigger both listeners
emitter.emit("app:ui:button.click", "submit")
```

#### Event Cancellation

```python
@emitter.on("process.data", priority=EventPriority.HIGHEST)
def validate_data(data):
    if not data.is_valid():
        raise EventCancelledError("Invalid data")

try:
    emitter.emit("process.data", raw_data)
except EventCancelledError:
    print("Processing cancelled due to invalid data")
```

#### Mixed Sync/Async Listeners

```python
@emitter.on("order.placed")
def log_order(order):
    print(f"Order received: {order.id}")

@emitter.on("order.placed")
async def process_order(order):
    await charge_customer(order)
    await send_confirmation_email(order)

# Both listeners will be called
emitter.emit("order.placed", new_order)
```
