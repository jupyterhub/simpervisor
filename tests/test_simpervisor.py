import asyncio
import inspect
import signal
import sys

import psutil
import pytest

from simpervisor import KilledProcessError, SupervisedProcess

SLEEP_TIME = 0.1

# On Windows, for test_start_success testpoint, the process exit is taking more
# than 0.5 seconds. Hence, to be on safe side setting the wait timeout value to
# be 5 seconds.
SLEEP_WAIT_TIME = 5


def sleep(retcode=0, time=SLEEP_TIME):
    """
    Sleep for {time} seconds & return code {retcode}
    """
    return [
        sys.executable,
        "-c",
        f"import sys, time; time.sleep({time}); sys.exit({retcode})",
    ]


async def test_start_success():
    """
    Start a process & check its running status
    """
    proc = SupervisedProcess(
        inspect.currentframe().f_code.co_name, *sleep(0), always_restart=False
    )
    await proc.start()
    assert proc.running
    await asyncio.sleep(SLEEP_WAIT_TIME)
    assert not proc.running


async def test_start_always_restarting():
    """
    Start a process & check it restarts even when it succeeds
    """
    proc = SupervisedProcess(
        inspect.currentframe().f_code.co_name, *sleep(0), always_restart=True
    )
    await proc.start()
    assert proc.running
    first_pid = proc.pid
    await asyncio.sleep(SLEEP_WAIT_TIME)
    # Process should have restarted by now
    assert proc.running
    # Make sure it is a new process
    assert proc.pid != first_pid

    await proc.terminate()
    assert not proc.running


async def test_start_fail_restarting():
    """
    Start a process that fails & make sure it restarts
    """
    proc = SupervisedProcess(
        inspect.currentframe().f_code.co_name, *sleep(1), always_restart=True
    )
    await proc.start()
    assert proc.running
    first_pid = proc.pid
    await asyncio.sleep(SLEEP_WAIT_TIME)
    # Process should have restarted by now
    assert proc.running
    # Make sure it is a new process
    assert proc.pid != first_pid

    await proc.terminate()
    assert not proc.running


async def test_start_multiple_start():
    """
    Starting the same process multiple times should be a noop
    """
    proc = SupervisedProcess(
        inspect.currentframe().f_code.co_name, *sleep(0), always_restart=True
    )
    await proc.start()
    assert proc.running
    first_pid = proc.pid
    await proc.start()
    assert proc.running
    assert proc.pid == first_pid

    await proc.terminate()
    assert not proc.running


@pytest.mark.parametrize("method", ["start", "kill", "terminate"])
async def test_method_after_kill(method):
    """
    Running 'method' on process after it has been killed should throw
    """
    proc = SupervisedProcess(
        inspect.currentframe().f_code.co_name, *sleep(0), always_restart=True
    )
    await proc.start()
    assert proc.running
    await proc.kill()
    assert not proc.running

    with pytest.raises(KilledProcessError):
        await getattr(proc, method)()


async def test_kill():
    """
    Test killing processes
    """
    proc = SupervisedProcess(
        inspect.currentframe().f_code.co_name, *sleep(0), always_restart=True
    )

    await proc.start()
    await proc.kill()
    exitcode = 1 if sys.platform == "win32" else -signal.SIGKILL
    assert proc.returncode == exitcode
    assert not proc.running
    assert not psutil.pid_exists(proc.pid)


async def test_terminate():
    """
    Test terminating processes
    """
    proc = SupervisedProcess(
        inspect.currentframe().f_code.co_name, *sleep(0), always_restart=True
    )

    await proc.start()
    await proc.terminate()
    exitcode = 1 if sys.platform == "win32" else -signal.SIGTERM
    assert proc.returncode == exitcode
    assert not proc.running
    assert not psutil.pid_exists(proc.pid)
