## Channels

WebSocket connections in Nexios are managed using the Channel class, which provides enhanced functionality for handling real-time communication. Channels wrap WebSocket connections with additional features like metadata, expiration, and structured message handling.

## Creating a Channel

```python
from nexios.websockets.channels import Channel, PayloadTypeEnum  

@app.websocket("/chat")  
async def chat_handler(ws: WebSocket):  
    await ws.accept()  

    # Create a channel with JSON payload and 30-minute expiration  
    channel = Channel(  
        websocket=ws,  
        payload_type=PayloadTypeEnum.JSON.value,  
        expires=1800  # 30 minutes  
    )  

    try:  
        while True:  
            data = await ws.receive_json()  
            await channel._send({"response": data})  # Send using channel  
    except Exception as e:  
        print(f"Error: {e}")  
    finally:  
        await ws.close()  
```