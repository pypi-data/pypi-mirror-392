<div align="center">

<h2 id="title">🐱‍👓 cobra-log 🐱‍👓</h2>

[![PyPI version](https://img.shields.io/pypi/v/cobra-log.svg)](https://pypi.org/project/cobra-log/)
![Python](https://img.shields.io/pypi/pyversions/cobra-log.svg)
[![Tests](https://github.com/tinchen777/cobra-log/actions/workflows/test.yml/badge.svg)](https://github.com/tinchen777/cobra-log/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/tinchen777/cobra-log/branch/main/graph/badge.svg)](https://codecov.io/gh/tinchen777/cobra-log)
![License](https://img.shields.io/github/license/tinchen777/cobra-log.svg)

[![Pull Requests Welcome](https://img.shields.io/badge/pull%20requests-welcome-brightgreen.svg)](https://github.com/tinchen777/cobra-log/pulls)
![Github stars](https://img.shields.io/github/stars/tinchen777/cobra-log.svg)

</div>

## About

A lightweight and easy-to-use logging library for Python.

- Python: 3.9+
- Runtime dependency: `cobra-color`.

## Features

- 🚀 Colorful or styled terminal output (`color`, `style`, `plain`).
- 🚀 Optional file persistence with rotation.
- 🚀 Concise exception chaining via `trace_exc`.
- 🚀 Simple, dependency-light design.

## Installation

Stable (once published):

```bash
pip install cobra-log
```

## Quick Start

- Simple warning

  ```python
  from cobra_log import warning

  warning("warning message")
  ```

## Example

```python
from cobra_log import (log_init, info, warning, trace_exc)

# Initialize the log system
log_init("log_save_path", display_type="style")

try:
    try:
        1 / 0  # This will raise a ZeroDivisionError
    except Exception as e1:
        raise RuntimeError(trace_exc("This is the main exception", e1))
except Exception as e:
    warning("A warning occurred.", e)
    info("Continuing execution after warning.")
```

## Requirements

- Python >= 3.9
- cobra-color >= 0.2.5

## License

See LICENSE in the repository.

## Links

- Homepage/Repo: https://github.com/tinchen777/cobra-log.git
- Issues: https://github.com/tinchen777/cobra-log.git/issues
