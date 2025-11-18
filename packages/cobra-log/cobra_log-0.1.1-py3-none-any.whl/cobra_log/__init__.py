# src/cobra_log/__init__.py
"""
cobra-log
----

A lightweight and easy-to-use logging library for Python.

_Example:_

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
"""

from . import exceptions

from .core import (log_init, display_use, exception)
from .log_levels import (critical, error, warning, info, debug)
from .utils import (trace_exc, stack_trace)


__author__ = "Zhen Tian"
__version__ = "0.1.1"

__all__ = [
    "exceptions",  # module
    "log_init",
    "display_use",
    "exception",
    "critical",
    "error",
    "warning",
    "info",
    "debug",
    "trace_exc",
    "stack_trace"
]
