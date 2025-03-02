

## **Setting Up the Logger**
First, create and configure a logger for your application:  

```python
from nexios.logging import create_logger

# Create a logger instance
logger = create_logger(
    logger_name="nexios_app",
    log_level="INFO",  # Change to DEBUG for more detailed logs
    log_file="logs/nexios.log",  # Optional: Save logs to a file
    max_bytes=5 * 1024 * 1024,  # Rotate file after 5MB
    backup_count=3  # Keep up to 3 old log files
)
```

---

## **Logging Messages**
Once the logger is set up, use it to log different types of messages:

```python
logger.debug("This is a debug message - useful for troubleshooting")
logger.info("Application started successfully")
logger.warning("Low disk space warning")
logger.error("An error occurred while processing the request")
logger.critical("Critical system failure - shutting down")
```

---

## **Using Logging in a Nexios Application**
If you're using Nexios in a web or API application, integrate logging into your app:

```python
from nexios.application import NexiosApp
from nexios.logging import create_logger

app = NexiosApp()
logger = create_logger("nexios_server", log_level="DEBUG")

@app.route("/")
def homer(req, res):
    logger.info("Home route accessed")
    return res.json("Welcome to Nexios!")


def handle_internal_error(req, res,error):
    logger.error(f"Internal Server Error: {error}")
    return "Something went wrong", 500


```

---

## **Logging with Exception Handling**
To log exceptions, use `exc_info=True`:

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    logger.exception("Attempted to divide by zero")
```

This will log the full traceback of the exception.

---

## **Structured Logging for JSON Output**
If you prefer structured logs for better debugging:

```python
import json

def json_formatter(record):
    return json.dumps({
        "timestamp": record.asctime,
        "level": record.levelname,
        "message": record.msg,
        "module": record.module
    })

logger.handlers[0].setFormatter(json_formatter)
logger.info("This log will now be in JSON format")
```

---

- Nexios provides an optimized logging system that supports queue-based asynchronous logging.  
- You can log to both **console** and **files**, with automatic rotation.  
- Logging helps in debugging, monitoring application health, and handling errors efficiently.  
