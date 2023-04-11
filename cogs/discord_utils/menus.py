import itertools
from io import StringIO
from textwrap import TextWrapper
from typing import Optional

import discord

from clodbot.utils import Cache, divide_iterable, myShorten

from .context import Context
from .embeds import ClodEmbed


class Source:
    def __init__(self, data):
        self.data = data

    async def get_page(self, index):
        return {"content": self.data[index]}

    def max_index(self):
        return len(self.data) - 1


class TableSource(Source):
    def __init__(self, data, max_rows=25, head_embed=None, heading=None):
        super(TableSource, self).__init__(data)
        self.data = divide_iterable(data, max_rows)
        self.head_embed: Optional[ClodEmbed] = head_embed
        if self.head_embed:
            self.original_footer = self.head_embed.get_footer()
        self.wrapper = TextWrapper(width=20, max_lines=1)
        self.wrapper.placeholder = "..."
        self.heading = heading

    def get_raw_page(self, index: int):
        if self.heading:
            return list(itertools.chain((self.heading,), self.data[index]))
        return self.data[index]

    def get_max_widths(self, index: int):
        page = self.get_raw_page(index)
        return [
            min(max(*map(lambda x: len(str(x[i])), page)), 30)
            for i in range(len(page[0]))
        ]

    @Cache
    async def get_page(self, index: int):
        page = self.get_raw_page(index)
        widths = self.get_max_widths(index)
        if self.heading:
            page.insert(1, tuple("-" * i for i in widths))
        with StringIO() as table:

            table.write("```fix\n")
            for row in page:
                for i, item in enumerate(row):
                    width = widths[i]
                    if isinstance(item, int | float):
                        table.write(f"|{item:{width}d}")
                    elif isinstance(item, str):
                        self.wrapper.width = width
                        table.write(f"|{myShorten(item, self.wrapper).ljust(width)}")
                table.write("\n")
            table.write("```")

            if self.head_embed:
                self.head_embed.description = table.getvalue()
                text = f"Page {index + 1} / {self.max_index() + 1} "
                self.head_embed.set_footer(text=text + self.original_footer)
                return {"embed": self.head_embed}
            return {"content": table.getvalue()}


class Menu(discord.ui.View):
    def __init__(self, source: Source, ctx: Context | discord.Interaction):
        super().__init__(timeout=60)
        self.source: Source = source
        self.ctx: Context | discord.Interaction = ctx
        self.message: Optional[discord.Message] = None
        self.current_index: int = 0

    async def show_page(self, interaction: discord.Interaction):
        kwargs = await TableSource.get_page(self.source, self.current_index)
        await interaction.response.edit_message(**kwargs)

    async def on_timeout(self) -> None:
        if self.message:
            await self.message.edit(view=None)

    async def start(self):
        kwargs = await TableSource.get_page(self.source, 0)
        if isinstance(self.ctx, Context):
            self.message = await self.ctx.send(**kwargs, view=self)
        elif isinstance(self.ctx, discord.Interaction):
            self.message = await self.ctx.response.send_message(**kwargs, view=self)

    @discord.ui.button(label="Back", style=discord.ButtonStyle.green)
    async def go_to_previous_page(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """go to the previous page"""
        self.current_index = (
            self.current_index - 1 if self.current_index > 0 else self.current_index
        )
        await self.show_page(interaction)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.green)
    async def go_to_next_page(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """go to the next page"""
        self.current_index = (
            self.current_index + 1
            if self.current_index < self.source.max_index()
            else self.current_index
        )
        await self.show_page(interaction)

    @discord.ui.button(label="Quit", style=discord.ButtonStyle.red)
    async def stop_pages(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """stops the pagination session."""
        await interaction.response.defer()
        await interaction.delete_original_response()
