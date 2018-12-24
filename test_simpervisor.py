import inspect
import asyncio
import pytest
import sys
import logging

import simpervisor

SLEEP_TIME = 0.5
SLEEP_WAIT_TIME = 1

def sleep(retcode=0, time=SLEEP_TIME):
    """
    Sleep for {time} seconds & return code {retcode}
    """
    return [
        sys.executable,
        '-c', f'import sys, time; time.sleep({time}); sys.exit({retcode})'
    ]

@pytest.mark.asyncio
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

@pytest.mark.asyncio
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

    await proc.kill()
    assert not proc.running

@pytest.mark.asyncio
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

    await proc.kill()
    assert not proc.running


@pytest.mark.asyncio
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

    await proc.kill()
    assert not proc.running