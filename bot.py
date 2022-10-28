import logging
import queue
import traceback
from contextlib import contextmanager
from logging.handlers import QueueHandler, QueueListener, RotatingFileHandler

import aiosqlite
import discord
from discord.ext import commands

import clodbot.database as database
import settings
from clodbot.http import SingletonSession
from cogs.discord_utils.context import Context
from cogs.discord_utils.embeds import ClodEmbed, makeEmbedsFromString

log = logging.getLogger("clodbot")
log.setLevel(logging.DEBUG)


class ClodBot(commands.Bot):
    def __init__(self, initialExt):
        intents = discord.Intents(
            guilds=True,
            members=True,
            bans=True,
            emojis=True,
            voice_states=True,
            messages=True,
            reactions=True,
            message_content=True,
        )

        super().__init__(
            command_prefix="--",
            description="Sulfate and Paraben free.",
            intents=intents,
        )
        self.error_hook = None
        self.db = None
        self.dev_guild = settings.DEV_GUILD
        self.initialExt = initialExt

    async def setup_hook(self) -> None:
        for extension in self.initialExt:
            await self.load_extension(extension)
        session = SingletonSession(loop=self.loop)
        self.error_hook = discord.Webhook.from_url(
            url=settings.ERROR_WEBHOOK, session=session
        )
        self.db: aiosqlite.Connection = await aiosqlite.connect(
            "data.db", isolation_level=None
        )
        await self.db.executescript(
            """
            pragma journal_mode = wal;
            pragma synchronous = normal;
        """
        )
        log.info("Setup Hook Complete!")

    async def close(self):
        log.info("Closing connection to Discord.")
        await SingletonSession().close()
        await self.db.close()
        await database.ConnectionPool.close()
        await super().close()

    async def get_context(self, message, *, cls=Context) -> Context:
        return await super().get_context(message, cls=cls)

    async def on_command_error(
        self, ctx: Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send("This command cannot be used in private messages.")
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send("This command is disabled and cannot be used.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"Dude, chill. {str(error)}")
        elif isinstance(error, commands.NotOwner):
            await ctx.send("This command can only be used by my owner.")
        elif isinstance(error, commands.CommandInvokeError):
            log.error(f"In command {ctx.command.qualified_name}: {str(error)}")
            await ctx.send("Something went wrong.")
            original = error.original
            if not isinstance(original, discord.HTTPException):
                trace = (
                    f"In command '{ctx.command.qualified_name}':\n"
                    + "".join(traceback.format_tb(original.__traceback__))
                    + str(error)
                )
                for message in makeEmbedsFromString(trace, status=False):
                    await self.error_hook.send(embed=message)
        elif isinstance(error, commands.UserInputError):
            errorEmbed = ClodEmbed(
                description=f"{str(error).capitalize()}. Your command isn't correct/complete. Use "
                f"'--help {ctx.command.qualified_name}' to learn how to use this "
                f"command. Idiot.",
                status=False,
            )
            await ctx.send(embed=errorEmbed)


@contextmanager
def logConfig():
    logger = logging.getLogger()

    logging.getLogger("discord").setLevel(logging.DEBUG)
    logging.getLogger("discord.http").setLevel(logging.INFO)
    logging.getLogger("discord.gateway").setLevel(logging.INFO)
    logging.getLogger("discord.client").setLevel(logging.INFO)
    logging.getLogger("discord.webhook").setLevel(logging.INFO)

    q = queue.Queue(-1)
    q_handler = QueueHandler(q)

    logFileHandler = RotatingFileHandler(
        filename="app.log",
        encoding="utf-8",
        maxBytes=75 * 1024,
        backupCount=5,
    )
    dt_fmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(
        "[{threadName:<10}] [{asctime}] [{levelname:<8}] {name}: {message}",
        dt_fmt,
        style="{",
    )

    listener = QueueListener(q, logFileHandler)
    logger.addHandler(q_handler)
    logFileHandler.setFormatter(formatter)
    listener.start()
    try:
        yield
    finally:
        logFileHandler.close()
        listener.stop()


def main():
    with logConfig():
        ext = ["cogs.admin", "cogs.pills"]
        bot = ClodBot(ext)
        log.info("Starting Bot")
        bot.run(token=settings.DISCORD_TOKEN, root_logger=True)


if __name__ == "__main__":
    main()
