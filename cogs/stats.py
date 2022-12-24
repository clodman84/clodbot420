import psutil
from discord.ext import commands, tasks

import clodbot.database
from bot import ClodBot
from clodbot import pills, utils
from cogs.discord_utils.context import Context
from cogs.discord_utils.embeds import ClodEmbed


class StatsCog(commands.Cog):
    def __init__(self, bot: ClodBot):
        self.bot = bot
        self.insertTimes.start()
        self.process = psutil.Process()

    @commands.command()
    async def perf(self, ctx: Context):
        """
        Gives performance metrics for the bot, mostly memory usage.
        """
        description = (
            f"```fix\n"
            f"{utils.natural_size(self.process.memory_full_info().uss)} - {self.process.memory_percent('uss')}%\n"
            f"{self.process.cpu_percent()} % CPU Usage\n"
            f"Running on {psutil.cpu_count()} CPUs and {self.process.num_threads()} threads\n```"
        )
        await ctx.send(
            embed=ClodEmbed(title="Performance Metrics", description=description)
        )

    @commands.command()
    async def rtt(self, ctx: Context):
        """
        Calculates Round-Trip Time to the API
        """
        # stolen from jishaku but modified to fit clodbot's style, these metrics are also recorded, because of the timer
        message = None
        api_readings = []
        websocket_readings = []

        for _ in range(5):
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
                with utils.SimpleTimer("API Latency") as timer:
                    await message.edit(embed=embed)
                api_readings.append(timer.time)
            else:
                with utils.SimpleTimer("API Latency") as timer:
                    message = await ctx.send(embed=embed)
                api_readings.append(timer.time)
            # Ignore websocket latencies that are 0 or negative because they usually mean we've got bad heartbeats
            if self.bot.latency > 0.0:
                websocket_readings.append(self.bot.latency)

    @tasks.loop(seconds=10)
    async def insertTimes(self):
        await clodbot.database.insert_timers(utils.SimpleTimer(), self.bot.db)

    async def cog_unload(self) -> None:
        self.insertTimes.stop()


async def setup(bot):
    await bot.add_cog(StatsCog(bot))
