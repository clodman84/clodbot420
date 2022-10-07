from discord.ext import commands
from cogs.discord_utils.Context import Context
from cogs.discord_utils.Embeds import ClodEmbed
from clodbot import python
from bot import ClodBot
import logging
from pathlib import Path
import psutil

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
        if path.is_dir() and not (path.name in ignore):
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
    async def dir(self, ctx):
        treeString = "\n".join(tree(Path(".")))
        embed = ClodEmbed(description=f"```py\n{treeString}\n```")
        await ctx.safe_send(embed=embed)

    @commands.command(hidden=True)
    async def perf(self, ctx):
        stats = f"```py\nMemory:\n\t{psutil.virtual_memory()}\n\nCPU Frequency:\n\t{psutil.cpu_freq()}\n```"
        await ctx.send(embed=ClodEmbed(description=stats))


async def setup(bot):
    await bot.add_cog(AdminCog(bot))
