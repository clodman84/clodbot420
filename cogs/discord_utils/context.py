import io
import discord
from discord.ext import commands
from .embeds import ClodEmbed
from typing import Optional
from textwrap import fill
import logging


log = logging.getLogger("clodbot.disutils.context")


class Context(commands.Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def safe_send(
        self,
        content: Optional[str] = None,
        embed: Optional[ClodEmbed] = None,
        fileType="txt",
    ) -> discord.Message:
        """Tries sending a file if something went wrong with sending the message, usually because it's too long"""
        try:
            await self.send(content, embed=embed)
        except Exception as e:
            data = (
                f"Content:\n\n{fill(str(content), width=75)}\n{'_'*75}\n\n{str(embed)}"
            )
            fp = io.BytesIO(data.encode())
            await self.send(f"{str(e)}. Trying to send a file instead...")
            return await self.send(
                file=discord.File(fp, filename=f"message_too_long.{fileType}")
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
