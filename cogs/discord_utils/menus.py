from textwrap import TextWrapper
from typing import Optional

import discord

from clodbot.utils import divide_iterable, myShorten

from .context import Context
from .embeds import ClodEmbed


class Source:
    def __init__(self, data):
        self.data = data

    def formatter(self, page):
        return page

    async def get_page(self, index):
        return {"content": self.data[index]}


class TableSource(Source):
    def __init__(self, data, max_rows=20, head_embed=None | ClodEmbed):
        super(TableSource, self).__init__(data)
        self.data = divide_iterable(data, max_rows)
        self.head_embed = head_embed
        self.wrapper = TextWrapper(width=20, max_lines=1)

    def formatter(self, page):
        for row in page:
            string = ""
            for item in row:
                if item is int | float:
                    string += f"|{item:3d}"
                elif item is str:
                    string += f"|{myShorten(item, self.wrapper)}"
            yield string

    async def get_page(self, index: int):
        page = self.data[index]
        table = "\n".join(self.formatter(page))
        return {"content": f"```fix\n{table}\n```", "embed": self.head_embed}


class Menu(discord.ui.View):
    def __init__(self, source: Source, *, interaction: discord.Interaction):
        super().__init__()
        self.source: Source = source
        self.interaction = interaction
        self.message: Optional[discord.Message] = None
        self.current_index: int = 0

    async def show_page(self, interaction: discord.Interaction):
        kwargs = await self.source.get_page(self.current_index)
        await interaction.message.edit(**kwargs)

    async def start(self):
        pass
