from textwrap import TextWrapper
from typing import Optional

import discord

from clodbot.utils import Cache, divide_iterable, myShorten

from .context import Context
from .embeds import ClodEmbed


class Source:
    def __init__(self, data):
        self.data = data

    def formatter(self, page):
        return page

    async def get_page(self, index):
        return {"content": self.data[index]}

    def max_index(self):
        return len(self.data) - 1


class TableSource(Source):
    def __init__(self, data, max_rows=20, head_embed=None, heading=None):
        super(TableSource, self).__init__(data)
        self.data = divide_iterable(data, max_rows)
        self.head_embed: Optional[ClodEmbed] = head_embed
        if self.head_embed:
            self.original_footer = self.head_embed.get_footer()
        self.wrapper = TextWrapper(width=20, max_lines=1)
        self.heading = heading

    @Cache
    def get_max_widths(self, index):
        page = self.data[index]
        return [max(*map(lambda x: len(str(x[i])), page)) for i in range(len(page[0]))]

    def formatter(self, index):
        # TODO: Dynamically resizing headings
        page = self.data[index]
        widths = TableSource.get_max_widths(self, index)
        for row in page:
            string = ""
            for i, item in enumerate(row):
                if isinstance(item, int | float):
                    string = string + f"|{item:{widths[i]}d}"
                elif isinstance(item, str):
                    self.wrapper.width = widths[i]
                    string = string + f"|{myShorten(item, self.wrapper)}"
            yield string

    async def get_page(self, index: int):
        table = "\n".join(self.formatter(index))
        text = f"page {index + 1} / {self.max_index() + 1} "
        if self.original_footer:
            self.head_embed.set_footer(text=text + self.original_footer)
        return {"content": f"```fix\n{table}\n```", "embed": self.head_embed}


class Menu(discord.ui.View):
    def __init__(self, source: Source, ctx: Context | discord.Interaction):
        super().__init__()
        self.source: Source = source
        self.ctx: Context | discord.Interaction = ctx
        self.message: Optional[discord.Message] = None
        self.current_index: int = 0

    async def show_page(self, interaction: discord.Interaction):
        kwargs = await self.source.get_page(self.current_index)
        await interaction.response.edit_message(**kwargs)

    async def on_timeout(self) -> None:
        if self.message:
            await self.message.edit(view=None)

    async def start(self):
        kwargs = await self.source.get_page(0)
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
