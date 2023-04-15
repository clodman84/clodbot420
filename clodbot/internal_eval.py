import ast
import io
import logging
import textwrap
from contextlib import redirect_stdout

from clodbot.utils import SimpleTimer

log = logging.getLogger("clodbot.core.intenal_eval")


def insert_returns(body):
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)


def cleanup_code(content: str) -> str:
    if content.startswith("```") and content.endswith("```"):
        return "\n".join(content.split("\n")[1:-1])
    return content.strip("` \n")


class Output:
    def __init__(
        self, status: bool, value: str, returned, time: str = "could not compute"
    ) -> None:
        """Output that holds the result of code execution

        Args:
            status (bool): The status of the execution, False if there was an error
            value (str): The values printed to stdout
            returned (any): The returned object from code execution
            time (str, optional): The time it took to execute. Defaults to "could not compute".
        """
        self.status = status
        self.value = value
        self.returned = returned
        self.time = time

    def __str__(self) -> str:
        value = self.value
        returned = self.returned
        if not self.status:
            return f"{value}{returned.__class__.__name__}: {returned}"
        output = (
            f"Printed:\n"
            f"```py\n"
            f"{None if value == '' else value}\n"
            f"```\n"
            f"Returned:\n"
            f"```py\n"
            f"{returned}\n"
            f"```"
        )
        return output


async def execute(code, env) -> Output:
    code = f'async def _func():\n{textwrap.indent(cleanup_code(code), "  ")}'
    status: bool
    time: str
    stdout = io.StringIO()

    try:
        parsed = ast.parse(code)
        insert_returns(parsed.body[0].body)
        exec(compile(parsed, filename="<ast>", mode="exec"), env)
    except Exception as returned:
        value = stdout.getvalue()
        status = False
        return Output(status, value, returned)

    try:
        with redirect_stdout(stdout):
            with SimpleTimer() as timer:
                returned = await eval("_func()", env)
        value = stdout.getvalue()

        status = True
        time = str(timer)
        return Output(status, value, returned, time)

    except Exception as returned:
        value = stdout.getvalue()
        status = False
        return Output(status, value, returned)
