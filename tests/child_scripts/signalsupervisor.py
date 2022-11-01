"""
Start a child process that prints signals it receives
"""
import asyncio
import os
import sys

from simpervisor import SupervisedProcess

signal_printer = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "signalprinter.py"
)


async def main():
    count = int(sys.argv[1])
    pids = []
    for i in range(count):
        proc = SupervisedProcess(
            f"signalprinter-{i}", *[sys.executable, signal_printer, "1"]
        )

        await proc.start()
        pids.append(proc.pid)

    print(" ".join([str(pid) for pid in pids]), flush=True)


loop = asyncio.get_event_loop()
asyncio.ensure_future(main())
try:
    loop.run_forever()
finally:
    # Cleanup properly so we get a clean exit
    remaining_tasks = asyncio.all_tasks(loop=loop)
    loop.run_until_complete(asyncio.gather(*remaining_tasks))
    loop.close()
    print("supervisor exiting cleanly")
