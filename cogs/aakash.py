"""
THIS FILE IS NEVER TOUCHED BY THE PROGRAM.
It's in here for historic purposes only.
"""

import datetime
import io

import discord
from discord import app_commands
from discord.ext import commands

import cogs.discord_utils.interactors as interactors
import cogs.discord_utils.menus as menus
import settings
from bot import ClodBot
from clodbot.aakash_scraper import aakash_db, analysis, scraper
from clodbot.utils import SimpleTimer
from cogs.discord_utils.embeds import ClodEmbed

tests_autocomplete = interactors.autocomplete(
    preview=aakash_db.view_last_15_tests, search=aakash_db.tests_fts
)
students_autocomplete = interactors.autocomplete(
    preview=aakash_db.view_15_students_sorted_alpha, search=aakash_db.students_fts
)


class Aakash(commands.Cog):
    def __init__(self, bot: ClodBot):
        self.bot = bot
        self.d_day = datetime.datetime(2023, 6, 3, 18, 30, 0)

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

    @commands.is_owner()
    @commands.command(hidden=True)
    async def add_test(self, ctx, test_id):
        await ctx.send(f"Scraping test -> {test_id}")
        val = await scraper.scrape(test_id)
        if val:
            students, results, test = val
        else:
            await ctx.send("No valid responses received from Aakash!")
            return
        with SimpleTimer("INSERT test") as test_time:
            await aakash_db.insert_test(test, self.bot.db)
        with SimpleTimer("INSERT students") as student_time:
            await aakash_db.insert_students(students, self.bot.db)
        with SimpleTimer("INSERT results") as results_time:
            await aakash_db.insert_results(results, self.bot.db)
        embed = ClodEmbed(
            description=f"Done!\nINSERTS for tests {test_time}, students {student_time}, results {results_time}."
        )
        await ctx.send(embed=embed)

    @app_commands.command(name="results", description="Aakash test results")
    @app_commands.guilds(1038025610913656873, 1060954891482308759, settings.DEV_GUILD)
    @app_commands.describe(test="Start searching for a test while I autocomplete.")
    @app_commands.autocomplete(test=tests_autocomplete)
    async def results(self, interaction: discord.Interaction, test: str):
        with SimpleTimer("SELECT results") as timer:
            results: list[aakash_db.Result] = await aakash_db.view_results(test)
        if results is None:
            await interaction.response.send_message(
                "Your test has to be **selected** from the autocomplete menu "
                "above, if it isn't there, it hasn't been added to the database yet, contact clodman",
                ephemeral=True,
            )
            return
        test_info = results[0].test
        metrics = (
            f"Centre Attendance - {test_info.centre_attendance}\n"
            f"National Attendance - {test_info.national_attendance}\n"
            f"Date - {test_info.date}"
        )
        embed = ClodEmbed(title=test_info.name)
        embed.add_field(name="Info", value=metrics)
        heading = ("TOT", "PHY", "CHM", "MTH", "AIR", "NAME")
        data = tuple(result.get_row() for result in results)
        source = menus.TableSource(data, head_embed=embed, heading=heading)
        menu = menus.Menu(source, interaction)
        await menu.start()

    @app_commands.command(name="export", description="Get test results in csv format.")
    @app_commands.guilds(1038025610913656873, 1060954891482308759, settings.DEV_GUILD)
    @app_commands.describe(test="Start searching for a test while I autocomplete.")
    @app_commands.autocomplete(test=tests_autocomplete)
    async def export(self, interaction: discord.Interaction, test: str):
        with SimpleTimer("Make CSV") as timer:
            data = await analysis.make_csv(test)
            csv_file = io.BytesIO(data)
        embed = ClodEmbed(
            description="Here's the csv file for this test, you can open this in Excel and weep."
        )
        embed.set_footer(text=timer)
        file = discord.File(csv_file, filename="test_results.csv")
        await interaction.response.send_message(embed=embed, file=file)

    @app_commands.command(
        name="report", description="Student performance reports. Yeah..."
    )
    @app_commands.guilds(1038025610913656873, 1060954891482308759, settings.DEV_GUILD)
    @app_commands.describe(
        student="Start searching for a student while I autocomplete."
    )
    @app_commands.autocomplete(student=students_autocomplete)
    async def report(self, interaction: discord.Interaction, student: str):
        with SimpleTimer("Make Report") as timer:
            report = await analysis.make_student_report(student)
            student = await aakash_db.get_student_from_roll(student)
        embed = ClodEmbed(title=student.name)
        for key, value in report.items():
            if key == "total":
                data = (
                    f"Growth Rate            | {value['growth_rate']:.2f}%\n"
                    f"Average Score          | {value['average_score']}\n"
                    f"Average Percentile     | {value['average_rank']:.2f}"
                )
                embed.add_field(name="Overall", value=f"```fix\n{data}\n```")
            else:
                data = (
                    f"Growth Rate            | {value['growth_rate']:.2f}%\n"
                    f"Average Score          | {value['average_score']}\n"
                    f"Average Rank           | {value['average_rank']:.2f}"
                )
                embed.add_field(name=key.capitalize(), value=f"```fix\n{data}\n```")
        embed.set_footer(text=timer)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="history", description="Get a student's test history")
    @app_commands.guilds(1038025610913656873, 1060954891482308759, settings.DEV_GUILD)
    @app_commands.describe(
        student="Start searching for a student while I autocomplete."
    )
    @app_commands.autocomplete(student=students_autocomplete)
    async def history(self, interaction: discord.Interaction, student: str):
        with SimpleTimer("SELECT student results") as timer:
            results = await aakash_db.get_student_results(roll_no=student)
        if results is None:
            await interaction.response.send_message(
                "Your test has to be **selected** from the autocomplete menu "
                "above, if it isn't there, it hasn't been added to the database yet, contact clodman",
                ephemeral=True,
            )
            return

        embed = ClodEmbed(title=f"{results[0].student.name}").set_footer(text=timer)
        heading = ("TOT", "PHY", "CHM", "MTH", "AIR", "DATE")
        data = tuple(result.get_row(test=True) for result in results)
        source = menus.TableSource(data, head_embed=embed, heading=heading)
        menu = menus.Menu(source, interaction)
        await menu.start()


async def setup(bot):
    await bot.add_cog(Aakash(bot))
