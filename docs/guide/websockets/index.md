# WebSocket 
WebSockets enable real-time, bidirectional communication between clients and servers, making them ideal for applications like chat systems, live dashboards, and notifications. Nexios provides a robust WebSocket implementation with intuitive APIs for managing connections, channels, and groups.

::: tip WebSocket Fundamentals
WebSockets in Nexios provide:
- **Real-time Communication**: Bidirectional, low-latency communication
- **Connection Management**: Automatic connection handling and cleanup
- **Channel Support**: Pub/sub patterns for broadcasting messages
- **Group Management**: Organize connections into groups for targeted messaging
- **Error Handling**: Graceful handling of disconnections and errors
- **Scalability**: Support for multiple WebSocket servers and load balancing
- **Security**: Built-in authentication and authorization support
:::

::: tip WebSocket Best Practices
1. **Handle Disconnections**: Always handle WebSocketDisconnect exceptions
2. **Implement Heartbeats**: Use ping/pong for connection health monitoring
3. **Validate Messages**: Validate incoming messages before processing
4. **Rate Limiting**: Implement rate limiting to prevent abuse
5. **Error Handling**: Provide meaningful error messages to clients
6. **Resource Cleanup**: Clean up resources when connections close
7. **Authentication**: Authenticate WebSocket connections when needed
8. **Monitoring**: Monitor connection health and performance
:::

::: tip Common WebSocket Patterns
- **Chat Applications**: Real-time messaging between users
- **Live Dashboards**: Real-time data updates and notifications
- **Gaming**: Real-time game state synchronization
- **Collaboration Tools**: Real-time document editing and presence
- **IoT Applications**: Real-time device monitoring and control
- **Live Streaming**: Real-time media streaming and chat
:::

::: tip WebSocket vs HTTP
**WebSockets:**
- Persistent connection
- Bidirectional communication
- Real-time updates
- Lower latency
- More complex to implement

**HTTP:**
- Request-response model
- Stateless
- Higher latency
- Simpler to implement
- Better for occasional updates
:::

## Basic WebSocket Setup

```python
from nexios import NexiosApp
app = NexiosApp()
@app.ws_route("/ws")
async def ws_handler(ws):
    await ws.accept()
    ...
```
Websocket routing follows the same pattern as other http routes making it easy to use.

::: tip WebSocket Lifecycle
1. **Connection**: Client initiates WebSocket connection
2. **Acceptance**: Server accepts the connection
3. **Communication**: Bidirectional message exchange
4. **Disconnection**: Connection closes (graceful or abrupt)
5. **Cleanup**: Resources are cleaned up
:::

Websocket also pocessed a `WebsocketRoutes` class for more complex routing needs

You can use it like this

```python
from nexios import NexiosApp
app = NexiosApp()
async def ws_handler(ws):
    await ws.accept()
    ...
app.add_ws_route(WebsocketRoutes("/ws", ws_handler))
```

## Websocket Router

The `WSRouter` operate similar to the `Router` but for websockets

```python
from nexios.routing import WSRouter
router = WSRouter()
router.add_ws_route("/ws", ws_handler)
app.mount_ws_router(router, "/ws")
```

::: tip 💡Tip
You can also pass a list of `WebsocketRoutes` to the `WSRouter` constructor similar to `Router` 
```python
from nexios.routing import WSRouter
router = WSRouter([
    WebsocketRoutes("/ws", ws_handler),
    WebsocketRoutes("/ws2", ws_handler2),
])
```
:::

::: tip 💡Tip
You can also add prefix to the `WSRouter` similar to `Router`
```python
from nexios.routing import WSRouter
router = WSRouter(prefix="/ws")
router.add_ws_route("/ws", ws_handler)
router.add_ws_route("/ws2", ws_handler2)
app.mount_ws_router(router, "/ws-overide") #this will override /ws

```
:::

## Sending Messages
the `WebSocket` class has some methods that can be used to send messages to a connected client.

```python
from nexios.websockets.base import WebSocket

async def ws_handler(ws):
    await ws.accept()
    await ws.send_text("Hello World")
    # await ws.send_json({"message": "Hello World"})
    # await ws.send_bytes(b"Hello World")
```

## Receiving Messages

The `WebSocket` class has some methods that can be used to receive messages from a connected client.

```python
from nexios.websockets.base import WebSocket

async def ws_handler(ws):
    await ws.accept()
    message = await ws.receive_text()
    # message = await ws.receive_json()
    # message = await ws.receive_bytes()
    print(message)
```

Nexios supports three primary message formats:



**1. Text Messages**

```python
text_data = await ws.receive_text()
await ws.send_text(f"Received: {text_data}")
```
**2. Binary Messages**

```python
binary_data = await ws.receive_bytes()
await ws.send_bytes(binary_data)  # Echo binary data
```

**3. JSON Messages**

```python
json_data = await ws.receive_json()
await ws.send_json({"status": "success", "data": json_data})
```

---

## Connection Lifecycle

A WebSocket connection follows a clear lifecycle:

**Accept the Connection**

```python
await ws.accept()
```

### Receive Messages (Loop)

```python
while True:
    data = await ws.receive()
    # Process data
```

## Handle Disconnections

```python
from nexios.websockets.base import WebSocketDisconnect
except WebSocketDisconnect:
    print("Client disconnected")
```

###  Close the Connection

```python
finally:
    await ws.close()
```
 this as a downloadable `.md` file too?
```
