from discord.ext import commands
from cogs.discord_utils.embeds import ClodEmbed
import discord
import clodbot.database as database
import time
from clodbot.utils import SimpleTimer
from bot import ClodBot


class PillsCog(commands.Cog):
    def __init__(self, bot: ClodBot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def basedDetector(self, message: discord.Message):
        if message.reference is None:
            return
        content = message.content.lower().split()
        if not (content[:2] == ["based", "and"] and content[-1] == "pilled"):
            return
        og: discord.Message = message.reference.resolved
        if og.author.id == message.author.id or og.content == "":
            return
        pill = database.Pill(
            int(time.time()),
            " ".join(content[3:-1]),
            og.content,
            message.author.id,
            og.author.id,
            message.channel.id,
            message.id,
            message.guild.id,
        )
        with SimpleTimer() as timer:
            await database.insertPill(pill, self.bot.db)

        embed = ClodEmbed(
            description=f"{og.author.mention} your based counter increased by one!"
        ).set_footer(text=timer)
        await message.channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(PillsCog(bot))
