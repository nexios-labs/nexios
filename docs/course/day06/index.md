# 🚀 Day 6: Environment Configuration

## Using .env Files

Nexios supports environment configuration through `.env` files:

```python
from nexios import NexiosApp
from nexios.config import MakeConfig

config = MakeConfig(
    debug = False,
    cors = {
        "allow_origins" : ["*"]
    }
)
app = NexiosApp(config=settings)
```

Example `.env` file:
```env
APP_NAME=My Nexios App
DEBUG=true
DATABASE_URL=postgresql://user:pass@localhost/db
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,example.com
CORS_ORIGINS=http://localhost:3000,https://app.example.com
```

## CORS Configuration

Configure Cross-Origin Resource Sharing (CORS):

```python
from nexios import NexiosApp
from nexios.middleware import CORSMiddleware
from nexios.config import MakeConfig
app = NexiosApp(config = MakeConfig(
    cors = {
    "allow_origins" : "*"
}
))

# Basic CORS setup
app.add_middleware(CORSMiddleware())


```





