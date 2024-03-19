"""
asyncio aware version of atexit.

Handles SIGINT and SIGTERM, unlike atexit
"""

import signal
import sys

_handlers = []

_prev_handlers = {}
signal_handler_set = False


def add_handler(handler):
    """
    Adds a signal handler function that will be called when the Python process
    receives either a SIGINT (on windows CTRL_C_EVENT) or SIGTERM signal.
    """
    _ensure_signal_handlers_set()
    _handlers.append(handler)


def remove_handler(handler):
    """Removes previously added signal handler."""
    _handlers.remove(handler)


def _ensure_signal_handlers_set():
    """
    Ensures _handle_signal is registered as a top level signal handler for
    SIGINT and SIGTERM and saves previously registered non-default Python
    callable signal handlers.
    """
    global signal_handler_set
    if not signal_handler_set:
        # save previously registered non-default Python callable signal handlers
        #
        # windows note: signal.getsignal(signal.CTRL_C_EVENT) would error with
        # "ValueError: signal number out of range", and
        # signal.signal(signal.CTRL_C_EVENT, _handle_signal) would error with
        # "ValueError: invalid signal value".
        #
        prev_sigint = signal.getsignal(signal.SIGINT)
        prev_sigterm = signal.getsignal(signal.SIGTERM)
        if callable(prev_sigint) and prev_sigint.__qualname__ != "default_int_handler":
            _prev_handlers[signal.SIGINT] = prev_sigint
        if callable(prev_sigterm) and prev_sigterm != signal.Handlers.SIG_DFL:
            _prev_handlers[signal.SIGTERM] = prev_sigterm

        # let _handle_signal handle SIGINT and SIGTERM
        signal.signal(signal.SIGINT, _handle_signal)
        signal.signal(signal.SIGTERM, _handle_signal)
        signal_handler_set = True


def _handle_signal(signum, *args):
    """
    Calls functions added by add_handler, and then calls the previously
    registered non-default Python callable signal handler if there were one.
    """
    prev_handler = _prev_handlers.get(signum)

    # Windows doesn't support SIGINT. Replacing it with CTRL_C_EVENT so that it
    # can used with subprocess.Popen.send_signal
    if signum == signal.SIGINT and sys.platform == "win32":
        signum = signal.CTRL_C_EVENT

    for handler in _handlers:
        handler(signum)

    # call previously registered non-default Python callable handler or exit
    if prev_handler:
        prev_handler(signum, *args)
    else:
        sys.exit(0)
