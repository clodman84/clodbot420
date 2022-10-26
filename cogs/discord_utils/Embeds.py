from clodbot import utils
from discord import Embed
from discord.ext import commands
import settings


def makeEmbeds(string, prefix='```py\n', suffix='```'):
    return [ClodEmbed(description=f"{prefix}{d}{suffix}") for d in utils.divideIterable(string, 1950)]


class ClodEmbed(Embed):
    """Just colour for now"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, colour=settings.COLOUR, **kwargs)


class EmbedInterface:
    """Creates an interface for navigating between embeds, with buttons and all that."""
    def __init__(self, bot: commands.Bot, embeds: list):
        raise NotImplementedError


