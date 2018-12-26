"""
Simple asynchronous process supervisor
"""
import signal
import asyncio
import logging
from simpervisor import atexitasync

class KilledProcessError(Exception):
    """
    Raised when a process that has been explicitly killed is started again.

    Each SupervisedProcess can be killed only once.
    """
    pass

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

        # The 'process' is a shared resource, and protected by this lock
        # This lock must be aquired whenever the process' state can be
        # changed. That includes starting it, communicating with it & waiting
        # for it to stop. While we need to be careful around sending signals to
        # the process, that doesn't require the lock to be held - since sending
        # signals is synchronous.
        self._proc_lock = asyncio.Lock()

        self.log = logging.getLogger('simpervisor')

    def _debug_log(self, action, message, extras=None):
        """
        Log debug message with some added meta information.

        Makes structured logging easier
        """
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
        self._killed = True
        self._debug_log('signal', f'Propagated signal {signal} to {self.name}')

    async def start(self):
        """
        Start the process if it isn't already running.

        If the process is already running, this is a noop. If the process
        has already been killed, this raises an exception
        """
        # Aquire process lock before we try to start the process.
        # We could concurrently be in any other part of the code where
        # process is started or killed. So we check for that as soon
        # as we aquire the lock and behave accordingly.
        with (await self._proc_lock):
            if self.running:
                # Don't wanna start it again, if we're already running
                return
            if self._killed:
                raise  KilledProcessError(f"Process {self.name} has already been explicitly killed")
            self._debug_log('try-start', f'Trying to start {self.name}',)
            self.proc = await asyncio.create_subprocess_exec(
                *self._proc_args, **self._proc_kwargs
            )
            self._debug_log('started', f'Started {self.name}',)

            self._killed = False
            self.running = True

            # Spin off a coroutine to watch, reap & restart process if needed
            # We don't wanna do this multiple times, so this is also inside the lock
            self._restart_process_future = asyncio.ensure_future(self._restart_process_if_needed())

            # This handler is removed when process stops
            atexitasync.add_handler(self._handle_signal)

    async def _restart_process_if_needed(self):
        """
        Watch for process to exit & restart it if needed.

        This is a long running task that keeps running until the process
        exits. If we restart the process, `start()` sets this up again.
        """
        retcode = await self.proc.wait()
        atexitasync.remove_handler(self._handle_signal)
        self._debug_log(
            'exited', f'{self.name} exited with code {retcode}',
            {'code': retcode}
        )
        self.running = False
        if (not self._killed) and (self.always_restart or retcode != 0):
            await self.start()


    async def _signal_and_wait(self, signum):
        """
        Send a SIGTERM or SIGKILL to the child process & reap it.

        - Send the signal to the process
        - Make sure we don't restart it when it stops
        - Wait for it to stop
        - Remove signal handler for it after we are done.
        """

        # Aquire lock to modify process sate
        with (await self._proc_lock):
            # Don't yield control between sending signal & calling wait
            # This way, we don't end up in a call to _restart_process_if_needed
            # and possibly restarting. We also set _killed, just to be sure.
            self.proc.send_signal(signum)
            self._killed = True

            # We cancel the restart watcher & wait for the process to finish,
            # since we return only after the process has been reaped
            self._restart_process_future.cancel()
            await self.proc.wait()
            self.running = False
            # Remove signal handler *after* the process is done
            atexitasync.remove_handler(self._handle_signal)

    async def terminate(self):
        """
        Send SIGTERM to process & reap it.

        Might take a while if the process catches & ignores SIGTERM.
        """
        if self._killed:
            raise  KilledProcessError(f"Process {self.name} has already been explicitly killed")
        return await self._signal_and_wait(signal.SIGTERM)

    async def kill(self):
        """
        Send SIGKILL to process & reap it
        """
        if self._killed:
            raise  KilledProcessError(f"Process {self.name} has already been explicitly killed")
        return await self._signal_and_wait(signal.SIGKILL)

    # Pass through methods specific methods from proc
    # We don't pass through everything, just a subset we know is safe
    # and would work.
    @property
    def pid(self):
        return self.proc.pid

    @property
    def returncode(self):
        return self.proc.returncode
