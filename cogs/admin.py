import logging
from pathlib import Path
from typing import Callable

import discord
from discord.ext import commands

from bot import ClodBot
from clodbot import python
from cogs.discord_utils.context import Context
from cogs.discord_utils.embeds import ClodEmbed
from cogs.discord_utils.interactors import (
    InteractionCancelledError,
    TextInteractor,
    YesOrNoMenu,
)

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
            response = await interactor.get_responses()
        except InteractionCancelledError:
            await interactor.cleanup()
            await ctx.tick(False)
            return

        embed = ClodEmbed(**response)
        sendConfirm = YesOrNoMenu(ctx.author)

        confirmationMessage = await ctx.send(
            "Send this embed?", embed=embed, view=sendConfirm
        )
        await sendConfirm.wait()
        await confirmationMessage.edit(view=sendConfirm)

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
    async def sync(self, ctx: Context):
        sync_confirmation_menu = YesOrNoMenu(ctx.author)
        confirmation_message = await ctx.send(
            "Are you sure you want to sync all servers?", view=sync_confirmation_menu
        )
        await sync_confirmation_menu.wait()
        await confirmation_message.edit(view=sync_confirmation_menu)

        if not sync_confirmation_menu.value:
            await ctx.tick(False)
            return

        await self.bot.tree.sync()
        await ctx.send(embed=ClodEmbed(description="Syncing completed to all servers!"))

    @commands.command()
    async def logs(self, ctx: Context):
        file = discord.File("./app.log")
        await ctx.send(file=file)


async def setup(bot):
    await bot.add_cog(AdminCog(bot))
