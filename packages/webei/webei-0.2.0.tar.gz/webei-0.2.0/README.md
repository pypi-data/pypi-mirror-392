# Webei UI Kit (Python)

`webei` is a revolutionary UI kit that allows you to design and build beautiful, modern web frontends entirely within Python. Forget about switching between HTML, CSS, and JavaScript. Describe your UI with simple, human-readable Python code, and `webei` will generate the necessary HTML and scoped CSS for you.

This new version focuses on ultimate flexibility and a magical, DSL-like experience.

## Features

- **Python-Native:** Design UIs using Python objects and functions. No HTML/CSS required.
- **Ultimate Flexibility:** Style any standard HTML element with any CSS property, directly from Python.
- **Human-Readable:** Use intuitive arguments like `font_size="2rem"` or `shadow="large"`.
- **Component-Based:** Comes with helpful pre-styled components like `Card` and `Button`, or build your own from `div`s.
- **Scoped Styles:** The engine automatically generates scoped CSS, so you don't have to worry about class name conflicts.
- **Magic Activation:** A simple `act()` call injects all the necessary tools into your environment.

## Installation

(This package is not on PyPI yet. To install locally for development:)
```bash
# Run this from the webei/pip directory
pip install -e .
```

## How to Use

The new `webei` is incredibly simple.

1.  **Activate Webei:**
    Call `act()` at the top of your script. This magically makes all the component functions (`p`, `c`, `div`, `h1`, etc.) available.

2.  **Build Your UI:**
    Compose your UI by calling and nesting component functions. A `p()` (Page) component is usually your root.

3.  **Render:**
    Call the `.render()` method on your root component to generate the final HTML document.

Here's a minimal example with Flask:

```python
from flask import Flask
from webei import act

# 1. Activate the Webei magic!
act()

app = Flask(__name__)

@app.route('/')
def home():
    # 2. Build the UI entirely in Python
    my_ui = p(  # p is an alias for Page
        div(
            h1("Hello from Webei!", text_align="center"),
            c(  # c is an alias for Card
                para("This is a card component."),
                shadow="large",
                margin_top="20px"
            ),
            padding="2rem"
        )
    )

    # 3. Render the UI to an HTML string
    return my_ui.render()

if __name__ == '__main__':
    app.run(debug=True)
```

### Available Components & Tags

After calling `act()`, you have access to:

- **High-Level Components:** `Page`, `Card`, `Button`, `Text`.
- **Aliases:** `p` (for `Page`), `c` (for `Card`).
- **Standard HTML Tags:** `div`, `h1`-`h6`, `a`, `img`, `span`, `section`, `header`, `footer`, `nav`, `ul`, `li`, `form`, `input`, `textarea`, and more. `p` is aliased to `para` to avoid conflict with the `Page` alias.

### Styling

Style any element by passing keyword arguments. `webei` automatically converts them to CSS.

```python
div(
    "I'm a styled div!",
    background_color="#eef",
    border_left="5px solid #aae",
    padding="20px",
    font_family="monospace"
)
```