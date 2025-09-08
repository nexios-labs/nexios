
# Frequently Asked Questions

## Framework Design

### Why isn't Nexios built on Starlette?
Nexios was designed from the ground up to provide a more opinionated and streamlined experience compared to Starlette. While Starlette is a great ASGI framework, Nexios makes different architectural choices to optimize for:
- Performance through Rust-based core components
- Simpler, more intuitive API design
- Tighter integration with modern Python features
- Built-in best practices for web development

### Why does Nexios use Uvicorn?
Nexios uses Uvicorn as its default ASGI server because:
- It's one of the fastest ASGI servers available
- Built-in support for HTTP/2 and WebSockets
- Excellent performance with async/await Python code
- Active maintenance and wide adoption in the Python community
- Seamless integration with ASGI applications

## Deployment

### How to use Gunicorn with Nexios?
To deploy Nexios with Gunicorn, follow these steps:

1. Install Gunicorn and Uvicorn workers:
   ```bash
   pip install gunicorn uvicorn[standard]
   ```

2. Create a `wsgi.py` file:
   ```python
   from your_app import app

   if __name__ == "__main__":
       import uvicorn
       uvicorn.run("wsgi:app", host="0.0.0.0", port=8000, reload=True)
   ```

3. Run with Gunicorn:
   ```bash
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker wsgi:app
   ```

   - `-w`: Number of worker processes
   - `-k`: Worker class (Uvicorn worker)

