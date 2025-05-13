---
layout: home

hero:
  name: Nexios
  text: Async Python Web Framework
  tagline: Nexios is a fast, minimalist Python framework for building async APIs with clean architecture, zero boilerplate, and a Pythonic feel.
  image:
    src: /icon.svg
    alt: Nexios
  actions:
    - theme: primary
      text: Get Started
      link: /guide/getting-started
    - theme: alt
      text: View on GitHub
      link: https://github.com/nexios-labs/nexios

features:
  - icon: ⚡
    title: Async by Design
    details: Nexios is built from the ground up with native async support, making it perfect for I/O-bound operations like API calls, database access, or file handling. Every route, middleware, and lifecycle hook supports async/await, allowing you to write clean, non-blocking code that scales naturally under heavy loads.

  - icon: 🚀 
    title: Lightning-Fast Performance 
    details: Nexios is ultra-lightweight and avoids bloated abstractions. It uses minimal layers between your code and the core ASGI server, ensuring requests are processed with blazing speed. The focus on performance makes it a great choice for microservices, APIs, and real-time apps where low latency matters.

  - icon: 🔌
    title: Built-in WebSocket Support 
    details: Real-time communication is a first-class citizen in Nexios. With direct WebSocket routing and connection lifecycle handling, you can build features like live chats, notifications, or real-time dashboards without external plugins. Managing WebSocket events is just as simple as defining routes.
---


## Getting Started  <Badge type="tip" text="2.4.0" />

You can get started using Nexios right away using `pip`

```sh
pip install nexios
nexios new <project_name>
```



```py [config.js]
from NexiosApp

app = NexiosApp

@app.get("/")
async def index(request, response):

  return {"message" : "Nexios , Fast Async , Minimal"}
```
