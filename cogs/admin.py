from discord.ext import commands
from cogs.discord_utils.Context import Context
from cogs.discord_utils.Embeds import ClodEmbed
from clodbot import python, utils
from bot import ClodBot
from typing import List, Collection, Tuple
import math
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


def mean_stddev(collection: Collection[float]) -> Tuple[float, float]:
    """
    Takes a collection of floats and returns (mean, stddev) as a tuple. Stolen from Jishaku, used by the rtt command.
    """
    average = sum(collection) / len(collection)
    if len(collection) > 1:
        stddev = math.sqrt(
            sum(math.pow(reading - average, 2) for reading in collection)
            / (len(collection) - 1)
        )
    else:
        stddev = 0.0
    return average, stddev


def natural_size(size_in_bytes: int) -> str:
    """
    Converts a number of bytes to an appropriately-scaled unit
    E.g.:
        1024 -> 1.00 KiB
        12345678 -> 11.77 MiB
    """
    units = ("B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB")

    power = int(math.log(max(abs(size_in_bytes), 1), 1024))

    return f"{size_in_bytes / (1024 ** power):.2f} {units[power]}"


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
        summary = ""
        try:
            proc = psutil.Process()

            with proc.oneshot():
                try:
                    mem = proc.memory_full_info()
                    summary += (
                        f"Using {natural_size(mem.rss)} bytes physical memory and "
                        f"{natural_size(mem.vms)} bytes virtual memory, "
                        f"{natural_size(mem.uss)} bytes of which unique to this process.\n"
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
    async def rtt(self, ctx):

        """
        Calculates Round-Trip Time to the API. Stolen from Jishaku with minor changes to fit clodbot's style.
        """

        message = None

        # We'll show each of these readings as well as an average and standard deviation.
        api_readings: List[float] = []
        # We'll also record websocket readings, but we'll only provide the average.
        websocket_readings: List[float] = []

        # We do 6 iterations here.
        # This gives us 5 visible readings, because a request can't include the stats for itself.
        for _ in range(6):
            # First generate the text
            text = "Calculating round-trip time...\n\n"
            text += "\n".join(
                f"Reading {index + 1}: {reading * 1000:.2f}ms"
                for index, reading in enumerate(api_readings)
            )

            if api_readings:
                average, stddev = mean_stddev(api_readings)
                text += f"\n\nAverage: {average * 1000:.2f} \N{PLUS-MINUS SIGN} {stddev * 1000:.2f}ms"
            else:
                text += "\n\nNo readings yet."

            if websocket_readings:
                average = sum(websocket_readings) / len(websocket_readings)
                text += f"\nWebsocket latency: {average * 1000:.2f}ms"
            else:
                text += f"\nWebsocket latency: {self.bot.latency * 1000:.2f}ms"

            embed = ClodEmbed(description=f"```fix\n{text}```")
            # Now do the actual request and reading
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
