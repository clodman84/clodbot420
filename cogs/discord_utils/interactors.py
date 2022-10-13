from bot import ClodBot
from .context import Context
from .embeds import ClodEmbed
from typing import Callable, List
from discord import Message, ui, ButtonStyle, Interaction


class InteractionCancelledError(Exception):
    pass


class YesOrNoMenu(ui.View):
    """
    simple menu with yes or no buttons.
    """

    def __init__(self, yesCallback, noCallback, author, timeout=120):
        super().__init__(timeout=timeout)
        self.tickCallback = yesCallback
        self.crossCallback = noCallback
        self.author = author

    async def interaction_check(self, interaction: Interaction, /) -> bool:
        return interaction.user == self.author

    @ui.button(label="Yes", style=ButtonStyle.green)
    async def yesButton(self, interaction: Interaction, _):
        await interaction.response.defer()
        await self.tickCallback()
        self.stop()

    @ui.button(label="No", style=ButtonStyle.red)
    async def noButton(self, interaction: Interaction, _):
        await interaction.response.defer()
        await self.crossCallback()
        self.stop()


class TextInteractor:
    """
    A simple way to interact with the user in an interactive conversational way. Handles input conversion and
    validation, cancellation and the message loop. All you need to do is pass in a dictionary, then `await
    TextInteractor.getResponse()` to get back the same dictionary with all the values filled in by the user.

    Other methods:
        cleanup() to delete all the back and forth messages between clodbot and the user

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

    def __init__(self, queries: dict, prompts: dict, ctx: Context, bot: ClodBot):
        """
        Parameters
        ----------
        queries:
            The user will be prompted to enter a value for each key. If the value for a key in this `queries` dictionary
            is a function, then it is called on the user input to further validate the user response. The callable
            should raise a ValueError to reject an input and return the value it wants to store as a response. This
            behaviour can be used to set defaults, convert the user input into types, etc.
        prompts:
            If a key from `queries` is present in this, it is what the user will see, if it isn't, it will default to an
            "Enter {key}: " prompt.
        ctx:
            The Context to do all the questioning
        bot:
            The bot user
        """
        self.queries = queries
        self.prompts = {
            key: prompts[key] if key in prompts else f"Enter {key}:" for key in queries
        }
        self.bot = bot
        self.author = ctx.author
        self.ctx = ctx
        self.interactions: List[Message] = []

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
                description=f"```fix\n{self.prompts[key]}:\n```"
            ).set_footer(text="Say 'cancel!' to stop")
            while True:
                prompt = await ctx.send(embed=promptEmbed)
                self.interactions.append(prompt)
                response: Message = await bot.wait_for(
                    "message",
                    check=lambda x: x.author == self.author
                    and x.channel == ctx.channel,
                )
                self.interactions.append(response)
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
                        error = await ctx.send(embed=errorEmbed)
                        self.interactions.append(error)
                        continue
                self.queries[key] = response
                break
        return self.queries

    async def cleanup(self):
        """
        Deletes every interaction between the bot and the user, neat and tidy.
        """
        await self.ctx.channel.delete_messages(self.interactions)
