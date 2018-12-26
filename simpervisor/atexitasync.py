"""
asyncio aware version of atexit.

Handles SIGINT and SIGTERM, unlike atexit
"""
import signal
import asyncio
import sys

_handlers = []

signal_handler_set = False

def add_handler(handler):
    global signal_handler_set
    if not signal_handler_set:
        loop = asyncio.get_event_loop()
        loop.add_signal_handler(signal.SIGINT, _handle_signal, signal.SIGINT)
        loop.add_signal_handler(signal.SIGTERM, _handle_signal, signal.SIGTERM)
        signal_handler_set = True
    _handlers.append(handler)

def remove_handler(handler):
    _handlers.remove(handler)

def _handle_signal(signum):
    for handler in _handlers:
        handler(signum)
    sys.exit(0)