import datetime
import io
from textwrap import TextWrapper

import discord
from discord import app_commands
from discord.ext import commands
from reactionmenu import ViewMenu

import settings
from bot import ClodBot
from clodbot.aakash_scraper import aakash_db, analysis, scraper
from clodbot.utils import SimpleTimer, myShorten
from cogs.discord_utils.embeds import ClodEmbed
from cogs.discord_utils.interactors import add_navigators


async def tests_autocomplete(_, current: str):
    w = TextWrapper(width=90, max_lines=1)
    if len(current) < 4:
        tests = await aakash_db.view_last_15_tests()
        return [
            app_commands.Choice(name=myShorten(test[0], w), value=test[1])
            for test in tests
        ]
    tests = await aakash_db.tests_fts(current)
    return [
        app_commands.Choice(name=myShorten(test[0], w), value=test[1]) for test in tests
    ]


async def make_results_menu(
    results: tuple[aakash_db.Result],
    embed: ClodEmbed,
    interaction: discord.Interaction,
):
    async def results_formatter():
        w = TextWrapper(width=20, max_lines=1)
        for i, result in enumerate(results):
            student = await result.student.fetch()
            shortened_name = myShorten(student.name, w)
            air = result.AIR
            phy = result.physics
            chem = result.chemistry
            math = result.maths
            yield f"|{phy+chem+math:3d}|{phy:3d}|{chem:3d}|{math:3d}|{air:5d}|{shortened_name}"

    menu = ViewMenu(
        interaction,
        menu_type=ViewMenu.TypeEmbedDynamic,
        rows_requested=20,
        custom_embed=embed,
        wrap_in_codeblock="fix",
    )

    if len(results) == 0:
        menu.add_row("Nothing to show here")

    test_info = await results[0].test.fetch()
    menu.add_row(test_info.name)
    menu.add_row(test_info.date)
    menu.add_row(f"Centre Attendance - {test_info.centre_attendance}")
    menu.add_row(f"National Attendance - {test_info.national_attendance}")
    menu.add_row("")
    menu.add_row("|TOT|PHY|CHM|MTH| AIR |NAME")
    menu.add_row(f"|~~~|~~~|~~~|~~~|~~~~~|{'~'*20}")
    async for line in results_formatter():
        menu.add_row(line)
    add_navigators(menu)

    return menu


class Aakash(commands.Cog):
    def __init__(self, bot: ClodBot):
        self.bot = bot
        self.d_day = datetime.datetime(2023, 1, 24, 5, 30, 0)

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
    @app_commands.guilds(1038025610913656873, settings.DEV_GUILD)
    @app_commands.describe(test="Start searching for a test while I autocomplete.")
    @app_commands.autocomplete(test=tests_autocomplete)
    async def results(self, interaction: discord.Interaction, test: str):
        with SimpleTimer("SELECT results") as timer:
            results = await aakash_db.view_results(test)
        if results is None:
            await interaction.response.send_message(
                "Your test has to be **selected** from the autocomplete menu "
                "above, if it isn't there, it hasn't been added to the database yet, contact clodman",
                ephemeral=True,
            )
            return

        embed = ClodEmbed(title="Test Results").set_footer(text=timer)
        menu = await make_results_menu(results, embed, interaction)

        await menu.start()

    @app_commands.command(name="export", description="Get test results in csv format.")
    @app_commands.guilds(1038025610913656873, settings.DEV_GUILD)
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


async def setup(bot):
    await bot.add_cog(Aakash(bot))
