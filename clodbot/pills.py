import logging
from dataclasses import astuple, dataclass

from aiosqlite import IntegrityError

from clodbot.database import ConnectionPool
from clodbot.utils import Cache

_log = logging.getLogger("clodbot.core.pills")


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
    def jump_url(self):
        return f"https://discord.com/channels/{self.guildID}/{self.channelID}/{self.messageID}"


def pharmacy(_, row: tuple):
    """
    A row factory for pills.
    """
    return Pill(*row)


@Cache
async def view_pill(rowID: int):
    async with ConnectionPool(pharmacy) as db:
        res = await db.execute("SELECT * FROM pills WHERE rowid = ?", (rowID,))
        pill = await res.fetchone()
        return pill


async def pills_fts(text: str, guildID: int):
    async with ConnectionPool(lambda _, y: y) as db:
        res = await db.execute(
            "SELECT pill, rowid, rank FROM pills_fts WHERE "
            "pill MATCH ? AND guildID = ? ORDER BY rank LIMIT 15",
            (text, guildID),
        )
        matched_pills = await res.fetchall()
        return matched_pills


@Cache
async def view_last_15_pills(guildID: int):
    async with ConnectionPool(lambda _, y: y) as db:
        res = await db.execute(
            "SELECT pill, rowid FROM pills WHERE guildID = ? ORDER BY timestamp DESC LIMIT 15",
            (guildID,),
        )
        pills = await res.fetchall()
        return pills


@Cache
async def view_pills_received(userID: int, guildID: int) -> list[Pill]:
    async with ConnectionPool(pharmacy) as db:
        res = await db.execute(
            "SELECT * FROM pills WHERE receiverID = ? AND guildID = ? ORDER BY timestamp DESC",
            (userID, guildID),
        )
        pills = await res.fetchall()
        return pills


@Cache
async def view_pills_given(userID: int, guildID: int) -> list[Pill]:
    async with ConnectionPool(pharmacy) as db:
        res = await db.execute(
            "SELECT * FROM pills WHERE senderID = ? AND guildID = ? ORDER BY timestamp DESC",
            (userID, guildID),
        )
        pills = await res.fetchall()
        return pills


async def insert_pill(pill: Pill, db) -> None:
    """
    Inserts pill objects into the database
    """
    view_pills_given.remove(pill.senderID)
    view_pills_received.remove(pill.receiverID)
    view_last_15_pills.remove(pill.guildID)
    data = astuple(pill)
    try:
        await db.execute("INSERT INTO pills VALUES(?, ?, ?, ?, ?, ?, ?, ?)", data)
    except IntegrityError as e:
        _log.error(f"{e.__class__.__name__} {e.args}")
        raise PillAlreadyExists
