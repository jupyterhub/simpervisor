import sys
import signal
import os
import pytest
from simpervisor import SupervisedProcess
import subprocess
import time
import errno


@pytest.mark.parametrize('childcount', [1, 5])
async def test_sigtermreap(childcount):
    """
    Test reaping subprocess after SIGTERM.

    - Start a supervisor process that supervises a child.
    - Send supervisor a SIGTERM
    - Make sure child receives it & exits first before supervisor exiting
    """
    signalsupervisor_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'child_scripts',
        'signalsupervisor.py'
    )

    proc = subprocess.Popen([sys.executable, signalsupervisor_file, str(childcount)], stdout=subprocess.PIPE)
    
    # Give the signal handlers a bit of time to set up
    time.sleep(0.5)

    # Read the child's PID from signalsupervisor
    child_pids = [int(l) for l in proc.stdout.readline().decode().split(' ')]

    proc.send_signal(signal.SIGTERM)
    proc.wait()

    stdout, stderr = proc.communicate()

    # Make sure the children are dead
    for child_pid in child_pids:
        with pytest.raises(OSError) as e:
            os.kill(child_pid, 0)
        assert e.value.errno == errno.ESRCH

    # Test order of exit of child & parent
    assert stdout.decode() == 'handler 0 received 15\n' * len(child_pids) + 'supervisor exiting cleanly\n'
    # Test that our supervisor also exited cleanly
    assert proc.returncode == 0