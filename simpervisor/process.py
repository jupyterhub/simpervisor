"""
Simple asynchronous process supervisor
"""
import asyncio
import logging
import signal
import subprocess
import sys
import time

from .atexitasync import add_handler, remove_handler


class KilledProcessError(Exception):
    """
    Raised when a process that has been explicitly killed is started again.

    Each SupervisedProcess can be killed only once.
    """


class Process:
    """
    Abstract class to start, wait and send signals to running processes in a OS agnostic way
    """

    # Protected data members only accessible by derived classes.
    _proc_cmd = None
    _proc_kwargs = None
    _proc = None

    def __init__(self, *cmd, **kwargs):
        self._proc_cmd = cmd
        self._proc_kwargs = kwargs

    async def start(self):
        """
        Start the process
        """
        raise NotImplementedError

    async def wait(self):
        """
        Wait for the process to terminate and return the process exit code.
        """
        raise NotImplementedError

    def get_kill_signal(self):
        """
        Returns the preferred OS signal to kill the process.
        """
        raise NotImplementedError

    def send_signal(self, signum):
        """
        Send the OS signal to the process.
        """
        if self._proc:
            self._proc.send_signal(signum)

    @property
    def pid(self):
        if self._proc:
            return self._proc.pid

    @property
    def returncode(self):
        if self._proc:
            return self._proc.returncode


class POSIXProcess(Process):
    """
    A process that uses asyncio-subprocess API to start and wait.
    """

    async def start(self):
        """
        Start the process using asyncio.create_subprocess_exec API
        """
        self._proc = await asyncio.create_subprocess_exec(
            *self._proc_cmd, **self._proc_kwargs
        )

    async def wait(self):
        """
        Wait for the process to stop and return the process exit code.
        """
        return await self._proc.wait()

    def get_kill_signal(self):
        """
        Returns the OS signal used for kill the child process.
        """
        return signal.SIGKILL


class WindowsProcess(Process):
    """
    A process that uses subprocess API to start and wait (uses busy polling).
    """

    async def start(self):
        """
        Starts the process using subprocess.Popen API
        """
        self._proc = subprocess.Popen(list(self._proc_cmd), **self._proc_kwargs)

    async def wait(self):
        """
        Wait for the process to stop and return the process exit code.

        subprocess.Popen.wait() is a blocking call which can cause the asyncio
        event loop to remain blocked until the child process is terminated.

        To circumvent this behavior, we use busy polling with asyncio.sleep to check
        whether the child process is alive or not and keeping the asyncio event
        loop running.

        See https://github.com/jupyter/jupyter_client/blob/main/jupyter_client/provisioning/local_provisioner.py#L54_L55 for similar use.
        """
        while self._proc.poll() is None:
            await asyncio.sleep(0.5)
        return self._proc.wait()

    def get_kill_signal(self):
        """
        Returns the OS signal used for kill the child process.

        Windows doesn't support SIGKILL. subprocess.Popen.kill() is an alias of
        subprocess.Popen.terminate(), so we can use SIGTERM instead of SIGKILL
        on windows platform.
        """
        return signal.SIGTERM


class SupervisedProcess:
    def __init__(
        self,
        name,
        *args,
        always_restart=False,
        ready_func=None,
        ready_timeout=5,
        log=None,
        **kwargs,
    ):
        self.always_restart = always_restart
        self.name = name
        self._proc_args = args
        self._proc_kwargs = kwargs
        self.ready_func = ready_func
        self.ready_timeout = ready_timeout
        self.proc = None
        if log is None:
            self.log = logging.getLogger("simpervisor")
        else:
            self.log = log

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

    def _debug_log(self, action, message, extras=None, *args):
        """
        Log debug message with some added meta information.

        Makes structured logging easier
        """
        base_extras = {
            "action": action,
            "proccess-name": self.name,
            "process-args": self._proc_args,
            "process-kwargs": self._proc_kwargs,
        }
        if extras:
            base_extras.update(extras)
        # Call .format() explicitly here, since we wanna use new style {} formatting
        self.log.debug(message.format(*args), extra=base_extras)

    def _handle_signal(self, signal):
        # Child processes should handle SIGTERM / SIGINT & close,
        # which should trigger self._restart_process_if_needed
        # We don't explicitly reap child processes
        self.proc.send_signal(signal)
        # Don't restart process after it is reaped
        self._killed = True
        self._debug_log("signal", "Propagated signal {} to {}", {}, signal, self.name)

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
        async with self._proc_lock:
            if self.running:
                # Don't wanna start it again, if we're already running
                return
            if self._killed:
                raise KilledProcessError(
                    f"Process {self.name} has already been explicitly killed"
                )
            self._debug_log("try-start", "Trying to start {}", {}, self.name)

            # Child process is created based on platform
            if sys.platform == "win32":
                self.proc = WindowsProcess(*self._proc_args, **self._proc_kwargs)
            else:
                self.proc = POSIXProcess(*self._proc_args, **self._proc_kwargs)

            # Start the child process
            await self.proc.start()
            self._debug_log("started", "Started {}", {}, self.name)

            self._killed = False
            self.running = True

            # Spin off a coroutine to watch, reap & restart process if needed
            # We don't wanna do this multiple times, so this is also inside the lock
            self._restart_process_future = asyncio.ensure_future(
                self._restart_process_if_needed()
            )

            # This handler is removed when process stops
            add_handler(self._handle_signal)

    async def _restart_process_if_needed(self):
        """
        Watch for process to exit & restart it if needed.

        This is a long running task that keeps running until the process
        exits. If we restart the process, `start()` sets this up again.
        """
        retcode = await self.proc.wait()
        # FIXME: Do we need to aquire a lock somewhere in this method?
        remove_handler(self._handle_signal)
        self._debug_log(
            "exited", "{} exited with code {}", {"code": retcode}, self.name, retcode
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
        async with self._proc_lock:
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
            remove_handler(self._handle_signal)

    async def terminate(self):
        """
        Send SIGTERM to process & reap it.

        Might take a while if the process catches & ignores SIGTERM.
        """
        if self._killed:
            raise KilledProcessError(
                f"Process {self.name} has already been explicitly killed"
            )
        return await self._signal_and_wait(signal.SIGTERM)

    async def kill(self):
        """
        Send SIGKILL to process & reap it
        """
        if self._killed:
            raise KilledProcessError(
                f"Process {self.name} has already been explicitly killed"
            )
        signum = self.proc.get_kill_signal()
        return await self._signal_and_wait(signum)

    async def ready(self):
        """
        Wait for process to become 'ready'
        """
        # FIXME: Should this be internal and part of 'start'?
        # FIXME: Do we need some locks here?
        # Repeatedly run ready_func with a timeout until it returns true
        # FIXME, parameterize these numbers
        start_time = time.time()
        wait_time = 0.01

        while True:
            if time.time() - start_time > self.ready_timeout:
                # We have exceeded our timeout, so return
                return False

            # Make sure we haven't been killed yet since the last loop
            # We explicitly do *not* check if we are running, since we might be
            # restarting in a loop while the readyness check is happening
            if self._killed or not self.proc:
                return False

            # FIXME: What's the timeout for each readyness check handler?
            # FIXME: We should probably check again if our process is still running
            # FIXME: Should we be locking something here?
            try:
                # Timeout of 5 secs is needed as DNS resolution of localhost
                # on Windows takes significant time.
                is_ready = await asyncio.wait_for(self.ready_func(self), 5)
            except asyncio.TimeoutError:
                is_ready = False
            cur_time = time.time() - start_time
            self._debug_log(
                "ready-wait",
                "Readyness: {} after {} seconds, next check in {}s",
                {"wait_time": wait_time, "ready": is_ready, "elapsed_time": cur_time},
                is_ready,
                cur_time,
                wait_time,
            )
            if is_ready:
                return True
            await asyncio.sleep(wait_time)

            # FIXME: Be more sophisticated here with backoff & jitter
            wait_time = 2 * wait_time
            if (time.time() + wait_time) > (start_time + self.ready_timeout):
                # If we wait for wait_time, we'll be over the ready_timeout
                # So let's clamp wait_time so that wait_time is just enough
                # to get us to ready_timeout seconds since start_time
                # FIXME: This means wait_time can be negative...
                wait_time = (start_time + self.ready_timeout) - time.time() - 0.01

        return False

    # Pass through methods specific methods from proc
    # We don't pass through everything, just a subset we know is safe
    # and would work.
    @property
    def pid(self):
        return self.proc.pid

    @property
    def returncode(self):
        return self.proc.returncode
