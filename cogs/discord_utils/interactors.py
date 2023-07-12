from textwrap import TextWrapper
from typing import Callable, List

import discord
from discord import ButtonStyle, Interaction, Message, app_commands, ui

from bot import ClodBot
from clodbot.utils import Cache, my_shorten

from .context import Context
from .embeds import ClodEmbed


def autocomplete(preview, search, attribute=None, user_attribute=False):
    w = TextWrapper(width=90, max_lines=1)

    @Cache(maxsize=256, ttl=30)
    async def completer(metadata, current: str):
        if len(current) < 4:
            values = await preview(metadata)
        else:
            values = await search(current, metadata)
        return [
            app_commands.Choice(name=f"{my_shorten(value[0], w)}", value=value[1])
            for value in values
        ]

    async def coro_wrapper(interaction: discord.Interaction, current: str):
        # this helps with the Cache since interactions are always different...
        # and in discord/app_commands/commands.py _populate_autocomplete() there is an iscoroutinefunction() check
        if attribute:
            metadata = (
                getattr(interaction.user, attribute)
                if user_attribute
                else getattr(interaction, attribute)
            )
        else:
            metadata = None
        return await completer(metadata, current)

    return coro_wrapper


class InteractionCancelledError(Exception):
    pass


class YesOrNoMenu(ui.View):
    """
    simple menu with yes or no buttons.
    """

    def __init__(self, author, timeout=120):
        super().__init__(timeout=timeout)
        self.value = False
        self.author = author

    async def interaction_check(self, interaction: Interaction, /) -> bool:
        return interaction.user == self.author

    @ui.button(label="Yes", style=ButtonStyle.green)
    async def yes_button(self, interaction: Interaction, _):
        await interaction.response.defer()
        self.value = True
        self.disable()

    @ui.button(label="No", style=ButtonStyle.red)
    async def no_button(self, interaction: Interaction, _):
        await interaction.response.defer()
        self.disable()

    def disable(self):
        for button in self.children:
            button.disabled = True
        self.stop()

    async def on_timeout(self) -> None:
        self.disable()


class TextInteractor:
    """
    A simple way to interact with the user in an interactive conversational way. Handles input conversion and
    validation, cancellation and the message loop. All you need to do is pass in a dictionary, then `await
    TextInteractor.get_responses()` to get back the same dictionary with all the values filled in by the user.

    Other methods:
        cleanup() to delete all the back and forth messages between clodbot and the user

    Example
    -------
        Getting a description from a user that is less than 1000 characters long, and a status that is a boolean: ::

            def check_length(desc):
                if len(desc) > 1000:
                    raise ValueError("Description too long")
                return str(desc)

            queries = {
                        "description": check_length,
                        "status": lambda x: x.lower() in {"true", "y, "yes"},
                        "footer": None  # This will accept any value
                    }
            interactor = TextInteractor(queries, ctx, bot)
            response = await interactor.get_responses()
    """

    def __init__(self, queries: dict, ctx: Context, bot: ClodBot, prompts: dict = None):
        """
        Parameters
        ----------
        queries:
            The user will be prompted to enter a value for each key. If the value for a key in this `queries` dictionary
            is a function, then it is called on the user input to further validate the user response. The callable
            should raise a ValueError to reject an input and return the value it wants to store as a response. This
            behaviour can be used to set defaults, convert the user input into types, etc.
        ctx:
            The Context to do all the questioning
        bot:
            The bot user
        prompts:
            If a key from `queries` is present in this, it is what the user will see, if it isn't, it will default to an
            "Enter {key}: " prompt. This is an optional argument that defaults to an empty dictionary.
        """
        if prompts is None:
            prompts = {}
        self.queries = queries
        self.prompts = {
            key: prompts[key] if key in prompts else f"Enter {key}:" for key in queries
        }
        self.bot = bot
        self.author = ctx.author
        self.ctx = ctx
        self.interactions: List[Message] = []

    async def get_responses(self) -> dict:
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
            prompt_embed = ClodEmbed(
                description=f"```fix\n{self.prompts[key]}:\n```"
            ).set_footer(text="Say 'cancel!' to stop")
            while True:
                prompt = await ctx.send(embed=prompt_embed)
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
                    except ValueError as err:
                        error_embed = ClodEmbed(
                            description=f"There was something wrong with your input. {err}",
                            status=False,
                        )
                        error = await ctx.send(embed=error_embed)
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
