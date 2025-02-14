import asyncio
import subprocess
from typing import TYPE_CHECKING

from omnigram.config import config
from omnigram.telegram import TelegramHandler

if TYPE_CHECKING:
    from asyncio import Task
    from asyncio.streams import StreamReader


class MinecraftServer:
    _server = None
    _task: "Task | None" = None
    _people_online: int = 0
    _telegram_handler: "TelegramHandler"

    async def _launch(self) -> None:
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

            async def send_password() -> None:
                if self._server is not None and self._server.stdin is not None:
                    self._server.stdin.write(f"{config.admin.sudo}\n".encode())
                    await self._server.stdin.drain()

            await send_password()

            if self._server is not None and self._server.stdout is not None and self._server.stderr is not None:
                asyncio.create_task(self._read_stream(self._server.stdout))
                asyncio.create_task(self._read_stream(self._server.stderr))

    async def send_message_to_telegram(self, text: str) -> None:
        text = text.replace("<", "[")
        text = text.replace(">", "]")
        output = text.split()
        output = output[5:]
        text = " ".join(output)

        print(text)
        await self._telegram_handler.bot.send_message(
            chat_id=config.telegram.group_mc,
            message_thread_id=config.telegram.topic_mc_minecraft_chat,
            text=text,
        )

    async def send_message_to_minecraft(self, user: str, text: str) -> None:
        if self._server is not None and self._server.stdin is not None:
            self._server.stdin.write(f'tellraw @a "<{user}>: {text}"\n'.encode())
            await self._server.stdin.drain()
            await asyncio.sleep(1)

    async def _read_stream(self, stream: "StreamReader") -> None:
        while True:
            line = await stream.readline()
            if not line:
                break
            output = line.decode().strip()
            if "of a max of 20 players online" in output:
                self._people_online = int(output.split()[5]) if output.split()[5] is not None else 0
            elif "Server empty for 60 seconds, pausing" in output:
                await self.terminate()
            elif "[Not Secure] <" in output:
                await self.send_message_to_telegram(text=output)
            else:
                print(output)

    async def list(self) -> int | None:
        if self._server is not None and self._server.stdin is not None:
            self._server.stdin.write("list\n".encode())
            await self._server.stdin.drain()
            await asyncio.sleep(1)
            return self._people_online
        return None

    def launch(self) -> None:
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._launch())

    async def terminate(self) -> None:
        if self._server is not None and self._server.stdin is not None:
            self._server.stdin.write("stop\n".encode())
            await self._server.stdin.drain()
            await asyncio.sleep(5)
            await self._server.wait()
            self._server = None

        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    def status(self) -> str:
        if self._server is not None:
            return "Active ✅"
        return "Terminated ❌"

    def __del__(self) -> None:
        asyncio.run(self.terminate())
