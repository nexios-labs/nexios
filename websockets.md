


Nexios provides built-in support for WebSockets, enabling real-time, bidirectional communication between clients and the server. The WebSocket implementation in Nexios is similar to Starlatte, making it easy for developers familiar with Starlatte to get started quickly.

WebSocket endpoints in Nexios are defined using the `@websocket` decorator. The handler function receives a `WebSocket` instance for managing the connection.

```python
from nexios import get_application, WebSocket
from nexios.routing import WSRouter
app = get_application()

ws_router = WSRouter()
app.mount_ws_router(ws_app)
@ws_router.ws_route("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    while True:
        data = await ws.receive_text()
        await ws.send_text(f"Received: {data}")
```

---

## **Handling Connections**
- `await ws.accept()`: Accepts an incoming WebSocket connection.
- `await ws.close()`: Closes the WebSocket connection gracefully, optionally with a close code and reason.
- `ws.client`: Provides client information (IP address, port, etc.).
- `ws.scope`: Returns metadata about the connection, including **headers, cookies, query parameters, and path parameters**.

---

## **Accessing Headers, Cookies, and Parameters**
Nexios WebSockets provide access to various request metadata via `ws.scope`:

### **Headers**
WebSocket headers can be accessed from the `ws.scope["headers"]` dictionary. Headers are stored as a list of tuples (key, value), both in byte format.

```python
@ws_router.ws_route("/headers")
async def headers_ws(ws: WebSocket):
    await ws.accept()
    headers = {k.decode(): v.decode() for k, v in ws.headers}
    print("Headers:", headers)
```

---

### **Cookies**
Cookies are passed via headers, so they can be accessed from `ws.scope["headers"]`.

```python
@ws_router.ws_route("/cookies")
async def cookies_ws(ws: WebSocket):
    await ws.accept()
  
    cookies = ws.cookies
    print("Cookies:", cookies)
```

---

### **Query Parameters**
Query parameters from the WebSocket URL are stored in `ws.scope["query_string"]`. You must decode it from bytes to string.

```python
@ws_router.ws_route("/ws")
async def query_params_ws(ws: WebSocket):
    await ws.accept()
    query_params = ws.query_params
    print("Query Parameters:", query_params)
```

Example WebSocket connection:
```
ws://localhost:8000/ws?token=12345&user=dunamis
```
Output:
```
Query Parameters: token=12345&user=dunamis
```

---

### **Path Parameters**
Path parameters are extracted from the URL pattern:

```python
@ws_router.ws_route("/ws/{room_id}")
async def websocket_with_params(ws: WebSocket):
    await ws.accept()
    room_id = ws.path_params
    print(f"Connected to room: {room_id}")
```

Connecting to `ws://localhost:8000/ws/42` prints:
```
Connected to room: 42
```

---

## **Sending and Receiving Data**
Nexios WebSockets support multiple data types for sending and receiving messages.

### **Receiving Data**
- `await ws.receive_text()`: Receives a UTF-8 text message.
- `await ws.receive_bytes()`: Receives a binary message.
- `await ws.receive_json()`: Receives a JSON message and automatically parses it into a Python dictionary.

Example:

```python
@ws_router.ws_route("/receive")
async def receive_example(ws: WebSocket):
    await ws.accept()
    json_data = await ws.receive_json()
    print("Received JSON:", json_data)
```

---

### **Sending Data**
- `await ws.send_text(text: str)`: Sends a UTF-8 text message.
- `await ws.send_bytes(data: bytes)`: Sends binary data.
- `await ws.send_json(data: dict)`: Sends a JSON message by serializing a Python dictionary.

Example:

```python
@ws_router.ws_route("/send")
async def send_example(ws: WebSocket):
    await ws.accept()
    await ws.send_json({"message": "Hello, Client!"})
```

---

## **Broadcasting Messages**
To broadcast messages to multiple connected clients, use a global set of connections.

```python
connections = set()

@ws_router.ws_route("/broadcast")
async def broadcast_ws(ws: WebSocket):
    await ws.accept()
    connections.add(ws)
    try:
        while True:
            data = await ws.receive_text()
            for conn in connections:
                await conn.send_text(data)
    except:
        connections.remove(ws)
```

---

## **WebSocket Middleware**
Nexios allows adding middleware to WebSocket connections for authentication, logging, etc.

```python
async def log_requests(ws: WebSocket, call_next):
    print(f"New WebSocket connection from {ws.client}")
    await call_next()

app.add_ws_middleware(log_requests) #global middleware
ws_router.add_ws_middleware(log_requests) #router  middleware


```
Nexios websocket also support route specific middlewares

```python
async def log_requests(ws: WebSocket, call_next):
    print(f"New WebSocket connection from {ws.client}")
    await call_next()


@ws_router.ws_route("/chat", middleware = [
    log_requests
])
async def ws_handler(ws):
    ...


```
---

## **Handling Custom Close Codes**
You can send a custom close code and message when terminating a connection.

```python
@ws_router.ws_route("/custom-close")
async def custom_close_ws(ws: WebSocket):
    await ws.accept()
    await ws.send_text("Closing connection with custom code")
    await ws.close(code=1001, reason="Service shutting down")
```

---

## **Handling WebSocket Exceptions**
To handle errors properly, use a try-except block.

```python
from nexios.websocket import WebSocketDisconnect

@ws_router.ws_route("/error-handling")
async def error_handling_ws(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            message = await ws.receive_text()
            await ws.send_text(f"Echo: {message}")
    except WebSocketDisconnect:
        print("Client disconnected")
```

