Here's a more granular breakdown with additional subheadings for better scannability:

# OpenAPI Configuration Customization

## Introduction
Customize your API documentation by modifying the OpenAPI configuration when initializing your Nexios application.

---

## Basic Configuration Options

### Core Metadata
Set fundamental API information directly in the NexiosApp constructor:
```python
from nexios import NexiosApp

app = NexiosApp(
    title="My API",
    version="1.0.0",
    description="This API provides access to awesome features",
)
```

### Example Endpoint
Basic usage with a sample route:
```python
@app.get("/")
async def get_root(req, res):
    return {"message": "Hello, world!"}
```

![Basic OpenAPI Output](./custom.png)

---

## Advanced Configuration

### Using MakeConfig
For complete control over OpenAPI specification:
```python
from nexios.openapi.models import Contact, License
from nexios import MakeConfig, NexiosApp
```

### Configuration Structure
The complete OpenAPI configuration format:
```python
config = MakeConfig({
    "openapi": {
        "title": "My API",
        "version": "1.0.0",
        "description": "This API provides access to awesome features",
        # Additional configuration elements...
    }
})
```

### Contact Information
Adding support contact details:
```python
"contact": Contact(
    name="API Support",
    url="https://example.com/support",
    email="support@example.com"
),
```

### License Information
Including licensing details:
```python
"license": License(
    name="Apache 2.0",
    url="https://www.apache.org/licenses/LICENSE-2.0.html"
)
```

### Full Implementation
Complete advanced configuration example:
```python
app = NexiosApp(config=config)
```

---

## Visual Representation
The custom configuration will generate documentation with your specified metadata:
![Custom OpenAPI Output](./custom2.png)
