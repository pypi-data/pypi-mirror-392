# NNL — Near Natural Language

### A Human-Readable, JSON-Compatible Data Language

![Status](https://img.shields.io/badge/status-active-brightgreen)
![Python](https://img.shields.io/badge/language-python-blue)
![License](https://img.shields.io/badge/license-MIT-purple)

---

## 🌱 What is NNL?

**NNL (Near Natural Language)** is a human-friendly, indentation-based data notation that looks like simple English sentences but maps **1:1 to JSON**.

Write this:

```
user contains:
name is Alice.
age is 30.
roles are admin, editor.
```

And get this JSON:

```json
{
  "user": {
    "name": "Alice",
    "age": 30,
    "roles": ["admin", "editor"]
  }
}
```

NNL is perfect for:

* Configuration files
* API payloads
* Human-editable datasets
* Documentation / examples
* Structured content

---

## ✨ Features

* **Full JSON compatibility**
* **Human-readable, minimal punctuation**
* Natural English-like syntax
* Supports:

  * objects (`contains:`)
  * arrays (`are:`)
  * inline lists (`a, b, c`)
  * arrays of objects
  * nested structures
  * numbers, strings, booleans, null
* Round-trip safe (NNL → JSON → NNL)

---

## 🔧 Installation

After publishing to PyPI:

```bash
pip install nnlpy
```

Local development install:

```bash
pip install -e .
```

---

## 🧪 Usage (Python)

```python
from nnl import parse_nnl, dump_nnl

text = """
user contains:
  name is Alice.
  age is 22.
  roles are admin, editor.
"""

data = parse_nnl(text)
print(data)
# {'user': {'name': 'Alice', 'age': 22, 'roles': ['admin', 'editor']}}

print(dump_nnl(data))
```

---

## 📝 CLI Usage

After install, the command `nnl` becomes available:

### NNL ➜ JSON

```bash
nnl nnl2json file.nnl
```

Or via stdin:

```bash
type file.nnl | nnl nnl2json -
```

### JSON ➜ NNL

```bash
nnl json2nnl file.json
```

---

## 📚 Language Basics

### Objects

```
project contains:
  name is Atlas.
  version is 1.0.
```

### Inline Lists

```
tags are alpha, beta, gamma.
```

### Block Lists

```
items are:
  - apple.
  - banana.
  - cherry.
```

### Arrays of Objects

```
users are:
  - contains:
      id is 1.
      name is Alice.
  - contains:
      id is 2.
      name is Bob.
```

### Nested Lists (Matrices)

```
matrix are:
  - 1, 2, 3.
  - 4, 5, 6.
```

---

## 📄 Documentation

See the `docs` directory:

* **spec.md** — Official NNL Specification v1.0
* **examples.md** — Practical examples & patterns

---

## 🧪 Testing

Run the test suite:

```bash
pytest -q
```

---

## 🔨 Development

### Install dependencies

```bash
pip install -e . pytest
```

### Project Structure

```
nnl/
 ├── nnl/
 │    ├── __init__.py
 │    ├── core.py
 │    ├── cli.py
 ├── tests/
 │    ├── test_nnl_basic.py
 ├── docs/
 │    ├── spec.md
 │    ├── examples.md
 ├── example.nnl
 ├── pyproject.toml
 ├── README.md
 ├── LICENSE
 ├── CONTRIBUTING.md
```

---

## 🚀 Publishing (PyPI)

Build:

```bash
python -m build
```

Upload:

```bash
twine upload dist/*
```

---

## 🤝 Contributing

Pull requests and issues are welcome.
NNL is designed to be readable, stable, and easy to extend.

---

## 📜 License

MIT License
See `LICENSE` for details.
