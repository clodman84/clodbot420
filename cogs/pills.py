from discord.ext import commands
from cogs.discord_utils.embeds import ClodEmbed
import discord
import clodbot.database as database
import time
import re
from clodbot.utils import SimpleTimer
from bot import ClodBot


class PillsCog(commands.Cog):
    def __init__(self, bot: ClodBot):
        self.bot = bot
        self.basedRegex = re.compile(
            r"based and (([\w\"'-]+\s+)+)pilled", re.IGNORECASE
        )

    @commands.Cog.listener("on_message")
    async def basedDetector(self, message: discord.Message):
        if message.reference is None:
            return
        match = self.basedRegex.search(message.content)
        if not match:
            return
        og: discord.Message = message.reference.resolved
        if og.author.id == message.author.id or og.content == "":
            return
        pillMessage = match.group(1).strip()
        pill = database.Pill(
            int(time.time()),
            pillMessage,
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
            description=f"{og.author.mention} you are now based and {pillMessage} pilled!"
        ).set_footer(text=timer)
        await message.channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(PillsCog(bot))
