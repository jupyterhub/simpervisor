"""
asyncio aware version of atexit.

Handles SIGINT and SIGTERM, unlike atexit
"""
import signal
import sys

_handlers = []
_existing_handlers = {}

signal_handler_set = False


def add_handler(handler):
    global signal_handler_set
    if not signal_handler_set:
        # Add handler of SIGINT only if it is not default
        _existing_sigint_handler = signal.getsignal(signal.SIGINT)
        if _existing_sigint_handler.__qualname__ == "default_int_handler":
            _existing_sigint_handler = None
        _existing_handlers.update(
            {
                signal.SIGINT: _existing_sigint_handler,
            }
        )

        # Add handler of SIGTERM only if it is not default
        _existing_sigterm_handler = signal.getsignal(signal.SIGTERM)
        if _existing_sigterm_handler == signal.Handlers.SIG_DFL:
            _existing_sigterm_handler = None
        _existing_handlers.update(
            {
                signal.SIGTERM: _existing_sigterm_handler,
            }
        )

        signal.signal(signal.SIGINT, _handle_signal)
        signal.signal(signal.SIGTERM, _handle_signal)
        signal_handler_set = True
    _handlers.append(handler)


def remove_handler(handler):
    _handlers.remove(handler)


def _handle_signal(signum, *args):
    # Windows doesn't support SIGINT. Replacing it with CTRL_C_EVENT so that it
    # can used with subprocess.Popen.send_signal
    if signum == signal.SIGINT and sys.platform == "win32":
        signum = signal.CTRL_C_EVENT
    for handler in _handlers:
        handler(signum)
    # Finally execute any existing handler that were registered in Python
    # Bail if existing handler is not a callable
    existing_handler = _existing_handlers.get(signum, None)
    if existing_handler is not None and callable(existing_handler):
        existing_handler(signum, None)
    else:
        sys.exit(0)
