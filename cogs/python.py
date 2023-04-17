from io import BytesIO

from discord import File
from discord.ext import commands

from bot import ClodBot
from clodbot import python
from clodbot.internal_eval import cleanup_code
from cogs.discord_utils.context import Context
from cogs.discord_utils.embeds import ClodEmbed


class Python(commands.Cog):
    def __init__(self, bot: ClodBot):
        self.bot = bot

    @commands.command()
    async def xeval(self, ctx: Context, *, code: str):  # x for experimental
        output = await python.post_code(cleanup_code(code))
        await ctx.tick(output.status)
        embed = ClodEmbed(
            status=output.status, description=f"```py\n{output.stdout}```"
        )
        embed.add_field(name="Status", value=output.get_status_message())
        files = [
            File(BytesIO(file.content), filename=file.get_discord_name())
            for file in output.files
        ]
        await ctx.send(embed=embed, files=files)


async def setup(bot):
    await bot.add_cog(Python(bot))
