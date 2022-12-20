import datetime

from discord.ext import commands

from bot import ClodBot
from cogs.discord_utils.embeds import ClodEmbed


class Aakash(commands.Cog):
    def __init__(self, bot: ClodBot):
        self.bot = bot
        self.d_day = datetime.datetime(2023, 1, 24, 5, 30, 0)

    @commands.hybrid_command()
    async def countdown(self, ctx: commands.Context):
        """Countdown to D-Day."""
        delta = abs(self.d_day - datetime.datetime.utcnow())
        d = delta.days if delta.days > 0 else 0
        # timedelta only stores seconds so calculate mins and hours by dividing remainder
        h, rem = divmod(delta.seconds, 3600)
        m, s = divmod(rem, 60)
        # text representation
        stringify = (
            f"{int(d)} {'days' if d != 1 else 'day'}, "
            f"{int(h)} {'hours' if h != 1 else 'hour'}, "
            f"{int(m)} {'minutes' if m != 1 else 'minute'}, "
            f"{int(s)} {'seconds' if s != 1 else 'second'} "
        )
        desc = f"<t:{int(self.d_day.timestamp())}> is {stringify} from today"

        embed = ClodEmbed(description=desc)
        embed.set_image(
            url="https://cdn.discordapp.com/attachments/842796682114498570/1054616038546874428/cozyNukes.jpg"
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Aakash(bot))
