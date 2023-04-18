import ast
import contextlib
import itertools
import logging
import re
from base64 import b64decode, b64encode
from dataclasses import dataclass
from io import StringIO
from signal import Signals

from clodbot import clod_http, database
from clodbot.utils import Cache, SimpleTimer, natural_size

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


class EvaluationFiles:
    def __init__(self, user_id: int, code: str):
        self.code: str = code
        self.unseen_files = set(scan_for_imports(code))
        self.unseen_files.add("main")
        self.seen_files = set()
        self.user_id = user_id

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
                content = await search_file(self.user_id, f"{filename}.py")
                if content:
                    break

            new_imports = tuple(
                filter(
                    lambda x: x not in self.seen_files,
                    scan_for_imports(content.decode()),
                )
            )
            if new_imports:
                self.unseen_files.update(new_imports)
            return File(f"{filename}.py", content)
        except KeyError:
            raise StopAsyncIteration


def scan_for_imports(code: str):
    try:
        source = ast.parse(code)
    except SyntaxError:
        return
    for node in ast.walk(source):
        if isinstance(node, ast.Import):
            yield from (i.name for i in node.names)
        if isinstance(node, ast.ImportFrom):
            yield node.module


@Cache
async def search_file(user_id, filename: str) -> bytes | None:
    async with database.ConnectionPool(lambda _, y: y) as db:
        res = await db.execute(
            "SELECT content FROM files WHERE userID = ? and filename = ?",
            (user_id, filename),
        )
        content = await res.fetchone()
        return content[0] if content else None


@Cache
async def get_file(row_id):
    async with database.ConnectionPool(lambda _, y: y) as db:
        res = await db.execute(
            "SELECT userID, filename, content FROM files WHERE rowid = ?", (row_id,)
        )
        content = await res.fetchone()
        return content


async def update_file(user_id, filename: str, content: bytes, db):
    search_file.remove(user_id, filename)
    # when sqlite crosses 3.38 within python, change this is strftime('%s')
    await db.execute(
        "UPDATE files SET content = ?, last_updated = strftime('%s') WHERE userID = ? and filename = ?",
        (content, user_id, filename),
    )


async def save_file(user_id, filename: str, content: bytes, db):
    search_file.remove(user_id, filename)
    await db.execute(
        "INSERT INTO files VALUES(strftime('%s'), ?, ?, ?, strftime('%s'))",
        (user_id, filename, content),
    )


async def delete_file(user_id, filename, db):
    search_file.remove(user_id, filename)
    query = await db.execute(
        "SELECT rowid FROM files WHERE userID = ? AND filename = ?", (user_id, filename)
    )
    (row_id,) = await query.fetchone()
    get_file.remove(row_id)
    await db.execute("DELETE FROM files WHERE rowid = ?", (row_id,))


async def files_fts(text, user_id):
    async with database.ConnectionPool(lambda _, y: y) as db:
        res = await db.execute(
            "SELECT filename, rowid FROM files_fts WHERE "
            "filename MATCH ? AND userID = ? ORDER BY rank LIMIT 15",
            (text, user_id),
        )
        matched_files = await res.fetchall()
        return matched_files


async def view_15_files(user_id):
    async with database.ConnectionPool(lambda _, y: y) as db:
        res = await db.execute(
            "SELECT filename, rowid FROM files WHERE userID = ? ORDER BY last_updated DESC LIMIT 15",
            (user_id,),
        )
        pills = await res.fetchall()
        return pills


async def post_code(user_id: int, content: str) -> Output:
    session = clod_http.SingletonSession()
    with SimpleTimer() as timer:
        file_list = [
            file.to_json_object() async for file in EvaluationFiles(user_id, content)
        ]
        json = {"args": ["main.py"], "files": file_list}
    _log.debug("Task - collect all files to evaluate - {}".format(timer))
    async with session.post("http://localhost:8060/eval", json=json) as response:
        json = await response.json()
        return Output(json)
