import io
import discord
from discord.ext import commands
from .Embeds import ClodEmbed
from typing import Optional
import logging
from textwrap import wrap

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
            embedDict = embed.to_dict()
            description = "\n".join(wrap(embedDict["description"], 75))
            data = f"{content}\n{description}\nFooter: {embedDict['footer']['text']}"
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
