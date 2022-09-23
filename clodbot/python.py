import ast
import textwrap
from clodbot.utils import SimpleTimer
import traceback
from contextlib import redirect_stdout
import io


def insert_returns(body):
    # insert return stmt if the last expression is a expression statement
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    # for if statements, we insert returns into the body and the orelse
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    # for with blocks, again we insert returns into the body
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)


def cleanup_code(content: str) -> str:
    """Automatically removes code blocks from the code."""
    # remove ```py\n```
    if content.startswith("```") and content.endswith("```"):
        return "\n".join(content.split("\n")[1:-1])

    return content.strip("` \n")


async def execute(code, env):
    code = f'async def _func():\n{textwrap.indent(cleanup_code(code), "  ")}'
    parsed = ast.parse(code)
    insert_returns(parsed.body[0].body)
    status: bool
    output: str
    time: str
    stdout = io.StringIO()

    try:
        exec(compile(parsed, filename="<ast>", mode="exec"), env)
    except Exception as e:
        value = stdout.getvalue()
        status = False
        output = f"{value}{e.__class__.__name__}: {e}"
        time = "could not compile"
        return status, output, time

    try:
        with redirect_stdout(stdout):
            with SimpleTimer() as timer:
                returned = await eval(f"_func()", env)
        value = stdout.getvalue()
        output = f"Printed:\n{value}\nReturned:\n{returned}"
        status = True
        time = str(timer)
        return status, output, time
    except Exception as e:
        status = False
        output = f"{traceback.format_exc()}\n{str(e)}"
        time = "could not compute"
        return status, output, time
