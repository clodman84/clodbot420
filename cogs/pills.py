import math

from discord.ext import commands
from discord import app_commands
from cogs.discord_utils.embeds import ClodEmbed
import discord
import clodbot.database as database
import time
from reactionmenu import ViewMenu, ViewButton
import re
import random
import string
from clodbot.utils import SimpleTimer
from bot import ClodBot
from textwrap import TextWrapper


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

    def pillFormatter(self, pills: list[database.Pill], is_receiver: bool):
        w = TextWrapper(width=30, max_lines=1)
        for i, pill in enumerate(pills):
            shortenedPill = w.fill(" ".join(pill.pill.strip().split()))
            user = self.bot.get_user(pill.senderID if is_receiver else pill.receiverID)
            yield f"{i+1:3d}|{pill.pillID}| {shortenedPill} - {user.name}"

    def pillMenuMaker(
        self,
        pills,
        embed: ClodEmbed,
        is_receiver: bool,
        ctx: commands.Context | discord.Interaction,
    ):
        menu = ViewMenu(
            ctx,
            menu_type=ViewMenu.TypeEmbedDynamic,
            rows_requested=10,
            custom_embed=embed,
            wrap_in_codeblock="fix",
        )
        if len(pills) == 0:
            menu.add_row("Nothing to show here")
        for line in self.pillFormatter(pills, is_receiver):
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
        pillID = "".join(random.choices(string.ascii_uppercase, k=8))
        pill = database.Pill(
            int(time.time()),
            pillMessage,
            og.content,
            message.author.id,
            og.author.id,
            message.channel.id,
            message.id,
            message.guild.id,
            pillID,
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

    @commands.hybrid_command(description="Shows a member's pills")
    async def pill(self, ctx: commands.Context, member: discord.Member):
        await ctx.send(f"Getting pills for {member.mention}...", ephemeral=True)
        with SimpleTimer() as timer:
            pills = await database.viewPillsReceived(member.id)
        filter(lambda x: x.guildID == member.guild.id, pills)
        pills.sort(reverse=True)
        embed = ClodEmbed(title=f"{member.name}'s pills").set_footer(text=timer)
        menu = self.pillMenuMaker(pills, embed, True, ctx)
        await menu.start()

    async def showPills(self, interaction: discord.Interaction, member: discord.Member):
        with SimpleTimer() as timer:
            pills = await database.viewPillsReceived(member.id)
        filter(lambda x: x.guildID == member.guild.id, pills)
        pills.sort(reverse=True)
        embed = ClodEmbed(title=f"{member.name}'s pills").set_footer(text=timer)
        menu = self.pillMenuMaker(pills, embed, True, interaction)
        await menu.start()


async def setup(bot):
    await bot.add_cog(PillsCog(bot))
