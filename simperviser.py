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
        self.running = False

    async def start(self):
        """
        Start the process
        """
        self.proc = await asyncio.create_subprocess_exec(
            *self._proc_args, **self._proc_kwargs
        )
        self.running = True
        asyncio.ensure_future(self._restart_process_if_needed())

    async def _restart_process_if_needed(self):
        retcode = await self.proc.wait()
        self.running = False
        if self.always_restart or retcode != 0:
            await self.start()

    @property
    def pid(self):
        return self.proc.pid


async def main():
    sp = SupervisedProcess('/bin/bash', '-c', 'echo $HI; exit 1', always_restart=False, env={'HI': 'BOO'})
    await sp.start()

if __name__ == '__main__':
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()