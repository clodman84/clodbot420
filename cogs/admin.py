from discord.ext import commands
from cogs.discord_utils.context import Context
from cogs.discord_utils.embeds import ClodEmbed
from cogs.discord_utils.interactors import (
    TextInteractor,
    InteractionCancelledError,
    YesOrNoMenu,
)
from clodbot import python, utils
from pathlib import Path
from bot import ClodBot
from typing import Callable
import logging
import psutil
import discord

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
        self.last_result = None

    async def cog_check(self, ctx: Context):
        if await self.bot.is_owner(ctx.author):
            return True
        else:
            raise commands.NotOwner

    @commands.command(name="eval")
    async def _eval(self, ctx: Context, *, code: str):
        """
        Evaluates python code.
        """
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

    @commands.command()
    async def dir(self, ctx: Context):
        """
        Sends the current directory tree structure.
        """
        treeString = "\n".join(tree(Path(".")))
        embed = ClodEmbed(description=f"```py\n{treeString}\n```")
        await ctx.safe_send(embed=embed)

    @commands.command()
    async def perf(self, ctx: Context):
        """
        Gives performance metrics for the bot, mostly memory usage.
        """
        summary = ""
        try:
            proc = psutil.Process()

            with proc.oneshot():
                try:
                    mem = proc.memory_full_info()
                    summary += (
                        f"Using {utils.natural_size(mem.rss)} physical memory and "
                        f"{utils.natural_size(mem.vms)} virtual memory, "
                        f"{utils.natural_size(mem.uss)} of which unique to this process.\n"
                    )
                except psutil.AccessDenied:
                    pass

                try:
                    name = proc.name()
                    pid = proc.pid
                    thread_count = proc.num_threads()
                    summary += f"Running on PID {pid} (`{name}`) with {thread_count} thread(s).\n"
                except psutil.AccessDenied:
                    pass

                summary += "\n"  # blank line
        except psutil.AccessDenied:
            summary += (
                "psutil is installed, but this process does not have high enough access rights "
                "to query process information.\n"
            )
            summary += "\n"  # blank line
        await ctx.send(embed=ClodEmbed(description=f"```fix\n{summary}\n```"))

    @commands.command()
    async def embed(self, ctx: Context, channel: int):
        """
        Sends an embed to desired channel.
        """
        channel = self.bot.get_channel(channel)
        await ctx.send(
            embed=ClodEmbed(
                description=f"Sending embed to {channel.name} in {channel.guild.name}."
            )
        )
        none_to_skip: Callable = lambda x: None if x.lower().strip() == "none" else x
        queries = {
            "title": none_to_skip,
            "description": none_to_skip,
            "status": lambda x: x.lower().strip() in {"true", "y", "yes"},
            "url": none_to_skip,
        }
        prompts = {
            "title": "Enter title, say 'none' to skip",
            "description": "Enter description, say 'none' to skip",
            "status": "Enter status, if True, the embed will have the default colour, if False it will be Red",
            "url": "Enter url, say 'none' to skip",
        }
        interactor = TextInteractor(queries, ctx, self.bot, prompts)
        try:
            response = await interactor.getResponses()
        except InteractionCancelledError:
            await interactor.cleanup()
            await ctx.tick(False)
            return

        embed = ClodEmbed(**response)
        sendConfirm = YesOrNoMenu(ctx.author)

        await ctx.send("Send this embed?", embed=embed, view=sendConfirm)
        await sendConfirm.wait()

        if sendConfirm.value:
            await interactor.cleanup()
            await channel.send(embed=embed)
            await ctx.tick(True)
        else:
            await interactor.cleanup()
            await ctx.tick(False)

    @commands.command(name="dsync")
    async def dev_sync(self, ctx, guildID: int = None):
        guild = discord.Object(guildID if guildID else self.bot.dev_guild)
        self.bot.tree.copy_global_to(guild=guild)
        await self.bot.tree.sync(guild=guild)
        await ctx.send(embed=ClodEmbed(description="Syncing completed to server!"))

    @commands.command()
    async def logs(self, ctx: Context):
        file = discord.File("./app.log")
        await ctx.send(file=file)

    @commands.command()
    async def rtt(self, ctx: Context):
        """
        Calculates Round-Trip Time to the API. Stolen from Jishaku with minor changes to fit clodbot's style.
        """
        message = None
        api_readings = []
        websocket_readings = []

        for _ in range(6):
            text = "Calculating round-trip time...\n\n"
            text += "\n".join(
                f"Reading {index + 1}: {reading * 1000:.2f}ms"
                for index, reading in enumerate(api_readings)
            )

            if api_readings:
                average, stddev = utils.mean_stddev(api_readings)
                text += f"\n\nAverage: {average * 1000:.2f} \N{PLUS-MINUS SIGN} {stddev * 1000:.2f}ms"
            else:
                text += "\n\nNo readings yet."
            if websocket_readings:
                average = sum(websocket_readings) / len(websocket_readings)
                text += f"\nWebsocket latency: {average * 1000:.2f}ms"
            else:
                text += f"\nWebsocket latency: {self.bot.latency * 1000:.2f}ms"

            embed = ClodEmbed(description=f"```fix\n{text}```")
            if message:
                with utils.SimpleTimer() as timer:
                    await message.edit(embed=embed)
                api_readings.append(timer.time)
            else:
                with utils.SimpleTimer() as timer:
                    message = await ctx.send(embed=embed)
                api_readings.append(timer.time)
            # Ignore websocket latencies that are 0 or negative because they usually mean we've got bad heartbeats
            if self.bot.latency > 0.0:
                websocket_readings.append(self.bot.latency)


async def setup(bot):
    await bot.add_cog(AdminCog(bot))
