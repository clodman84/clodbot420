from bot import ClodBot
from .context import Context
from .embeds import ClodEmbed
from typing import Callable
from discord import Message


class InteractionCancelledError(Exception):
    pass


class TextInteractor:
    """
    A simple way to interact with the user in an interactive conversational way. Handles input conversion and validation,
    cancellation and the message loop. All you need to do is pass in a dictionary, then `await
    TextInteractor.getResponse()` to get back the same dictionary with all the values filled in by the user.

    Example
    -------
        Getting a description from a user that is less than 1000 characters long, and a status that is a boolean: ::

            def checkLength(desc):
                if len(desc) > 1000:
                    raise ValueError("Description too long")
                return str(desc)

            queries = {
                        "description": checkLength,
                        "status": lambda x: x.lower() in {"true", "y, "yes"},
                        "footer": None  # This will accept any value
                    }
            interactor = TextInteractor(queries, ctx, bot)
            response = await interactor.getResponses()
    """

    def __init__(self, queries: dict, ctx: Context, bot: ClodBot):
        """
        Parameters
        ----------
        queries:
            A dictionary of keys and values. The user will be prompted to enter a value for each key. If the value for a
            callable, then it is called on the user input to further validate the user response. The callable should
            raise a ValueError to reject an input and return the value it wants to store as a response.
        ctx:
            The Context to do all the questioning
        bot:
            The bot user
        """
        self.queries = queries
        self.bot = bot
        self.author = ctx.author
        self.ctx = ctx

    async def getResponses(self) -> dict:
        """
        Await this to get back a dictionary of user responses.

        Raises
        ------
            InteractionCancelledError
                If the user says 'cancel!' at any point
        """
        ctx = self.ctx
        bot = self.bot
        for key, value in self.queries.items():
            promptEmbed = ClodEmbed(
                description=f"```fix\nEnter {key}:\n```"
            ).set_footer(text="Say 'cancel!' to stop")
            while True:
                await ctx.send(embed=promptEmbed)
                response: Message = await bot.wait_for(
                    "message",
                    check=lambda x: x.author == self.author
                    and x.channel == ctx.channel,
                )
                response: str = response.content
                if response == "cancel!":
                    raise InteractionCancelledError
                # if the dictionary has a function in it, it is used to further validate and transform the response
                if isinstance(value, Callable):
                    try:
                        response = value(response)
                    except ValueError:
                        errorEmbed = ClodEmbed(
                            description=f"There was something wrong with your input. {ValueError}",
                            status=False,
                        )
                        await ctx.send(embed=errorEmbed)
                        continue
                self.queries[key] = response
                break
        return self.queries
