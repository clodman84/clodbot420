from discord.ext import commands
from cogs.discord_utils.Context import Context
from cogs.discord_utils.Embeds import ClodEmbed
from bot import ClodBot
from contextlib import redirect_stdout
from clodbot.utils import SimpleTimer
from typing import Optional, Any

import logging
import io
import traceback
import textwrap

log = logging.getLogger('clodbot.admin')


class AdminCog(commands.Cog):
    # borrowed from RoboDanny
    def __init__(self, bot: ClodBot):
        self.bot = bot
        self._last_result: Optional[Any] = None

    async def cog_check(self, ctx: Context):
        return await self.bot.is_owner(ctx.author)

    @staticmethod
    def cleanup_code(content: str) -> str:
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    @commands.command(hidden=True, name='eval')
    async def _eval(self, ctx: Context, *, body: str):
        """Evaluates a code"""

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result,
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with SimpleTimer() as timer:
                with redirect_stdout(stdout):
                    ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except Exception as e:
                log.error(f"While adding reaction to eval command {e.__class__.__name__}: {e}")

            self._last_result = ret
            description = f'```py\n{value}Returned: {ret}\n```'
            await ctx.send(embed=ClodEmbed(description=description).set_footer(text=f"{timer}"))


async def setup(bot):
    await bot.add_cog(AdminCog(bot))
