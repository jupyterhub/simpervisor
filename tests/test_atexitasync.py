import os
import signal
import subprocess
import sys
import time

import pytest


@pytest.mark.parametrize(
    "signum, handlercount",
    [
        (signal.SIGTERM, 1),
        (signal.SIGINT, 1),
        (signal.SIGTERM, 5),
        (signal.SIGINT, 5),
    ],
)
@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Testing signals on Windows doesn't seem to be possible",
)
def test_atexitasync(signum, handlercount):
    """
    Test signal handlers receive signals properly
    """
    signalprinter_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "child_scripts", "signalprinter.py"
    )
    proc = subprocess.Popen(
        [sys.executable, signalprinter_file, str(handlercount)],
        stdout=subprocess.PIPE,
        text=True,
    )

    # Give the process time to register signal handlers
    time.sleep(1)
    proc.send_signal(signum)

    # Make sure the signal is handled by our handler in the code
    stdout, stderr = proc.communicate()
    expected_output = (
        "\n".join([f"handler {i} received {signum}" for i in range(handlercount)])
        + "\n"
    )

    assert stdout == expected_output

    # The code should exit cleanly
    retcode = proc.wait()
    assert retcode == 0
