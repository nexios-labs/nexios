

# WebSocket API Reference (with Examples)

---

## ⚙️ Initialize WebSocket

```python
ws = WebSocket(scope, receive, send)
```

---

## ✅ Accepting a Connection

```python
await ws.accept()
```

Optionally with subprotocol and headers:

```python
await ws.accept(subprotocol="chat", headers=[(b"x-token", b"abc123")])
```

---

## 📥 Receiving Messages

### 📝 Receive Text

```python
text = await ws.receive_text()
```

### 🧱 Receive Bytes

```python
data = await ws.receive_bytes()
```

### 🧬 Receive JSON

```python
payload = await ws.receive_json()
# mode="binary" also supported
```

---

## 🔁 Streaming Messages

```python
async for message in ws.iter_text():
    print("Got message:", message)
```

Same applies for:

```python
await ws.iter_bytes()
await ws.iter_json()
```

---

## 📤 Sending Messages

### 📝 Send Text

```python
await ws.send_text("hello world")
```

### 📦 Send Bytes

```python
await ws.send_bytes(b"\x00\x01")
```

### 🧬 Send JSON

```python
await ws.send_json({"user": "dunamis", "msg": "yo!"})
# or binary mode:
await ws.send_json({"ping": True}, mode="binary")
```

---

## ❌ Closing Connection

```python
await ws.close(code=1001, reason="bye bye!")
```

---

## 🔎 Check Connection

```python
if ws.is_connected():
    print("We’re live 🎉")
```

---

Want me to turn this into a Markdown doc file (`websocket.md`) or embed it in auto-generated docs for Nexios?
