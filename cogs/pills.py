import re
import time
from textwrap import TextWrapper

import discord
from discord import app_commands
from discord.ext import commands
from reactionmenu import ViewButton, ViewMenu

import clodbot.database as database
from bot import ClodBot
from clodbot.utils import SimpleTimer
from cogs.discord_utils.embeds import ClodEmbed


async def pillsAutocomplete(interaction: discord.Interaction, current: str):
    if len(current) < 4:
        pills = await database.last15pills(interaction.guild_id)
        return [app_commands.Choice(name=pill[0], value=pill[1]) for pill in pills]
    pills = await database.pills_fts(current, interaction.guild_id)
    return [app_commands.Choice(name=pill[0], value=pill[1]) for pill in pills]


class PillsCog(commands.Cog):
    def __init__(self, bot: ClodBot):
        self.bot = bot
        self.basedRegex = re.compile(
            r"based and (([\w\"'-]+\s+)+)pilled", re.IGNORECASE
        )
        self.context_menu = app_commands.ContextMenu(
            name="Show Pills", callback=self.showPills
        )
        self.bot.tree.add_command(self.context_menu)

    def pillMenuMaker(
        self,
        pills,
        embed: ClodEmbed,
        is_receiver: bool,
        ctx: commands.Context | discord.Interaction,
    ):
        def pillFormatter():
            w = TextWrapper(width=30, max_lines=1)
            for i, pill in enumerate(pills):
                shortenedPill = w.fill(" ".join(pill.pill.strip().split()))
                user = self.bot.get_user(
                    pill.senderID if is_receiver else pill.receiverID
                )
                yield f"|{i + 1:3d}| {shortenedPill} - {user.name}"

        menu = ViewMenu(
            ctx,
            menu_type=ViewMenu.TypeEmbedDynamic,
            rows_requested=10,
            custom_embed=embed,
            wrap_in_codeblock="fix",
        )

        if len(pills) == 0:
            menu.add_row("Nothing to show here")
        for line in pillFormatter():
            menu.add_row(line)

        menu.add_button(
            ViewButton(
                style=discord.ButtonStyle.green,
                label="Back",
                custom_id=ViewButton.ID_PREVIOUS_PAGE,
            )
        )
        menu.add_button(
            ViewButton(
                style=discord.ButtonStyle.green,
                label="Next",
                custom_id=ViewButton.ID_NEXT_PAGE,
            )
        )
        menu.add_button(
            ViewButton(
                style=discord.ButtonStyle.red,
                label="Stop",
                custom_id=ViewButton.ID_END_SESSION,
            )
        )
        menu.add_button(
            ViewButton(
                style=discord.ButtonStyle.gray,
                label="Jump",
                custom_id=ViewButton.ID_GO_TO_PAGE,
            )
        )
        return menu

    async def pillMenuSender(self, member, ctx, fil, is_receiver=True):
        with SimpleTimer() as timer:
            if is_receiver:
                pills = await database.viewPillsReceived(member.id)
            else:
                pills = await database.viewPillsGiven(member.id)
        pills = list(filter(fil, pills))
        pills.sort(reverse=True)
        embed = ClodEmbed(title=f"{member.name}'s pills").set_footer(text=timer)
        menu = self.pillMenuMaker(pills, embed, is_receiver, ctx)
        await menu.start()

    @commands.Cog.listener("on_message")
    async def basedDetector(self, message: discord.Message):
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
        with SimpleTimer() as timer:
            try:
                await database.insertPill(pill, self.bot.db)
                embed = ClodEmbed(
                    description=f"{og.author.mention} you are now based and {pillMessage} pilled!"
                )
            except database.PillAlreadyExists:
                embed = ClodEmbed(
                    description=f"Someone is already based and {pillMessage} pilled in this server!"
                )
        embed.set_footer(text=timer)
        await message.channel.send(embed=embed)

    @commands.hybrid_group(name="pills")
    async def pill(self, ctx: commands.Context):
        await ctx.send(
            "Use --pill received or something, this command can't be invoked like this."
        )

    @pill.command(name="received")
    async def received(self, ctx: commands.Context, member: discord.Member):
        await ctx.send(f"Getting pills for {member.mention}...", ephemeral=True)
        await self.pillMenuSender(member, ctx, lambda x: x.guildID == member.guild.id)

    @pill.command(name="given")
    async def given(self, ctx: commands.Context, member: discord.Member):
        await ctx.send(f"Getting pills for {member.mention}...", ephemeral=True)
        await self.pillMenuSender(
            member, ctx, lambda x: x.guildID == member.guild.id, is_receiver=False
        )

    async def showPills(self, ctx: discord.Interaction, member: discord.Member):
        await self.pillMenuSender(member, ctx, lambda x: x.guildID == member.guild.id)

    @app_commands.command(name="pills_search")
    @app_commands.autocomplete(pill=pillsAutocomplete)
    async def search(self, interaction: discord.Interaction, pill: int):
        pill: database.Pill = await database.viewPill(pill)
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
            ClodEmbed(description=f"{pill.basedMessage}", url=pill.jumpURL)
            .set_author(name=author.name, icon_url=author.display_avatar.url)
            .add_field(name="Pill:", value=pill.pill)
            .add_field(name="Awarded by:", value=f"<@{pill.senderID}>")
            .add_field(name="Awarded on:", value=f"<t:{pill.timestamp}>")
            .add_field(name="Channel:", value=f"<#{pill.channelID}>")
        )
        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(PillsCog(bot))
