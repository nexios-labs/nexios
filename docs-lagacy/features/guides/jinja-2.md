---
icon: css3
---

# Jinja 2

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

* `FileSystemLoader(template_dir)`: Loads templates from the specified directory.
* `autoescape=True`: Ensures safe HTML rendering to prevent XSS attacks.
* `trim_blocks=True` and `lstrip_blocks=True`: Improve readability by removing excess whitespace.

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

* **Variables**: `{{ variable }}`
* **Filters**: `{{ name|upper }}` (Converts text to uppercase)
* **Loops**: `<div data-gb-custom-block data-tag="for"> {{ user }} </div>` (Iterates over lists)
* **Conditionals**: `<div data-gb-custom-block data-tag="if"> Welcome Admin </div>` (Handles logic)
* **Macros**: `<div data-gb-custom-block data-tag="macro"> Hello, {{ name }}! </div>` (Reusable components)

### Example: Using Loops and Conditionals

```html
<ul>
    <div data-gb-custom-block data-tag="for">
        <li>{{ user.name }} <div data-gb-custom-block data-tag="if">(Admin)</div></li>
    <div data-gb-custom-block data-tag="else"></div>
        <li>No users found.</li>
    </div>


</ul>
```

### Example: Using Macros

Macros allow you to create reusable snippets of code.

```html

<div data-gb-custom-block data-tag="macro">


    <div class="user">
        <h2>{{ user.name }}</h2>
        <p>Email: {{ user.email }}</p>
    </div>

</div>

{{ user_card(current_user) }}
```

## Template Inheritance

Jinja2 supports template inheritance to maintain a consistent layout across pages.

### Example: Base Template (`base.html`)

```html
<!DOCTYPE html>
<html>
<head>
    <title><div data-gb-custom-block data-tag="block">Default Title</div></title>
</head>
<body>
    <header>
        <h1>My Website</h1>
    </header>
    <main>
        <div data-gb-custom-block data-tag="block"></div>


    </main>
</body>
</html>
```

### Extending the Base Template (`home.html`)

```html

<div data-gb-custom-block data-tag="extends" data-0='base.html'></div>




<div data-gb-custom-block data-tag="block">Home Page</div>




<div data-gb-custom-block data-tag="block">


    <p>Welcome to the Home Page!</p>

</div>
```
