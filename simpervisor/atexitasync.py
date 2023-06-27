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
        # First get existing signal handlers for SIGINT and SIGTERM
        # If no handlers are defined in Python, getsignal will return None
        _existing_handlers.update(
            {
                signal.SIGINT: signal.getsignal(signal.SIGINT),
                signal.SIGTERM: signal.getsignal(signal.SIGTERM),
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
    existing_handler = _existing_handlers.get(signum, None)
    if existing_handler is not None:
        existing_handler(signum, None)
    else:
        sys.exit(0)
