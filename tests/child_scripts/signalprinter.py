"""
Print received SIGTERM & SIGINT signals
"""
import asyncio
import sys
from functools import partial

from simpervisor.atexitasync import add_handler


def _handle_sigterm(number, received_signum):
    # Print the received signum so we know our handler was called
    print(f"handler {number} received", int(received_signum), flush=True)


handlercount = int(sys.argv[1])
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
