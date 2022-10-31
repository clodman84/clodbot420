import psutil
from discord.ext import commands, tasks

from bot import ClodBot
from clodbot import database, utils
from cogs.discord_utils.context import Context
from cogs.discord_utils.embeds import ClodEmbed


class StatsCog(commands.Cog):
    def __init__(self, bot: ClodBot):
        self.bot = bot
        self.insertTimes.start()

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

    @tasks.loop(seconds=10)
    async def insertTimes(self):
        await database.insertTimers(utils.SimpleTimer(), self.bot.db)

    async def cog_unload(self) -> None:
        self.insertTimes.stop()


async def setup(bot):
    await bot.add_cog(StatsCog(bot))
