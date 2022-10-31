import sys
import time
import pytest
import os
from simpervisor import SupervisedProcess
import aiohttp
import logging

async def test_ready():
    """
    Test web app's readyness
    """
    httpserver_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'child_scripts',
        'simplehttpserver.py'
    )

    port = '9005'
    # We tell our server to wait this many seconds before it starts serving
    ready_time = 3.0

    async def _ready_func(p):
        url = 'http://localhost:{}'.format(port)
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as resp:
                    logging.debug('Got code {} back from {}', resp.status, url)
                    return resp.status == 200
            except aiohttp.ClientConnectionError:
                logging.debug('Connection to {} refused', url)
                return False

    proc = SupervisedProcess(
        'socketserver',
        sys.executable, httpserver_file, str(ready_time),
        ready_func=_ready_func,
        env={'PORT': port}
    )

    try:
        await proc.start()
        start_time = time.time()
        assert (await proc.ready())
        assert time.time() - start_time > ready_time
    finally:
        # Clean up our process after ourselves
        await proc.kill()