
---

### **Example: Basic Nexios Application**  

```python
from nexios import get_application  

app = get_application()  

@app.route("/", methods=["GET"])  
def home(req, res):  
    return res.json({"message": "Welcome to Nexios!"})  

@app.route("/hello/{name}", methods=["GET"])  
def greet(req, res):  
    name = req.path_params.name  
    return res.json({"message": f"Hello, {name}!"})  

# Run using Uvicorn  
if __name__ == "__main__":  
    import uvicorn  
    uvicorn.run(app, host="127.0.0.1", port=5000, reload=True)  
```

---

### **Explanation:**  
- **Initializes** a Nexios app using `get_application()`.  
- **Defines routes:**  
  - `/` → Returns a **welcome message**.  
  - `/hello/{name}` → Accepts a **dynamic parameter** and returns a **personalized message**.  
- **Runs with Uvicorn**, enabling:  
  - **ASGI support** for better performance.  
  - **Auto-reload** for faster development (`reload=True`).  
  - **Host set to 127.0.0.1**, listening on **port 5000**.  
