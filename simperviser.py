"""
Simple asynchronous process supervisor
"""
import asyncio


class SupervisedProcess:
    def __init__(self, *args, always_restart=False, **kwargs):
        self.always_restart = always_restart
        self._proc_args = args
        self._proc_kwargs = kwargs
        self.proc: asyncio.Process = None

        # asyncio.Process has no 'poll', so we keep that state internally
        self.running = False

        # Don't restart process if we explicitly kill it
        self._killed = False

        # Only one coroutine should be starting or killing a process at a time
        self._start_stop_lock = asyncio.Lock()

    async def start(self):
        """
        Start the process
        """
        with (await self._start_stop_lock):
            if self.running:
                # Don't wanna start it again, if we're already running
                return
            self.proc = await asyncio.create_subprocess_exec(
                *self._proc_args, **self._proc_kwargs
            )
        self._killed = False
        self.running = True

        # Spin off a coroutine to watch, reap & restart process if needed
        asyncio.ensure_future(self._restart_process_if_needed())

    async def _restart_process_if_needed(self):
        retcode = await self.proc.wait()
        self.running = False
        if (not self._killed) and (self.always_restart or retcode != 0):
            await self.start()

    async def kill(self):
        self._killed = True
        with (await self._start_stop_lock):
            self.proc.kill()
        return await self.proc.wait()

    @property
    def pid(self):
        return self.proc.pid