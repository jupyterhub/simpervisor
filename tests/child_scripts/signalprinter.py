"""
Print received SIGTERM & SIGINT signals
"""
import asyncio
import signal
from functools import partial
import sys
from simpervisor import atexitasync 

def _handle_sigterm(number, received_signum):
    # Print the received signum so we know our handler was called
    print(f"handler {number} received", int(received_signum), flush=True)

handlercount = int(sys.argv[1])
for i in range(handlercount):
    atexitasync.add_handler(partial(_handle_sigterm, i))

loop = asyncio.get_event_loop()
try:
    loop.run_forever()
finally:
    # Cleanup properly so we get a clean exit
    loop.run_until_complete(asyncio.gather(*asyncio.Task.all_tasks()))
    loop.close()