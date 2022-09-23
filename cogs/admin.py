from discord.ext import commands
from cogs.discord_utils.Context import Context
from cogs.discord_utils.Embeds import makeEmbeds
from clodbot import python
from bot import ClodBot
from typing import Optional, Any

import logging

log = logging.getLogger("clodbot.admin")


class AdminCog(commands.Cog):
    # borrowed from RoboDanny
    def __init__(self, bot: ClodBot):
        self.bot = bot
        self._last_result: Optional[Any] = None

    async def cog_check(self, ctx: Context):
        return await self.bot.is_owner(ctx.author)

    @commands.command(hidden=True, name="eval")
    async def _eval(self, ctx: Context, *, code: str):
        """Evaluates a code"""
        env = {
            "bot": self.bot,
            "ctx": ctx,
            "channel": ctx.channel,
            "author": ctx.author,
            "guild": ctx.guild,
            "message": ctx.message,
            "_": self._last_result,
        }
        env.update(globals())
        status, output, time = await python.execute(code, env)
        await ctx.tick(status)
        for embed in makeEmbeds(output):
            embed.set_footer(text=f"{time}")
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(AdminCog(bot))
