Nexios provides a comprehensive event system that enables communication between different parts of your application. The event system is designed to be:

- **Flexible**: Supports synchronous and asynchronous operations
- **Scalable**: Manages thousands of events efficiently
- **Thread-safe**: Safe for use in multi-threaded environments
- **Feature-rich**: Includes priorities, namespaces, weak references, and more

## Core Concepts

### Events

An `Event` represents a specific occurrence in your application that other parts can listen for and respond to. Each event has:

- A unique name
- A set of listeners (callbacks)
- Configuration options (priority, max listeners, etc.)

### EventEmitter

The `EventEmitter` class serves as a central hub for creating and managing events. It provides methods to:

- Register and remove listeners
- Trigger events
- Organize events hierarchically using namespaces

### Event Priorities

Listeners can be assigned one of five priority levels:

1. `EventPriority.HIGHEST`
2. `EventPriority.HIGH`
3. `EventPriority.NORMAL` (default)
4. `EventPriority.LOW`
5. `EventPriority.LOWEST`

Listeners are executed in priority order (highest first) when an event is triggered.

### Event Phases

Events propagate through three phases:

1. **Capturing Phase**: From parent to child
2. **Target Phase**: On the event target
3. **Bubbling Phase**: From child to parent

## Basic Usage

### Creating and Triggering Events

```python
from nexios.events import EventEmitter

emitter = EventEmitter()

# Register a listener
@emitter.on("user.created")
def handle_user_created(user):
    print(f"User created: {user['name']}")

# Trigger the event
emitter.emit("user.created", {"name": "Alice", "email": "alice@example.com"})
```

### One-time Listeners

```python
# This listener will only be called once
@emitter.once("system.ready")
def handle_system_ready():
    print("System is ready!")
```

### Event Namespaces

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

## Advanced Features

### Asynchronous Events

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

### Weak References

```python
# Use weak_ref=True to prevent memory leaks
@emitter.on("timer.tick", weak_ref=True)
def handle_tick():
    print("Tick")
```

### Event Metrics

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

### Event History

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

## Error Handling

The event system provides several specialized exceptions:

- `EventError`: Base class for all event-related errors
- `ListenerAlreadyRegisteredError`: Raised when adding a duplicate listener
- `MaxListenersExceededError`: Raised when exceeding max listeners
- `EventCancelledError`: Raised when event propagation is cancelled

```python
try:
    emitter.emit("critical.event")
except EventCancelledError:
    print("Event was cancelled")
except EventError as e:
    print(f"Event error: {e}")
```

## Performance Considerations

### Benchmarking

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

### EventEmitter Methods

- `event(name)`: Get or create an event
- `namespace(name)`: Create a namespace
- `on(event_name, func)`: Register a listener
- `once(event_name, func)`: Register a one-time listener
- `emit(event_name, *args, **kwargs)`: Trigger an event
- `remove_listener(event_name, func)`: Remove a specific listener
- `remove_all_listeners(event_name)`: Remove all listeners for an event

### Event Methods

- `listen(func)`: Register a listener
- `once(func)`: Register a one-time listener
- `trigger(*args, **kwargs)`: Fire the event
- `remove_listener(func)`: Remove a specific listener
- `remove_all_listeners()`: Remove all listeners
- `get_metrics()`: Get performance metrics
- `get_history()`: Get event trigger history
- `cancel()`: Cancel event propagation
- `prevent_default()`: Prevent default behavior

### AsyncEventEmitter Methods

- `emit_async()`: Asynchronous version of emit
- `schedule_emit()`: Schedule an event to be triggered
- `shutdown()`: Clean up resources

## Examples

### Complex Event Hierarchy

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

### Event Cancellation

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

### Mixed Sync/Async Listeners

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
