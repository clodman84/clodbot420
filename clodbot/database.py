import aiosqlite
import logging
import queue
from dataclasses import dataclass, astuple
from clodbot.utils import Cache

_log = logging.getLogger("clodbot.core.db")

# doing this because discord IDs are bigger than the maximum size of sqlite integers
_MAX_SQLITE_INT = 2**63 - 1
aiosqlite.register_adapter(int, lambda x: hex(x) if x > _MAX_SQLITE_INT else x)
aiosqlite.register_converter("integer", lambda b: int(b, 16 if b[:2] == b"0x" else 10))


class PillAlreadyExists(Exception):
    pass


@dataclass(slots=True, frozen=True, order=True)
class Pill:
    timestamp: int
    pill: str
    basedMessage: str
    senderID: int
    receiverID: int
    channelID: int
    messageID: int
    guildID: int

    @property
    def jumpURL(self):
        return f"https://discord.com/channels/{self.guildID}/{self.channelID}/{self.messageID}"


def pharmacy(_, row: tuple):
    """
    A row factory for pills.
    """
    return Pill(*row)


class ConnectionPool:
    _q = queue.SimpleQueue()

    def __init__(self, row_factory=pharmacy):
        self.connection = None
        self.row_factory = row_factory

    async def __aenter__(self):
        try:
            self.connection = self._q.get_nowait()
        except queue.Empty:
            self.connection = await aiosqlite.connect("data.db")
        self.connection.row_factory = self.row_factory
        return self.connection

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._q.put(self.connection)

    @classmethod
    async def close(cls):
        while not cls._q.empty():
            await cls._q.get_nowait().close()
        _log.debug("ConnectionPool Closed")


@Cache
async def viewPill(rowID: int):
    _log.debug("SELECT Pill: %s", rowID)
    async with ConnectionPool() as db:
        res = await db.execute("SELECT * FROM pills WHERE rowid = ?", (rowID,))
        pill = await res.fetchone()
        return pill


@Cache(maxsize=1000, ttl=120)
async def pills_fts(text: str, guildID: int):
    async with ConnectionPool(lambda _, y: y) as db:
        res = await db.execute(
            f"SELECT pill, rowid, rank FROM pills_fts WHERE "
            f"pill MATCH ? AND guildID = ? ORDER BY rank LIMIT 15",
            (text, guildID),
        )
        matched_pills = await res.fetchall()
        return matched_pills


@Cache
async def last15pills(guildID: int):
    async with ConnectionPool(lambda _, y: y) as db:
        res = await db.execute(
            "SELECT pill, rowid FROM pills WHERE guildID = ? ORDER BY timestamp LIMIT 15",
            (guildID,),
        )
        pills = await res.fetchall()
        return pills


@Cache
async def viewPillsReceived(userID: int):
    _log.debug("SELECT pills received by %s", userID)
    async with ConnectionPool() as db:
        res = await db.execute("SELECT * FROM pills WHERE receiverID = ?", (userID,))
        pills = await res.fetchall()
        return pills


@Cache
async def viewPillsGiven(userID: int):
    _log.debug("SELECT pills given by %s", userID)
    async with ConnectionPool() as db:
        res = await db.execute("SELECT * FROM pills WHERE senderID = ?", (userID,))
        pills = await res.fetchall()
        return pills


async def insertPill(pill: Pill, db: aiosqlite.Connection) -> None:
    """
    Inserts pill objects into the database
    """
    _log.debug(
        "INSERT pills given by %s to %s in server %s",
        pill.senderID,
        pill.receiverID,
        pill.guildID,
    )
    viewPillsGiven.remove(pill.senderID)
    viewPillsReceived.remove(pill.receiverID)
    last15pills.remove(pill.guildID)
    data = astuple(pill)
    try:
        await db.execute("INSERT INTO pills VALUES(?, ?, ?, ?, ?, ?, ?, ?)", data)
    except aiosqlite.IntegrityError as e:
        _log.error(f"{e.__class__.__name__} {e.args}")
        raise PillAlreadyExists
