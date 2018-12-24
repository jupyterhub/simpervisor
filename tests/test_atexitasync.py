import asyncio
import pytest
import subprocess
from textwrap import dedent
from simpervisor import atexitasync 
import sys
import signal
import os
import time


@pytest.mark.parametrize('signum', [signal.SIGTERM, signal.SIGINT])
def test_sigterm(signum):
    CHILD_CODE = dedent(f"""
    import asyncio
    import signal
    import sys
    from simpervisor import atexitasync 
    def _handle_sigterm(received_signum):
        # Print the received signum so we know our handler was called
        print("Received", int(received_signum), flush=True)
    atexitasync.add_handler(_handle_sigterm)
    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    finally:
        # Cleanup properly so we get a clean exit
        loop.run_until_complete(asyncio.gather(*asyncio.Task.all_tasks()))
        loop.close()
    """)
    proc = subprocess.Popen([sys.executable, '-c', CHILD_CODE], stdout=subprocess.PIPE)

    # Give the process time to register signal handlers
    time.sleep(0.2)
    proc.send_signal(signum)

    # Make sure the signal is handled by our handler in the code
    stdout, stderr = proc.communicate()
    assert stdout.decode() == f"Received {signum}\n"

    # The code should exit cleanly
    retcode = proc.wait()
    assert retcode == 0