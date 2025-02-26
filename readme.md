:  

---

#  Nexios – The Future of Python Frameworks!  

<p align="center">
  <img src="./docs/nexiohero.png" width="1000" alt="Nexios Logo"/>
</p>  

### 🌟 The lightweight, blazing-fast Python framework you've been waiting for!  

[![GitHub stars](https://github.com/nexios-labs/Nexios?style=for-the-badge)](https://github.com/nexios-labs/Nexios)  
[![PyPI Downloads](https://img.shields.io/pypi/dm/nexios?style=for-the-badge)](https://pypi.org/project/nexios/)  
[![Documentation](https://img.shields.io/badge/Docs-Read%20Now-blue?style=for-the-badge)](https://nexios-labs.github.io/Nexios/)  

## ⚡ What is Nexios?  
Think **FastAPI meets Express.js** but with its own **swagger**!  Nexios is a modern Python framework designed to help you **build, deploy, and scale** applications **effortlessly**.  

✅ **Super lightweight** – No unnecessary bloat!  
✅ **Crazy fast** 🚀 – Like, seriously!  
✅ **Insanely flexible** – Works with any ORM.  
✅ **Multiple authentication types** – Because security matters!  

## 🛠 Installation  
```bash
pip install nexios
```

## 🚀 Quick Start  

### 1️⃣ Create a New Nexios Project  
```bash
nexios create
cd <myapp>
```

### 2️⃣ Follow the Instructions  
The CLI will guide you through setting up your project structure.  

### 3️⃣ Expand
```bash
nexios run --reload
```

### 4️⃣ Run Your App  
```py
from nexios import get_application
app = get_application()
@app.get("/users")
async def get_users(request,response):
    return response.json({"users": ["Alice", "Bob"]})
```
## 🤯 Nexios vs. The World  
| Feature      | Nexios 🚀 | FastAPI ⚡ | Django 🏗 | Flask 🍶 |
|-------------|----------|----------|---------|--------|
| Speed       | ⚡⚡⚡⚡⚡  | ⚡⚡⚡⚡  | ⚡⚡  | ⚡⚡⚡  |
| Ease of Use | ✅✅✅✅✅ | ✅✅✅✅ | ✅✅✅ | ✅✅✅✅ |
| ORM Support | Any! | SQLAlchemy | Django ORM | SQLAlchemy |
| Async Support | ✅ | ✅ | ❌ (Django 4.1+ has partial) | ❌ |
| Authentication | ✅  | ✅ | ✅ | ❌ |
| Built-in Admin Panel | Coming Soon | ❌ | ✅ | ❌ |
| Best For | APIs & Full Apps | APIs | Full-stack Web Apps | Small Apps |

## 📖 Read the Full Documentation  
👉  <a href="https://github.com/nexios-labs/Nexios/">https://github.com/nexios-labs/Nexios</a>

## ⭐ Star Nexios on GitHub!  
If you love **Nexios**, show some ❤️ by **starring** the repo!  

🔗 [**GitHub Repo**](https://github.com/nexios-labs/Nexios)  

---

