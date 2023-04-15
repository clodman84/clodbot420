import ast
import asyncio
import logging
from base64 import b64decode, b64encode
from dataclasses import dataclass

from clodbot import clod_http, database
from clodbot.utils import SimpleTimer

_log = logging.getLogger("clodbot.core.python")


@dataclass(frozen=True)
class File:
    name: str
    content: bytes

    @property
    def json_object(self):
        return {"path": self.name, "content": b64encode(self.content).decode("ascii")}


class Output:
    # TODO: Holds the result of an evaluation -> A list of Files, output message, error message
    def __init__(self):
        pass


def search_imports(code: str):
    source = ast.parse(code)
    for node in ast.walk(source):
        if isinstance(node, ast.Import):
            yield from (i.name for i in node.names)
        if isinstance(node, ast.ImportFrom):
            yield node.module


class EvaluationFiles:
    def __init__(self, code: str):
        self.code: str = code
        self.unseen_files = set(search_imports(code))
        self.unseen_files.add("main.py")
        self.seen_files = set()

    def __aiter__(self):
        return self

    async def __anext__(self) -> File:
        try:
            while True:
                filename = self.unseen_files.pop()
                self.seen_files.add(filename)
                _log.debug("Current File:", filename)

                if filename == "main.py":
                    return File("main.py", self.code.encode())

                content = await search_file(123, filename)
                if content is not None:
                    break

                _log.debug("File not found, popping another file...")

            new_imports = tuple(
                filter(lambda x: x not in self.seen_files, search_imports(content))
            )
            if new_imports:
                self.unseen_files.add(*new_imports)
            _log.debug("Unseen Files:", self.unseen_files)
            _log.debug("Scheduled for evaluation:", self.seen_files)
            return File(f"{filename}.py", content.encode())

        except KeyError:
            raise StopAsyncIteration


# TODO: Implement these functions
async def search_file(user_id, filename):
    if filename == "file":
        return "import banana\nprint('hello world from file!')"
    if filename == "banana":
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
async def post_code(content: str):
    session = clod_http.SingletonSession()
    with SimpleTimer() as timer:
        file_list = [f.json_object async for f in EvaluationFiles(content)]
        json = {"args": ["main.py"], "files": file_list}
    print(timer)
    async with session.post("http://localhost:8060/eval", json=json) as response:
        return await response.json()


async def main():
    async with clod_http.SingletonSession():
        data = await post_code("import file\nprint('Hello World!')")
        print("Output:", data["stdout"])
        print("Files:", [b64decode(i["content"]) for i in data["files"]])


if __name__ == "__main__":
    asyncio.run(main())
