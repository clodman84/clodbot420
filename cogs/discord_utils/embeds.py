from discord import Embed

import settings
from clodbot import utils


def makeEmbedsFromString(string, prefix="```py\n", suffix="```", status=True):

    return [
        ClodEmbed(description=f"{prefix}{d}{suffix}", status=status)
        for d in utils.divide_iterable(string, 4000)
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

    def get_footer(self):
        if hasattr(self, "_footer"):
            return self._footer.get("text")
        return ""

    def __str__(self) -> str:
        return "\n".join(utils.format_dictionary(self.to_dict()))
