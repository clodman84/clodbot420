from discord.ext import commands
from cogs.discord_utils.Context import Context
from cogs.discord_utils.Embeds import ClodEmbed
from clodbot import python
from bot import ClodBot
import logging

log = logging.getLogger("clodbot.cogs.admin")


class AdminCog(commands.Cog):
    def __init__(self, bot: ClodBot):
        self.bot = bot
        self.retain = False

    async def cog_check(self, ctx: Context):
        return await self.bot.is_owner(ctx.author)

    @commands.command(hidden=True, name="eval")
    async def _eval(self, ctx: Context, *, code: str):
        env = {
            "bot": self.bot,
            "ctx": ctx,
            "channel": ctx.channel,
            "author": ctx.author,
            "guild": ctx.guild,
            "message": ctx.message,
        }
        env.update(globals())
        status, output, time = await python.execute(code, env)
        await ctx.tick(status)
        embed = ClodEmbed(description=output, status=status).set_footer(text=time)
        await ctx.safe_send(embed=embed)


async def setup(bot):
    await bot.add_cog(AdminCog(bot))
