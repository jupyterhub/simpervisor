import asyncio
import errno
import inspect
import os
import signal
import sys

import pytest

import simpervisor

SLEEP_TIME = 0.1
SLEEP_WAIT_TIME = 0.5

def sleep(retcode=0, time=SLEEP_TIME):
    """
    Sleep for {time} seconds & return code {retcode}
    """
    return [
        sys.executable,
        '-c', 'import sys, time; time.sleep({}); sys.exit({})'.format(time, retcode)
    ]

async def test_start_success():
    """
    Start a process & check its running status
    """
    proc = simpervisor.SupervisedProcess(
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
    proc = simpervisor.SupervisedProcess(
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
    proc = simpervisor.SupervisedProcess(
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
    proc = simpervisor.SupervisedProcess(
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


@pytest.mark.parametrize('method', ['start', 'kill', 'terminate'])
async def test_method_after_kill(method):
    """
    Running 'method' on process after it has been killed should throw
    """
    proc = simpervisor.SupervisedProcess(
        inspect.currentframe().f_code.co_name, *sleep(0), always_restart=True
    )
    await proc.start()
    assert proc.running
    await proc.kill()
    assert not proc.running

    with pytest.raises(simpervisor.KilledProcessError):
        await getattr(proc, method)()


async def test_kill():
    """
    Test killing processes
    """
    proc = simpervisor.SupervisedProcess(
        inspect.currentframe().f_code.co_name, *sleep(0), always_restart=True
    )

    await proc.start()
    await proc.kill()
    assert proc.returncode == -signal.SIGKILL
    assert not proc.running
    with pytest.raises(OSError) as e:
        os.kill(proc.pid, 0)
    assert e.value.errno == errno.ESRCH


async def test_terminate():
    """
    Test terminating processes
    """
    proc = simpervisor.SupervisedProcess(
        inspect.currentframe().f_code.co_name, *sleep(0), always_restart=True
    )

    await proc.start()
    await proc.terminate()
    assert proc.returncode == -signal.SIGTERM
    assert not proc.running
    with pytest.raises(OSError) as e:
        os.kill(proc.pid, 0)
    assert e.value.errno == errno.ESRCH