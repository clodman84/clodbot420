import re
import time
from textwrap import TextWrapper, shorten

import discord
from discord import app_commands
from discord.ext import commands

import clodbot.pills as database
import cogs.discord_utils.menus as menus
from bot import ClodBot
from clodbot.utils import SimpleTimer, myShorten
from cogs.discord_utils.embeds import ClodEmbed


async def pillsAutocomplete(interaction: discord.Interaction, current: str):
    w = TextWrapper(width=90, max_lines=1)
    if len(current) < 4:
        pills = await database.view_last_15_pills(interaction.guild_id)
        return [
            app_commands.Choice(name=myShorten(pill[0], w), value=pill[1])
            for pill in pills
        ]
    pills = await database.pills_fts(current, interaction.guild_id)
    return [
        app_commands.Choice(name=myShorten(pill[0], w), value=pill[1]) for pill in pills
    ]


class PillsCog(commands.Cog):
    def __init__(self, bot: ClodBot):
        self.bot = bot
        self.basedRegex = re.compile(r"based and (.*?) pilled", re.IGNORECASE)
        self.context_menu = app_commands.ContextMenu(
            name="Show Pills", callback=self.showPills
        )
        self.bot.tree.add_command(self.context_menu)

    async def send_pill_menu(
        self, member, ctx: commands.Context | discord.Interaction, is_receiver=True
    ):
        with SimpleTimer("SELECT pills") as timer:
            if is_receiver:
                pills = await database.view_pills_received(member.id, ctx.guild.id)
            else:
                pills = await database.view_pills_given(member.id, ctx.guild.id)

        def extractor(pill: database.Pill):
            user_id = pill.senderID if is_receiver else pill.receiverID
            return pill.pill, self.bot.get_user(user_id).display_name

        embed = ClodEmbed(title=f"{member.name}'s pills").set_footer(text=timer)
        extracted = map(extractor, pills)
        data = tuple((i + 1, *j) for i, j in enumerate(extracted))
        if not pills:
            data = (
                (
                    1,
                    "<anything>",
                    "somebody who thinks you're based"
                    if is_receiver
                    else "somebody based",
                ),
            )
            prefix = (
                "When you say something incredibly based and someone else replies to your message "
                if is_receiver
                else "When you read something incredibly based and reply to that message "
            )
            body = "with the phrase 'based and <anything> pilled' where <anything> can be absolutely anything, clodbot will detect this and maintain a log of all the times this has happened."
            embed.add_field(name="Nothing to show!", value=prefix + body)
        heading = ("No.", "Pill", "Awarder" if is_receiver else "Awardee")
        source = menus.TableSource(data, head_embed=embed, heading=heading)
        menu = menus.Menu(source, ctx)
        await menu.start()

    @commands.Cog.listener("on_message")
    async def detect_based_messages(self, message: discord.Message):
        if message.reference is None:
            return
        match = self.basedRegex.search(message.content)
        if not match:
            return
        og: discord.Message = message.reference.resolved
        if og.author.id == message.author.id or og.content == "":
            return
        pillMessage = match.group(1).strip()
        pill = database.Pill(
            int(time.time()),
            pillMessage,
            og.content,
            message.author.id,
            og.author.id,
            message.channel.id,
            message.id,
            message.guild.id,
        )
        with SimpleTimer("INSERT pill") as timer:
            try:
                await database.insert_pill(pill, self.bot.db)
                embed = ClodEmbed(
                    description=f"{og.author.mention} you are now based and {shorten(pillMessage, 1000)} pilled!"
                )
            except database.PillAlreadyExists:
                embed = ClodEmbed(
                    description=f"Someone is already based and {shorten(pillMessage, 1000)} pilled in this server!"
                )
        embed.set_footer(text=timer)
        await message.channel.send(embed=embed)

    @commands.hybrid_group(name="pills")
    async def pill(self, ctx: commands.Context):
        await ctx.send(
            'Use "--pill received/given <@member>" , this command can\'t be invoked like this.'
        )

    @pill.command(name="received", description="Shows pills received in this server")
    async def received(self, ctx: commands.Context, member: discord.Member):
        ctx = ctx.interaction if ctx.interaction else ctx
        # the line above makes the reactionmenu library treat this context
        # as an interaction if it was invoked with a slash command
        await self.send_pill_menu(member, ctx)

    @pill.command(name="given", description="Shows pills given in this server")
    async def given(self, ctx: commands.Context, member: discord.Member):
        ctx = ctx.interaction if ctx.interaction else ctx
        await self.send_pill_menu(member, ctx, is_receiver=False)

    async def showPills(self, ctx: discord.Interaction, member: discord.Member):
        await self.send_pill_menu(member, ctx)

    @app_commands.command(
        name="search", description="Searches for a specific pill in the server"
    )
    @app_commands.describe(pill="Start searching for a pill while I autocomplete.")
    @app_commands.autocomplete(pill=pillsAutocomplete)
    async def search(self, interaction: discord.Interaction, pill: int):
        with SimpleTimer("SELECT pill") as timer:
            pill: database.Pill = await database.view_pill(pill)
        if pill is None:
            await interaction.response.send_message(
                "Your pill has to be **selected** from the autocomplete menu "
                "above, if it isn't there, it doesn't exist.",
                ephemeral=True,
            )
            return
        if pill.guildID != interaction.guild_id:
            await interaction.response.send_message(
                "This pill is not from your server", ephemeral=True
            )
            return
        view = discord.ui.View()
        jump_button = discord.ui.Button(url=pill.jumpURL, label="Jump To Message")
        view.add_item(jump_button)

        author = self.bot.get_user(pill.receiverID)
        embed = (
            ClodEmbed(
                description=f"{shorten(pill.basedMessage, width=2000)}",
                url=pill.jumpURL,
            )
            .set_author(name=author.name, icon_url=author.display_avatar.url)
            .add_field(name="Pill:", value=shorten(pill.pill, width=1000))
            .add_field(name="Awarded by:", value=f"<@{pill.senderID}>")
            .add_field(name="Awarded on:", value=f"<t:{pill.timestamp}>")
            .add_field(name="Channel:", value=f"<#{pill.channelID}>")
            .set_footer(text=timer)
        )
        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(PillsCog(bot))
