# Ushka

[![PyPI Version](https://img.shields.io/pypi/v/ushka)](https://pypi.org/project/ushka/)
![Python Versions](https://img.shields.io/pypi/pyversions/ushka)
![License](https://img.shields.io/pypi/l/ushka)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Build](https://img.shields.io/github/actions/workflow/status/kleber-code/ushka/python-publish.yml?branch=main)](https://github.com/kleber-code/ushka/actions)

**Ushka** is a minimal, experimental Python ASGI web framework focused on **file-based routing**. It turns your filesystem into your API.

---

## ⚠️ Alpha Stage

This project is in **early alpha**. Expect breaking changes. Not for production use.

---

## Installation

Install via pip:

```bash
pip install ushka
````

---

## Core Idea: File-Based Routing

Ushka automatically maps Python files in a `routes/` directory to URL endpoints:

* `routes/index.py` → `/`
* `routes/hello.py` → `/hello`
* `routes/api/v1/status.py` → `/api/v1/status`
* Dynamic paths: `routes/users/[id].py` → `/users/<id>`
* HTTP method = function name (`get()`, `post()`, etc.)

No decorators. No config. The filesystem is the API.

---

## Example Project

### Structure

```
examples/
├── app.py
└── routes/
    ├── index.py
    ├── hello.py
    └── hello/
        └── [name].py
```

### Route Handlers

**`routes/index.py`**

```python
def get():
    return "Welcome to the autodiscovered example!"
```

**`routes/hello.py`**

```python
def get():
    return "Hello, World!"
```

**`routes/hello/[name].py`**

```python
def get(name: str):
    return f"Hello, {name}!"
```

### Application Entry Point

**`app.py`**

```python
from ushka import Ushka

app = Ushka()

if __name__ == "__main__":
    print("Starting Ushka server on http://127.0.0.1:8000")
    app.run("127.0.0.1", 8000)
```

### Run

```bash
python examples/app.py
```

Then make requests:

* `GET /` → "Welcome to the autodiscovered example!"
* `GET /hello` → "Hello, World!"
* `GET /hello/<name>` → "Hello, <name>!"

---

## Manual Routing (Optional)

If you prefer explicit control:

```python
from ushka import Ushka

app = Ushka()

def handler():
    return "Manual route"

app.router.add_route("GET", "/manual", handler)
```

---

## Roadmap

* Improve routing (static + dynamic)
* Request/Response objects
* Middleware support
* CLI for scaffolding
* Basic DI system

---

## License

MIT
