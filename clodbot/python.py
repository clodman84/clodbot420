import asyncio
from base64 import b64decode, b64encode
from dataclasses import dataclass

from clodbot import clod_http
from clodbot.utils import SimpleTimer


@dataclass(frozen=True)
class File:
    name: str
    content: bytes

    @property
    def json_object(self):
        return {"path": self.name, "content": b64encode(self.content).decode("ascii")}


class EvaluationFiles:
    def __init__(self, code: str):
        self.code: str = code
        self.files = self.search_imports()
        self.files.append("main.py")

    def search_imports(self):
        # this is supposed to have a regex that matches all import statements
        return []

    def __aiter__(self):
        return self

    async def __anext__(self) -> File:
        # this bit is supposed to search through the database, matching file names with imports
        # this isn't "parallel" though, so I *might* change this to some sort of .gather()
        try:
            filename = self.files.pop()
            if filename == "main.py":
                return File("main.py", self.code.encode())
            content = b'print("Placeholder")'
            return File(filename, content)
        except IndexError:
            raise StopAsyncIteration


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
