# -*- coding: utf-8 -*-
# Python version: 3.9
# @TianZhen

import inspect
import os
import re
from cobra_color import (ctext, smart_print)
from typing import Any

from . import core


_TRACE_FMT = r"%(fileName)s->%(funcName)s(%(lineno)d)"
_END_SYMBOLS = (".", "!", "?", "。", "！", "？")


def trace_exc(__msg: Any, *exc: Exception):
    r"""
    Format a statement with message and instances of raised exception. Just like:

    Parameters
    ----------
        __msg : Any
            Description message.

        *exc : Exception
            An instance of raised exception.

            NOTE: The first exception should be thrown later and the last exception should be thrown earlier.

    Usages
    ------
    >>> from cobra_log import trace_exc
    >>>
    >>> try:
    >>>     raise ValueError("exception 1")
    >>> except Exception as e1:
    >>>     try:
    >>>         l = []
    >>>         l[1]  # This will raise an IndexError
    >>>     except Exception as e2:
    >>>         raise RuntimeError(trace_exc("exception 3", e2, e1))

    - The output is:
    >>> RuntimeError: exception 3.
    >>>     2=> <IndexError> list index out of range.
    >>>     1=> <ValueError> exception 1

    Returns
    -------
        str
            Formatted string.
    """
    # message
    msg = str(__msg)
    if not msg.endswith(_END_SYMBOLS):
        msg += "."

    for idx, e in enumerate(exc):
        # exception string
        exc_str = str(e).strip('"').encode().decode('unicode_escape')
        if "\n" in exc_str and "=>" in exc_str:
            # exist traced exceptions
            exc_str = exc_str.replace("\n", "\n    ")
            exc_styles = ()
        else:
            # no traced exceptions
            if not exc_str.endswith(_END_SYMBOLS):
                exc_str += "."
            if idx == len(exc) - 1:
                exc_styles = {"bold", "selected"}
            else:
                exc_styles = {"bold"}
        # arrow
        if len(exc) == 1:
            if core._DISPLAY_TYPE == "plain":
                arrow = "\n     => "
            else:
                arrow = ctext("\n    ", styles={"disappear"}) + ctext(" => ", styles={"bold"})
        else:
            idx_str = str(len(exc) - idx)
            if core._DISPLAY_TYPE == "plain":
                arrow = f"\n     {idx_str}=> "
            else:
                arrow = ctext("\n    ", styles={"disappear"}) + ctext(f" {idx_str}=> ", styles={"bold"})
            exc_str = re.sub(r"(\d?=>)", lambda m: idx_str + m.group(1), exc_str)

        # traceback
        tb = e.__traceback__
        tb_str = f": {os.path.basename(tb.tb_frame.f_code.co_filename)}({tb.tb_lineno})" if tb else ""
        tb_detail_str = f"<{e.__class__.__name__}{tb_str}> "
        tb_detail = tb_detail_str if core._DISPLAY_TYPE == "plain" else ctext(tb_detail_str, styles={"italic", *exc_styles})

        exc_ = exc_str if core._DISPLAY_TYPE == "plain" else ctext(exc_str, styles=exc_styles)

        msg += f"{arrow}{tb_detail}{exc_}"

    return msg


def stack_trace(fmt: str = _TRACE_FMT, stack_level: int = 1):
    r"""
    Trace the stack information of the function call.

    Parameters
    ----------
        fmt : str, default to TRACE_FMT
            The format string, `TRACE_FMT` is defined as `r"%(fileName)s->%(funcName)s(%(lineno)d)"`.
            Includes:
            - `%(stackDepth)d`: stack depth;
            - `%(funcName)s`: function name;
            - `%(filePath)s`: file path;
            - `%(fileName)s`: file name;
            - `%(lineno)d`: line number;
            - `%(funcLineno)d`: function start line number.

        stack_level : int, default to `1`
            The stack level of the function call.
            - `0`: this function;
            - `1`: the caller of this function;
            - ...

    Returns
    -------
        str
            Formatted stack information.
    """
    text = ""
    try:
        total_stack = inspect.stack()
        frame_info = total_stack[stack_level][0]
        total_depth = len(total_stack)  # total stack depth

        stackDepth = total_depth - stack_level  # current stack depth
        funcName = frame_info.f_code.co_name  # current function name
        filePath = frame_info.f_code.co_filename  # current file path
        fileName = os.path.basename(filePath)  # current file name
        lineno = int(frame_info.f_lineno)  # current line number
        funcLineno = frame_info.f_code.co_firstlineno  # function start line number

        text = fmt % {"stackDepth": stackDepth, "funcName": funcName, "filePath": filePath, "fileName": fileName, "lineno": lineno, "funcLineno": funcLineno}

    except KeyError as e:
        smart_print(ctext(f"ERROR: Can Not Match [{e}] In Stack Trace Format [{fmt}].", fore="d", styles={"bold"}, back="y"))
    except Exception as e:
        smart_print(ctext(f"ERROR: Get Stack Trace Error. <{e.__class__.__name__}> {e}", fore="d", styles={"bold"}, back="y"))

    return text
