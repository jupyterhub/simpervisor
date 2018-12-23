import asyncio
import pytest

import simperviser

@pytest.mark.asyncio
async def test_start_success():
    """
    Start a process & check its running status
    """
    proc = simperviser.SupervisedProcess(
        '/bin/bash', '-c', 'sleep 0.5', always_restart=False
    )
    await proc.start()
    assert proc.running
    await asyncio.sleep(0.51)
    assert not proc.running


@pytest.mark.asyncio
async def test_start_restarting():
    """
    Start a process that fails & make sure it restarts
    """
    proc = simperviser.SupervisedProcess(
        '/bin/bash', '-c', 'sleep 0.5; exit 1', always_restart=False
    )
    await proc.start()
    assert proc.running
    first_pid = proc.pid
    await asyncio.sleep(0.51)
    # Process should have restarted by now
    assert proc.running
    # Make sure it is a new process
    assert proc.pid != first_pid