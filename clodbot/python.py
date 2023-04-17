import ast
import asyncio
import contextlib
import itertools
import logging
import re
from base64 import b64decode, b64encode
from dataclasses import dataclass
from io import StringIO
from signal import Signals

from clodbot import clod_http, database
from clodbot.utils import SimpleTimer, natural_size

_log = logging.getLogger("clodbot.core.python")
MAX_FILE_SIZE = 8 * 1024 * 1024  # 8MB

# ANSI escape sequences
RE_ANSI = re.compile(r"\\u.*\[(.*?)m")
# Characters with a leading backslash
RE_BACKSLASH = re.compile(r"\\.")
# Discord disallowed file name characters
RE_DISCORD_FILE_NAME_DISALLOWED = re.compile(r"[^a-zA-Z0-9._-]+")


@dataclass(frozen=True)
class File:
    name: str
    content: bytes

    def to_json_object(self):
        return {"path": self.name, "content": b64encode(self.content).decode("ascii")}

    @classmethod
    def from_json_object(cls, obj):
        return cls(obj["path"], b64decode(obj["content"]))

    def get_discord_name(self):
        name = RE_ANSI.sub("_", self.name)
        name = RE_BACKSLASH.sub("_", name)
        # Replace any disallowed character with an underscore
        name = RE_DISCORD_FILE_NAME_DISALLOWED.sub("_", name)
        return name


class Output:
    # TODO: Holds the result of an evaluation -> A list of Files, output message, error message
    def __init__(self, json: dict):
        self.stdout = json["stdout"]
        self.return_code = json["returncode"]
        # self.files only consists of the first 10 files in the json with size less than MAX_FILE_SIZE
        filtered = itertools.islice(
            filter(lambda x: x["size"] < MAX_FILE_SIZE, json["files"]), 0, 10
        )
        self.files = [File.from_json_object(file) for file in filtered]  # only 10
        # number of discarded files
        self.files_discarded = (
            files_discarded
            if (files_discarded := len(json["files"]) - len(self.files)) > 0
            else False
        )

    @property
    def status(self):
        return self.return_code == 0

    def get_status_message(self):
        with StringIO() as message:
            message.write("Your eval job")
            if self.return_code is None:
                message.write(" has failed")
            elif self.return_code == 137:
                message.write(" timed out or ran out of memory")
            elif self.return_code == 255:
                message.write(" has failed")
            else:
                message.write(f" has completed with return code {self.return_code}")
                # Try to append signal's name if one exists
                with contextlib.suppress(ValueError):
                    name = Signals(self.return_code - 128).name
                    message.write(f" ({name})")
            if self.files_discarded:
                message.write(
                    f"\n\n{self.files_discarded} {'file was' if self.files_discarded == 1 else 'files were'} "
                    f"discarded from this output.\n**Files created cannot exceed {natural_size(MAX_FILE_SIZE)} "
                    f"and more than 10 files cannot be sent!**"
                )
            return message.getvalue()


def search_imports(code: str):
    try:
        source = ast.parse(code)
    except SyntaxError:
        return
    for node in ast.walk(source):
        if isinstance(node, ast.Import):
            yield from (i.name for i in node.names)
        if isinstance(node, ast.ImportFrom):
            yield node.module


class EvaluationFiles:
    def __init__(self, code: str):
        self.code: str = code
        self.unseen_files = set(search_imports(code))
        self.unseen_files.add("main")
        self.seen_files = set()

    def __aiter__(self):
        return self

    async def __anext__(self) -> File:
        try:
            while True:
                filename = self.unseen_files.pop()
                self.seen_files.add(filename)
                if filename == "main":
                    return File("main.py", self.code.encode())
                # filenames will be stored with the .py extension, future versions might allow saving other file types.
                content = await search_file(123, f"{filename}.py")
                if content is not None:
                    break

            new_imports = tuple(
                filter(lambda x: x not in self.seen_files, search_imports(content))
            )
            if new_imports:
                self.unseen_files.update(new_imports)
            return File(f"{filename}.py", content.encode())
        except KeyError:
            raise StopAsyncIteration


# TODO: Implement these functions
async def search_file(user_id, filename):
    if filename == "file.py":
        return "import banana\nprint('hello world from file!')"
    if filename == "banana.py":
        return "import file\nprint(2+2, 'from banana')"


async def update_file(user_id, filename):
    pass


async def save_file(user_id, filename):
    pass


async def files_fts(curr, user_id):
    pass


async def view_15_files(user_id):
    pass


# TODO: post_code() should return a list of Files and an Output and all that
async def post_code(content: str) -> Output:
    session = clod_http.SingletonSession()
    with SimpleTimer() as timer:
        file_list = [file.to_json_object() async for file in EvaluationFiles(content)]
        json = {"args": ["main.py"], "files": file_list}
    _log.debug("Task - collect all files to evaluate - {}".format(timer))
    async with session.post("http://localhost:8060/eval", json=json) as response:
        json = await response.json()
        return Output(json)


async def main():
    async with clod_http.SingletonSession():
        data = await post_code("import file\nprint('Hello World!')")
        print("Output:", data.stdout)
        print("Files:", data.files)


if __name__ == "__main__":
    asyncio.run(main())
