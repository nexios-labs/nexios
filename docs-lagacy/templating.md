# Jinja2 Integration with Nexios

## Introduction
Jinja2 is a powerful templating engine for Python, widely used for rendering dynamic HTML content. Nexios, as a Python framework, allows seamless integration with Jinja2 for building robust web applications with templating support.

## Installation
To integrate Jinja2 with Nexios, first ensure Jinja2 is installed in your environment:
```bash
pip install Jinja2
```

## Configuring Jinja2 in Nexios
Nexios supports Jinja2 out-of-the-box, but you need to configure the template directory and environment settings. Here’s how you can set it up:

```python
from jinja2 import Environment, FileSystemLoader
import os

# Define the template directory
template_dir = os.path.join(os.path.dirname(__file__), 'templates')

# Create Jinja2 environment
env = Environment(
    loader=FileSystemLoader(template_dir),
    autoescape=True,  # Enables automatic escaping for security
    trim_blocks=True,  # Removes unnecessary whitespace
    lstrip_blocks=True  # Strips leading whitespace inside blocks
)
```

### Explanation of Configuration
- `FileSystemLoader(template_dir)`: Loads templates from the specified directory.
- `autoescape=True`: Ensures safe HTML rendering to prevent XSS attacks.
- `trim_blocks=True` and `lstrip_blocks=True`: Improve readability by removing excess whitespace.

## Rendering Templates in Nexios
Once Jinja2 is set up, you can render templates dynamically within Nexios views.

### Example: Rendering a Simple Template
Assume you have a `index.html` file inside the `templates/` folder:

```html
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
</head>
<body>
    <h1>Welcome to {{ name }}</h1>
</body>
</html>
```

Now, render it inside a Nexios route:

```python
from nexios import get_applcation

app = get_application()
@app.get("/")
def home_view(request, response):
    template = env.get_template('index.html')
    rendered_template = template.render(title='Nexios App', name='Techwithdunamix')
    return response.html(rendered_template, content_type='text/html')
```

## Using Jinja2 Features
Jinja2 provides various features such as:
- **Variables**: `{{ variable }}`
- **Filters**: `{{ name|upper }}` (Converts text to uppercase)
- **Loops**: `{% for user in users %} {{ user }} {% endfor %}` (Iterates over lists)
- **Conditionals**: `{% if is_admin %} Welcome Admin {% endif %}` (Handles logic)
- **Macros**: `{% macro greet(name) %} Hello, {{ name }}! {% endmacro %}` (Reusable components)

### Example: Using Loops and Conditionals

```html
<ul>
    {% for user in users %}
        <li>{{ user.name }} {% if user.is_admin %}(Admin){% endif %}</li>
    {% else %}
        <li>No users found.</li>
    {% endfor %}
</ul>
```

### Example: Using Macros
Macros allow you to create reusable snippets of code.

```html
{% macro user_card(user) %}
    <div class="user">
        <h2>{{ user.name }}</h2>
        <p>Email: {{ user.email }}</p>
    </div>
{% endmacro %}

{{ user_card(current_user) }}
```

## Template Inheritance
Jinja2 supports template inheritance to maintain a consistent layout across pages.

### Example: Base Template (`base.html`)
```html
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Default Title{% endblock %}</title>
</head>
<body>
    <header>
        <h1>My Website</h1>
    </header>
    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

### Extending the Base Template (`home.html`)
```html
{% extends "base.html" %}

{% block title %}Home Page{% endblock %}

{% block content %}
    <p>Welcome to the Home Page!</p>
{% endblock %}
```


