from discord.ext import commands
from cogs.discord_utils.Context import Context
from cogs.discord_utils.Embeds import ClodEmbed
from clodbot import python
from bot import ClodBot
import logging
from pathlib import Path

log = logging.getLogger("clodbot.cogs.admin")

space = "    "
branch = "│   "
tee = "├── "
last = "└── "

ignore = {".git", "__pycache__", ".idea", "venv"}


def tree(dir_path: Path, prefix: str = ""):
    # https://stackoverflow.com/questions/9727673/list-directory-tree-structure-in-python
    contents = list(dir_path.iterdir())
    pointers = [tee] * (len(contents) - 1) + [last]
    for pointer, path in zip(pointers, contents):
        yield prefix + pointer + path.name
        if path.is_dir() and not (
            path.name in ignore
        ):  # don't want a huge tree with the .git files in them
            extension = branch if pointer == tee else space
            yield from tree(path, prefix=prefix + extension)


class AdminCog(commands.Cog):
    def __init__(self, bot: ClodBot):
        self.bot = bot

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
            "_": self.last_result,
        }
        env.update(globals())
        output = await python.execute(code, env)

        if output.status and not isinstance(output.returned, Exception):
            self.last_result = output.returned

        await ctx.tick(output.status)
        embed = ClodEmbed(description=str(output), status=output.status).set_footer(
            text=output.time
        )
        await ctx.safe_send(embed=embed)

    @commands.command(hidden=True)
    async def tree(self, ctx):
        treeString = "```py\n"
        for line in tree(Path(".")):
            treeString += line + "\n"
        treeString += "```"
        embed = ClodEmbed(description=treeString)
        await ctx.safe_send(embed=embed)


async def setup(bot):
    await bot.add_cog(AdminCog(bot))
