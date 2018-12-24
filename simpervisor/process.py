"""
Simple asynchronous process supervisor
"""
import signal
import asyncio
import logging
from simpervisor import atexitasync


class SupervisedProcess:
    def __init__(self, name, *args, always_restart=False, **kwargs):
        self.always_restart = always_restart
        self.name = name
        self._proc_args = args
        self._proc_kwargs = kwargs
        self.proc: asyncio.Process = None

        # asyncio.Process has no 'poll', so we keep that state internally
        self.running = False

        # Don't restart process if we explicitly kill it
        self._killed = False

        # Don't restart process if we are terminating after SIGTERM / SIGINT
        self._terminating = False

        # Only one coroutine should be starting or killing a process at a time
        self._start_stop_lock = asyncio.Lock()

        self.log = logging.getLogger('simpervisor')

    def _debug_log(self, action, message, extras=None):
        base_extras = {
            'action': action,
            'proccess-name': self.name,
            'process-args': self._proc_args,
            'process-kwargs': self._proc_kwargs
        }
        if extras:
            base_extras.update(extras)
        self.log.debug(message, extra=base_extras)

    def _handle_signal(self, signal):
        # Child processes should handle SIGTERM / SIGINT & close,
        # which should trigger self._restart_process_if_needed
        # We don't explicitly reap child processe
        self.proc.send_signal(signal)
        # Don't restart process after it is reaped
        self._terminating = True
        self._debug_log('signal', f'Propagated signal {signal} to {self.name}')

    def wait(self):
        return self.proc.wait()

    async def start(self):
        """
        Start the process
        """
        with (await self._start_stop_lock):
            if self.running:
                # Don't wanna start it again, if we're already running
                return
            self._debug_log('try-start', f'Trying to start {self.name}',)
            self.proc = await asyncio.create_subprocess_exec(
                *self._proc_args, **self._proc_kwargs
            )
            self._debug_log('started', f'Started {self.name}',)

        self._killed = False
        self.running = True

        # Spin off a coroutine to watch, reap & restart process if needed
        asyncio.ensure_future(self._restart_process_if_needed())
        atexitasync.add_handler(self._handle_signal)

    async def _restart_process_if_needed(self):
        retcode = await self.proc.wait()
        atexitasync.remove_handler(self._handle_signal)
        self._debug_log(
            'exited', f'{self.name} exited with code {retcode}',
            {'code': retcode}
        )
        self.running = False
        if (not self._terminating) and (not self._killed) and (self.always_restart or retcode != 0):
            await self.start()

    async def kill(self):
        self._killed = True
        with (await self._start_stop_lock):
            self._debug_log('killing', f'Killing {self.name}')
            self.proc.kill()
            retcode = await self.proc.wait()
            self._debug_log(
                'killed',
                f'Killed {self.name}, with retcode {retcode}', extras={'code': retcode}
            )
            self.running = False
        return retcode

    @property
    def pid(self):
        return self.proc.pid