# krag-mathlib

`krag-mathlib` is a Python library for performing mathematical operations like addition, subtraction, and more.

---

## 📑 Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Development Workflow](#development-workflow)

   * [Run Tests](#1-pytest--q---run-your-tests)
   * [Editable Install](#2-pip-install-e---editable-install-development-mode)
   * [Build Package](#3-python--m-build---create-release-artifacts)
4. [Publishing](#publishing)
5. [Usage](#usage)
6. [Contributing](#contributing)
7. [License](#license)

---

## Introduction

`krag-mathlib` provides a clean and simple interface for performing common mathematical operations. It is designed for Python developers who want a lightweight, easy-to-use library for basic calculations.

---

## Installation

Install the package from PyPI:

```bash
pip install krag-mathlib
```

For development with optional dependencies (for testing, etc.):

```bash
pip install .[dev]
```

---

## Development Workflow

### 1. `pytest -q` — Run your tests

Run:

```bash
pytest -q
```

Use it to test your package code during:

* Development
* Before committing
* Before releasing/publishing

This ensures your package works correctly in your local environment.

---

### 2. `pip install -e .` — Editable install (development mode)

Run:

```bash
pip install -e .
```

Use editable mode to:

* Use the package in another project
* Test imports without reinstalling
* Develop multiple packages simultaneously

Changes in:

```
src/krag_mathlib/
```

are immediately reflected everywhere Python imports `krag_mathlib`.

---

### 3. `python -m build` — Create release artifacts

Run:

```bash
python -m build
```

This creates:

```
dist/krag_mathlib-0.1.0-py3-none-any.whl
" +
"dist/krag_mathlib-0.1.0.tar.gz
```

Use this before:

* Releasing on GitHub
* Publishing to PyPI
* Sharing the library

---

## Publishing

### PyPI

```bash
twine upload dist/*
```

### GitHub

* Upload wheel + tar.gz to a release

---

## Usage

Install from PyPI:

```bash
pip install krag-mathlib
```

Then use in your code:

```python
from krag_mathlib import add, subtract

def main():
    a = 10
    b = 5

    sum_result = add(a, b)
    diff_result = subtract(a, b)

    print(f"The sum of {a} and {b} is: {sum_result}")
    print(f"The difference when {b} is subtracted from {a} is: {diff_result}")

if __name__ == "__main__":
    main()
```

**Note:** The PyPI package name is `krag-mathlib`, but the import is `krag_mathlib` (matching the internal folder name).

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests:

```bash
pytest -q
```

5. Submit a pull request

---

## License

This project is licensed under the MIT License.
