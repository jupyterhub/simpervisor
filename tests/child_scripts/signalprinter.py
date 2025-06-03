"""
Print received SIGTERM & SIGINT signals
"""

import asyncio
import signal
import sys
from functools import partial

from simpervisor.atexitasync import add_handler


def _non_default_handle(sig, frame):
    # Print the received signum and then exit
    print(f"non default handler received {sig}", flush=True)
    sys.exit(0)


def _handle_sigterm(number, received_signum):
    # Print the received signum so we know our handler was called
    print(f"handler {number} received", int(received_signum), flush=True)


handlercount = int(sys.argv[1])
# Add non default handler if arg true is passed
if len(sys.argv) == 3:
    if bool(sys.argv[2]):
        signal.signal(signal.SIGINT, _non_default_handle)
        signal.signal(signal.SIGTERM, _non_default_handle)
for i in range(handlercount):
    add_handler(partial(_handle_sigterm, i))

loop = asyncio.get_event_loop()
try:
    loop.run_forever()
finally:
    # Cleanup properly so we get a clean exit
    try:
        remaining_tasks = asyncio.all_tasks(loop=loop)
    except AttributeError:
        # asyncio.all_tasks was added in 3. Provides reverse compatability.
        remaining_tasks = asyncio.Task.all_tasks(loop=loop)
    loop.run_until_complete(asyncio.gather(*remaining_tasks))
    loop.close()
