---
icon: down-to-line
---

# Getting Started  <Badge type="tip" text="2.4.0" />

Nexios is simple to install , no stress !

::: tip
Nexios Requires Python 3.9+
:::



## ⬇️ Install 
install With pip :

```sh
pip install nexios

pip install nexios[granian] # Install Nexios with optional Granian support
```

::: info 😎 Tip
Use a virtual environment to manage project dependencies.
:::

**____________________or poetry____________________**

```bash
poetry add nexios
```


## Your First Nexios App
**main.py**
```py
from nexios import NexiosApp

app = NexiosApp()

@app.get("/")
async def index(request, response) :
    return {"Message" : "Nexios is working 🚀"}

```



Awesome, that was easy.

Building a complex application typically involves much more code than this simple example. One common challenge is managing multiple files, asynchronous initialization, and designing a scalable architecture.


::: details Check Out this cool this stuff
Nexios come with `get_application` function that return a ready NexiosApp  with middleware like Session,Cors
```py {2}
from nexios import get_application
app = get_application()

```
:::

Now Use `nexios run` to run your app

```bash
nexios run
```
Visit http://localhost:4000/docs to view the Swagger API documentation.

Alternatively you can use `uvicorn main:app`

```bash
uvicorn main:app --reload
```

Visit http://localhost:8000/docs to view the Swagger API documentation.

## Managing Configuration

Nexios uses a `MakeConfig` class that you can use to manage your application's configuration.

```py
from nexios import MakeConfig

config = MakeConfig({
    "debug" : True
})

app = NexiosApp(config=config)


```

And Thats it ! 🚀