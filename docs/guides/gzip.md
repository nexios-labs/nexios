---
icon: file-zipper
---

# Gzip

Gzip is a widely used compression format that reduces the size of HTTP responses, improving performance by reducing bandwidth usage and load times. The `GzipMiddleware` in Nexios automatically compresses responses for clients that support gzip encoding.

---

### **How It Works**

1. The middleware checks if the `Accept-Encoding` header in the request includes **gzip**.
2. If the client supports gzip, it processes the response after calling the next middleware or handler.
3. If the response meets the compression criteria (size and content type), it compresses the response body using gzip.
4. The middleware updates response headers to indicate gzip encoding.

---

### **Configuration Options**

The middleware retrieves configuration settings from `get_config().gzip`, allowing customization.

| Option              | Default Value            | Description                                                            |
| ------------------- | ------------------------ | ---------------------------------------------------------------------- |
| `minimum_size`      | 500 bytes                | Only compress responses larger than this size.                         |
| `content_types`     | HTML, CSS, JSON, etc.    | Specifies which content types should be compressed.                    |
| `compression_level` | 6 (moderate compression) | Controls gzip compression level (1-9, where 9 is maximum compression). |

---

### **Middleware Flow**

1. **Checks for Gzip Support**
   - Reads the `Accept-Encoding` header.
   - If gzip is not supported, the request continues normally.
2. **Processes Response**
   - Calls the next middleware or request handler.
   - Checks if the response should be compressed based on size and content type.
3. **Compresses Response**
   - Uses `gzip.GzipFile` to compress the response body.
   - Updates headers (`Content-Encoding`, `Content-Length`, `Vary`).

---

### **Example Usage**

#### **1. Enabling Gzip Middleware in Nexios**

To enable gzip compression, add it to your middleware stack:

```python
from nexios.middlewares.gzip import GzipMiddleware
from nexios.application import NexiosApp

app = get_application()
app.add_middleware(GzipMiddleware())
```

---

#### **2. Testing Gzip Compression**

You can check gzip compression by making a request with `Accept-Encoding: gzip`:

```bash
curl -H "Accept-Encoding: gzip" -I http://localhost:8000
```

If compression is applied, the response headers should include:

```plaintext
Content-Encoding: gzip
Vary: Accept-Encoding
```

---

### **Benefits of Using Gzip Compression**

**Reduces Response Size** – Helps in reducing bandwidth usage.\
**Improves Load Times** – Faster delivery of text-based content.\
**Supported by All Modern Browsers** – Works across various clients seamlessly.

This middleware is ideal for optimizing API responses and web pages without affecting functionality.
