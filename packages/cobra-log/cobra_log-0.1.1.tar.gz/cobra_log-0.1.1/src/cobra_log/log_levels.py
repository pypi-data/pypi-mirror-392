# -*- coding: utf-8 -*-
# Python version: 3.9
# @TianZhen

from __future__ import annotations
from cobra_color import (ctext, smart_print)
from cobra_color.color import ColorStr
from typing import Any

from . import core
from .exceptions import CriticalException
from .utils import (trace_exc, stack_trace)


_EXC_FMT = r" [%(fileName)s->%(funcName)s(%(lineno)d)]"


def _loc_trace(stack_level: Any):
    r"""
    Format the location trace.
    """
    try:
        fmt_level = max(0, int(stack_level))
    except Exception:
        fmt_level = 1

    return stack_trace(
        fmt=_EXC_FMT,
        stack_level=fmt_level
    )


def _display_msg(c_msg: ColorStr):
    r"""
    Output display message according to the current display type.
    """
    if core._DISPLAY_TYPE == "color":
        return c_msg
    elif core._DISPLAY_TYPE == "style":
        return c_msg.style_only
    else:
        return c_msg.plain


def critical(__msg: str = "", *exc: Any, throw: bool = True, loc: bool = True, stack_level: int = 1):
    r"""
    `CRITICAL` exception and `log` record. Stored as `log` requires `log_init()`.

    NOTE: Used when the overall program is not running.

    Parameters
    ----------
        __msg : str, default to `""`
            Description message.

        *exc : Any
            An instance of raised exception. Used to output exception details.

            NOTE: The first exception should be thrown later and the last exception should be thrown earlier.

        throw : bool, default to `True`
            Control whether to throw exception.
            - `True`: throw `CriticalException` exception;
            - `False`: output as `str`.

        loc : bool, default to `True`
            Control whether to display file function location information.

        stack_level : int, default to `1`
            The stack level of the function call.
            - `0`: this function;
            - `1`: the caller of this function;
            - ...

    Returns
    -------
        str
            Formatted message.

    Raises
    ------
        CriticalException
    """
    # exception
    msg = trace_exc(__msg, *exc)
    # log
    if core._FILE_HANDLER:
        core._LOGGER.critical(msg, stack_info=True, stacklevel=2)
    # loc_str
    loc_str = _loc_trace(stack_level) if loc else ""
    # colored message
    c_msg = ctext(f"CRITICAL-ERROR{loc_str}: {msg}", fg="w", bg="r", styles={"bold"})

    if throw:
        raise CriticalException(_display_msg(c_msg))

    return c_msg.plain


def error(__msg: str = "", *exc: Any, stack_info: bool = False, throw: bool = True, loc: bool = True, stack_level: int = 1):
    r"""
    `ERROR` exception and `log` record. Stored as `log` requires `log_init()`.

    NOTE: Used when some functions are not running.

    Parameters
    ----------
        __msg : str, default to `""`
            Description message.

        *exc : Any
            An instance of raised exception. Used to output exception details.

            NOTE: The first exception should be thrown later and the last exception should be thrown earlier.

        stack_info : bool, default to `False`
            Control whether to display stack information.

        throw : bool, default to `True`
            Control whether to throw exception.
            - `True`: Print the error exception;
            - `False`: Output as `str`.

        loc : bool, default to `True`
            Control whether to display file function location information.

        stack_level : int, default to `1`
            The stack level of the function call.
            - `0`: this function;
            - `1`: the caller of this function;
            - ...

    Returns
    -------
        str
            Formatted message.
    """
    # exception
    msg = trace_exc(__msg, *exc)
    # log
    if core._FILE_HANDLER:
        core._LOGGER.error(msg, stack_info=stack_info, stacklevel=2)
    # loc_str
    loc_str = _loc_trace(stack_level) if loc else ""
    # colored message
    c_msg = ctext(f"ERROR{loc_str}: {msg}", fg="d", bg="y", styles={"bold"})

    if throw:
        smart_print(_display_msg(c_msg))

    return c_msg.plain


def warning(__msg: str = "", *exc: Any, throw: bool = True, loc: bool = True, dim: bool = False, stack_level: int = 1):
    r"""
    `WARNING` exception and `log` record. Stored as `log` requires `log_init()`.

    NOTE: Used when unexpected events occur, and the program can still run normally.

    Parameters
    ----------
        __msg : str, default to `""`
            Description message.

        *exc : Any
            An instance of raised exception. Used to output exception details.

            NOTE: The first exception should be thrown later and the last exception should be thrown earlier.

        throw : bool, default to `True`
            Control whether to throw exception.
            - `True`: Print the warning exception;
            - `False`: Output as `str`.

        loc : bool, default to `True`
            Control whether to display file function location information.

        dim : bool, default to `False`
            Control whether to dim the warning message.

        stack_level : int, default to `1`
            The stack level of the function call.
            - `0`: this function;
            - `1`: the caller of this function;
            - ...

    Returns
    -------
        str
            Formatted message.
    """
    # exception
    msg = trace_exc(__msg, *exc)
    # log
    if core._FILE_HANDLER:
        core._LOGGER.warning(msg, stacklevel=2)
    # loc_str
    loc_str = _loc_trace(stack_level) if loc else ""
    # colored message
    c_msg = ctext(f"WARNING{loc_str}: {msg}", fg="y", styles=None if dim else {"bold"})

    if throw:
        smart_print(_display_msg(c_msg))

    return c_msg.plain


def info(__msg: str = "", *exc: Any, level: int = 1, throw: bool = True, outline: bool = False, end: str = "", loc: bool = True, stack_level: int = 1):
    r"""
    `INFO` exception and `log` record. Stored as `log` requires `log_init()`.

    NOTE: Used to record key node information.

    Parameters
    ----------
        __msg : str, default to `""`
            Description message.

        *exc : Any
            An instance of raised exception. Used to output exception details.

            NOTE: The first exception should be thrown later and the last exception should be thrown earlier.

        level : int, default to `1`
            The indentation level of the information. Level `1` is the topest level without indentation.

        throw : bool, default to `True`
            Control whether to throw exception.
            - `True`: Print the info exception;
            - `False`: Output as `str`.

        outline : bool, default to `False`
            Control whether to emphasize the color of the information.

        end : str, default to `""`
            The end string of the information.

        loc : bool, default to `True`
            Control whether to display file function location information.

        stack_level : int, default to `1`
            The stack level of the function call.
            - `0`: this function;
            - `1`: the caller of this function;
            - ...

    Returns
    -------
        str
            Formatted message.
    """
    # exception
    msg = trace_exc(__msg, *exc)
    # log
    if core._FILE_HANDLER:
        core._LOGGER.info(msg, stacklevel=2)
    # loc_str
    loc_str = _loc_trace(stack_level) if loc else ""
    # style
    level = int(max(1, level))
    if level == 1:
        font = "m" if outline else "g"
        prefix = ""
    else:
        font = "m" if outline else None
        prefix = f"{'    '*(level-2)} |--"
    # colored message
    c_msg = ctext(f"{prefix}INFO{loc_str}: {msg}{end}", fg=font, styles={"bold"})

    if throw:
        smart_print(_display_msg(c_msg))

    return c_msg.plain


def debug(*args: Any, **kwargs: Any):
    r"""
    `DEBUG` exception and `log` record. Stored as `log` requires `log_init()`.

    NOTE: Used for debugging.
    """
    msg = ""
    for arg in args:
        msg += f"\n{arg}"
    for arg_name, arg_val in kwargs.items():
        msg += f"\n[{arg_name}]: {arg_val}"
    # log
    if core._FILE_HANDLER and msg:
        core._LOGGER.debug(msg, stacklevel=2)
