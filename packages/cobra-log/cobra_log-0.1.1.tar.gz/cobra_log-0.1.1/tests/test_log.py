# tests/test_log.py
from cobra_log import (trace_exc, warning, info)


def test_cobra_log():
    try:
        try:
            raise KeyError("This is the first exception")
        except Exception as e1:
            try:
                raise KeyError(trace_exc("This is the second exception"))
            except Exception as e2:
                raise RuntimeError(trace_exc("This is the main exception", e2, e1))

    except Exception as e:
        warning("An error occurred during the test.", e)
        info("Continuing execution after warning.")
