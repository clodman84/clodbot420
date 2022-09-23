import io
import discord
from discord.ext import commands
import logging

log = logging.getLogger("clodbot.context")


class Context(commands.Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def safe_send(self, content: str, **kwargs) -> discord.Message:
        """Tries sending a file if something went wrong with sending the message, usually because it's too long"""
        try:
            await self.send(content, **kwargs)
        except Exception as e:
            fp = io.BytesIO(content.encode())
            kwargs.pop("file", None)
            await self.send(f"{str(e)}. Trying to send a file instead...")
            return await self.send(
                file=discord.File(fp, filename="message_too_long.txt"), **kwargs
            )

    async def tick(self, opt):
        lookup = {
            True: "\u2705",
            False: "\u274C",
        }
        try:
            await self.message.add_reaction(lookup[opt])
        except Exception as e:
            log.error(f"While adding reaction {e.__class__.__name__}: {e}")
