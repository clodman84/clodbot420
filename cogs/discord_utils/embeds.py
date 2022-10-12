from clodbot import utils
from discord import Embed
from discord.ext import commands
import settings


def makeEmbeds(string, prefix="```py\n", suffix="```", status=True):

    return [
        ClodEmbed(description=f"{prefix}{d}{suffix}", status=status)
        for d in utils.divideIterable(string, 4000)
    ]


class ClodEmbed(Embed):
    """
    Just an embed with colours and __str__() method.
    """

    def __init__(self, *args, status=True, **kwargs):
        """

        Parameters
        ----------
        args
        status
            If True (default) then the embed will be the default bot colour, if False, it will be red.
        kwargs
        """
        super().__init__(
            *args, colour=(settings.COLOUR if status else 0xFF0000), **kwargs
        )

    def __str__(self) -> str:
        return "\n".join(utils.dictionaryFormatter(self.to_dict()))


class EmbedInterface:
    """Creates an interface for navigating between embeds, with buttons and all that."""

    def __init__(self, bot: commands.Bot, embeds: list):
        raise NotImplementedError
