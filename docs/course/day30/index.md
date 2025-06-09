# Day 30: Final Project

## Learning Objectives
- Build a complete Nexios application
- Integrate all major features
- Implement best practices
- Deploy production-ready code

## Project: Real-time Collaboration Platform

We'll build a real-time collaboration platform that demonstrates Nexios's capabilities:

- Authentication and authorization
- Real-time WebSocket communication
- Channel-based messaging
- File handling
- API endpoints
- Production deployment

## Project Structure

```
collaboration_platform/
├── app/
│   ├── __init__.py
│   ├── auth.py
│   ├── websockets.py
│   ├── api.py
│   ├── models.py
│   └── utils.py
├── static/
│   ├── css/
│   └── js/
├── templates/
├── tests/
├── config/
│   ├── development.json
│   └── production.json
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Core Application

Main application setup:

```python
from nexios import NexiosApp
from nexios.auth import auth
from nexios.websockets import WebSocketConsumer
from nexios.websockets.channels import Channel, ChannelBox
from nexios.http import Request, Response
from nexios.logging import create_logger
import jwt
import os

# Application setup
app = NexiosApp()

# Configure logging
logger = create_logger(
    logger_name="collaboration_platform",
    log_level="info",
    log_file="app.log"
)

# Load configuration
with open(f"config/{os.getenv('NEXIOS_ENV', 'development')}.json") as f:
    config = json.load(f)
app.config.update(config)
```

## Authentication System

```python
# auth.py
from nexios.exceptions import HTTPException
import bcrypt
import jwt

class User:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = self._hash_password(password)
    
    def _hash_password(self, password: str) -> str:
        return bcrypt.hashpw(
            password.encode(),
            bcrypt.gensalt()
        ).decode()
    
    def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(
            password.encode(),
            self.password.encode()
        )

@app.post("/auth/register")
async def register(request: Request, response: Response):
    data = await request.json
    
    # Create user
    user = User(
        data["username"],
        data["password"]
    )
    # Save user...
    
    return Response(
        {"message": "User registered"},
        status_code=201
    )

@app.post("/auth/login")
async def login(request: Request, response: Response):
    data = await request.json
    
    # Verify credentials
    user = await get_user(data["username"])
    if not user or not user.verify_password(data["password"]):
        raise HTTPException(401, "Invalid credentials")
    
    # Generate token
    token = jwt.encode(
        {"username": user.username},
        app.config["jwt_secret"],
        algorithm="HS256"
    )
    
    return response.json({"token": token})
```

## Real-time Collaboration

```python
# websockets.py
class CollaborationConsumer(WebSocketConsumer):
    encoding = "json"
    
    async def on_connect(self, websocket):
        # Verify authentication
        try:
            token = websocket.headers["Authorization"].split(" ")[1]
            payload = jwt.decode(
                token,
                app.config["jwt_secret"],
                algorithms=["HS256"]
            )
            websocket.scope["user"] = payload
        except Exception:
            await websocket.close(code=4001)
            return
        
        await websocket.accept()
        
        # Set up channel
        self.channel = Channel(
            websocket=websocket,
            payload_type="json",
            expires=3600
        )
    
    async def on_receive(self, websocket, data):
        action = data.get("action")
        room_id = data.get("room")
        
        if action == "join":
            # Join collaboration room
            await ChannelBox.add_channel_to_group(
                self.channel,
                f"room_{room_id}"
            )
            await self.broadcast(
                {
                    "type": "user_joined",
                    "user": websocket.scope["user"]["username"]
                },
                group_name=f"room_{room_id}",
                save_history=True
            )
        
        elif action == "update":
            # Broadcast updates
            await self.broadcast(
                {
                    "type": "content_update",
                    "content": data["content"],
                    "user": websocket.scope["user"]["username"]
                },
                group_name=f"room_{room_id}",
                save_history=True
            )
    
    async def on_disconnect(self, websocket, close_code):
        if self.channel:
            # Clean up channel
            groups = await ChannelBox.show_groups()
            for group_name in groups:
                if self.channel in groups[group_name]:
                    await ChannelBox.remove_channel_from_group(
                        self.channel,
                        group_name
                    )

# Register WebSocket consumer
app.add_route(
    "/ws/collaborate",
    CollaborationConsumer.as_route("/ws/collaborate")
)
```

## API Endpoints

```python
# api.py
@app.get("/api/rooms")
@auth(["jwt"])
async def list_rooms(request: Request, response: Response):
    rooms = await get_rooms()
    return response.json({
        "rooms": [room.to_dict() for room in rooms]
    })

@app.post("/api/rooms")
@auth(["jwt"])
async def create_room(request: Request, response: Response):
    data = await request.json
    
    room = await create_new_room(
        name=data["name"],
        owner=request.scope["user"]["username"]
    )
    
    return Response(
        room.to_dict(),
        status_code=201
    )

@app.get("/api/rooms/{room_id}/history")
@auth(["jwt"])
async def room_history(request: Request, response: Response):
    room_id = request.path_params.room_id
    history = await ChannelBox.show_history(f"room_{room_id}")
    
    return response.json({
        "history": history
    })
```

## File Handling

```python
@app.post("/api/rooms/{room_id}/files")
@auth(["jwt"])
async def upload_file(request: Request, response: Response):
    room_id = request.path_params.room_id
    
    # Handle file upload
    form = await request.form
    file = form["file"]
    
    # Save file
    filename = file.filename
    content = await file.read()
    await save_file(room_id, filename, content)
    
    # Notify room members
    await broadcast_to_room(
        room_id,
        {
            "type": "file_uploaded",
            "filename": filename,
            "user": request.scope["user"]["username"]
        }
    )
    
    return Response(
        {"message": "File uploaded"},
        status_code=201
    )

@app.get("/api/rooms/{room_id}/files/{filename}")
@auth(["jwt"])
async def download_file(request: Request, response: Response):
    room_id = request.path_params.room_id
    filename = request.path_params.filename
    
    content = await get_file(room_id, filename)
    
    return Response(
        content,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
```

## Production Configuration

```python
# config/production.json
{
    "jwt_secret": "your-secret-key",
    "allowed_origins": [
        "https://your-domain.com"
    ],
    "file_storage": {
        "type": "s3",
        "bucket": "your-bucket",
        "region": "your-region"
    },
    "redis_url": "redis://redis:6379",
    "log_level": "info"
}
```

## Docker Setup

```dockerfile
# Dockerfile
FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV NEXIOS_ENV=production
ENV HOST=0.0.0.0
ENV PORT=8000

EXPOSE 8000
CMD ["python", "-m", "nexios", "run"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - NEXIOS_ENV=production
    depends_on:
      - redis
    volumes:
      - ./logs:/app/logs
    deploy:
      replicas: 2
  
  redis:
    image: redis:alpine
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

## Testing

```python
# tests/test_collaboration.py
import pytest
from nexios.testing import Client

@pytest.fixture
async def auth_headers():
    # Create test user and get token
    token = create_test_token()
    return {"Authorization": f"Bearer {token}"}

async def test_create_room(async_client: Client, auth_headers):
    response = await async_client.post(
        "/api/rooms",
        json={"name": "Test Room"},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == "Test Room"

async def test_websocket_collaboration(async_client: Client, auth_headers):
    async with async_client.websocket_connect(
        "/ws/collaborate",
        headers=auth_headers
    ) as websocket:
        # Join room
        await websocket.send_json({
            "action": "join",
            "room": "test-room"
        })
        
        # Send update
        await websocket.send_json({
            "action": "update",
            "room": "test-room",
            "content": "Hello, World!"
        })
        
        # Verify response
        response = await websocket.receive_json()
        assert response["type"] == "content_update"
        assert response["content"] == "Hello, World!"
```

## Best Practices

1. Security:
   - Implement proper authentication
   - Validate all input
   - Secure file handling
   - Use HTTPS in production

2. Real-time Features:
   - Manage WebSocket connections
   - Handle disconnections gracefully
   - Implement proper error handling
   - Use channel groups effectively

3. Performance:
   - Configure caching
   - Optimize file handling
   - Use connection pooling
   - Monitor resource usage

4. Deployment:
   - Use container orchestration
   - Implement health checks
   - Set up monitoring
   - Configure logging

## 📝 Final Exercise

1. Extend the platform:
   - Add user profiles
   - Implement file versioning
   - Add real-time cursors
   - Create admin dashboard

2. Enhance features:
   - Add video chat
   - Implement drawing tools
   - Add file preview
   - Create mobile interface 