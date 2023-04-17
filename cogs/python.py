from io import BytesIO

import discord
from discord import File, app_commands
from discord.ext import commands

from bot import ClodBot
from clodbot import python
from clodbot.internal_eval import cleanup_code
from cogs.discord_utils import interactors
from cogs.discord_utils.context import Context
from cogs.discord_utils.embeds import ClodEmbed


def py_filename_convertor(argument: str):
    return argument if argument.endswith(".py") else f"{argument}.py"


files_autocomplete = interactors.autocomplete(
    preview=python.view_15_files,
    search=python.files_fts,
    attribute="id",
    user_attribute=True,
)


class Python(commands.Cog):
    def __init__(self, bot: ClodBot):
        self.bot = bot

    @commands.max_concurrency(1, per=commands.BucketType.user)
    @commands.group(invoke_without_command=True)
    async def py(self, ctx: Context, *, code: str):
        async with ctx.typing():
            output = await python.post_code(ctx.author.id, cleanup_code(code))
            await ctx.tick(output.status)
            embed = ClodEmbed(
                status=output.status, description=f"```py\n{output.stdout or '...'}```"
            )
            embed.add_field(name="Status", value=output.get_status_message())
            files = [
                File(BytesIO(file.content), filename=file.get_discord_name())
                for file in output.files
            ]
            await ctx.send(embed=embed, files=files)

    @py.command()
    async def save(self, ctx: Context, filename: py_filename_convertor, *, code: str):
        exists = await python.search_file(ctx.author.id, filename)
        if exists:
            await ctx.tick(False)
            await ctx.send(
                f"{filename} already exists, you might want to use "
                f"--py update {filename} {code:<20} instead"
            )
            return
        code = cleanup_code(code)
        await python.save_file(ctx.author.id, filename, code.encode(), self.bot.db)
        await ctx.tick(True)
        await ctx.send(f"Saved file {filename}!")

    @py.command()
    async def update(self, ctx: Context, filename: py_filename_convertor, *, code: str):
        exists = await python.search_file(ctx.author.id, filename)
        if not exists:
            await ctx.tick(False)
            await ctx.send(
                f"{filename} doesn't exist, you might want to use "
                f"--py save {filename} {code:<20} instead"
            )
            return
        code = cleanup_code(code)
        await python.update_file(ctx.author.id, filename, code.encode(), self.bot.db)
        await ctx.tick(True)
        await ctx.send(f"Updated file {filename}!")

    @py.command()
    async def delete(self, ctx: Context, filename: py_filename_convertor):
        exists = await python.search_file(ctx.author.id, filename)
        if not exists:
            await ctx.tick(False)
            await ctx.send(
                f"{filename} doesn't exist, you might want to use /view to look at all the files you have saved."
            )
            return
        queries = {"filename": lambda x: x == filename}
        prompts = {"filename": f"Say '{filename}' to delete the file"}
        interactor = interactors.TextInteractor(queries, ctx, self.bot, prompts)
        try:
            await interactor.get_responses()
        except interactors.InteractionCancelledError:
            await interactor.cleanup()
            await ctx.tick(False)
            return
        await python.delete_file(ctx.author.id, filename, self.bot.db)
        await ctx.tick(True)

    @app_commands.command(description="Runs a python file you have saved.")
    @app_commands.describe(file="Start searching for a file while I autocomplete.")
    @app_commands.autocomplete(file=files_autocomplete)
    async def run(self, interaction: discord.Interaction, file: int):
        content = await python.get_file(file)
        if not content or content[0] != interaction.user.id:
            await interaction.response.send_message(
                "Your file has to be **selected** from the autocomplete menu "
                "above, if it isn't there, it doesn't exist.",
                ephemeral=True,
            )
            return
        await interaction.response.defer()
        output = await python.post_code(
            interaction.user.id, cleanup_code(content[2].decode())
        )
        embed = ClodEmbed(
            status=output.status, description=f"```py\n{output.stdout or '...'}```"
        )
        embed.add_field(name="Status", value=output.get_status_message())
        files = [
            File(BytesIO(file.content), filename=file.get_discord_name())
            for file in output.files
        ]
        await interaction.followup.send(embed=embed, files=files)

    @app_commands.command(
        description="Sends the source code for a python file you have saved."
    )
    @app_commands.describe(file="Start searching for a file while I autocomplete.")
    @app_commands.autocomplete(file=files_autocomplete)
    async def view(self, interaction: discord.Interaction, file: int):
        content = await python.get_file(file)
        if not content or content[0] != interaction.user.id:
            await interaction.response.send_message(
                "Your file has to be **selected** from the autocomplete menu "
                "above, if it isn't there, it doesn't exist.",
                ephemeral=True,
            )
            return
        code = content[2].decode()
        embed = ClodEmbed(description=f"```py\n{code}```")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Python(bot))
