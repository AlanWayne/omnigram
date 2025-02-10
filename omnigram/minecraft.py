import asyncio
import subprocess
from omnigram.config import config


class MinecraftServer:
    _instance = None
    _server = None
    _task = None
    _stdout_queue: asyncio.Queue = asyncio.Queue()
    _stderr_queue: asyncio.Queue = asyncio.Queue()
    people_online = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MinecraftServer, cls).__new__(cls)
        return cls._instance

    async def _launch(self):
        if not self._server:
            self._server = await asyncio.create_subprocess_exec(
                "sudo",
                "-S",
                "make",
                config.minecraft.target,
                cwd=config.minecraft.path,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            async def send_password():
                self._server.stdin.write(f"{config.admin.sudo}\n".encode())
                await self._server.stdin.drain()

            await send_password()

            asyncio.create_task(self._read_stream(self._server.stdout))
            asyncio.create_task(self._read_stream(self._server.stderr))

    async def _read_stream(self, stream):
        while True:
            line = await stream.readline()
            if not line:
                break
            output = line.decode().strip()
            if "of a max of 20 players online" in output:
                self.people_online = output.split()[5]
            else:
                print(output)

    async def list(self):
        self._server.stdin.write("list\n".encode())
        await self._server.stdin.drain()
        await asyncio.sleep(1)
        return self.people_online

    def launch(self):
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._launch())

    async def terminate(self):
        if self._server:
            self._server.terminate()
            await self._server.wait()
            self._server = None

        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    def status(self):
        if self._server:
            return "Active ✅"
        return "Terminated ❌"

    def __del__(self):
        asyncio.run(self.terminate())
