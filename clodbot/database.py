import aiosqlite
import logging
import asyncio
from dataclasses import dataclass, astuple
from typing import List
from clodbot.utils import Cache

_log = logging.getLogger("clodbot.core.db")


# doing this because discord IDs are bigger than the maximum size of sqlite integers
_MAX_SQLITE_INT = 2**63 - 1
aiosqlite.register_adapter(int, lambda x: hex(x) if x > _MAX_SQLITE_INT else x)
aiosqlite.register_converter("integer", lambda b: int(b, 16 if b[:2] == b"0x" else 10))


@dataclass(slots=True)
class Pill:
    timestamp: int
    pill: str
    basedMessage: str
    senderID: int
    receiverID: int
    channelID: int
    messageID: int
    guildID: int


def pharmacy(_, row: tuple):
    """
    A row factory for pills.
    """
    return Pill(*row)


@Cache
async def viewPillsReceived(userID: int):
    _log.debug("SELECT pills received by %s", userID)
    db: aiosqlite.Connection = await aiosqlite.connect("../data.db")
    db.row_factory = pharmacy
    cursor = await db.cursor()
    await cursor.execute("SELECT * FROM pills WHERE receiverID = ?", (userID,))
    pills = await cursor.fetchall()
    await db.close()
    return pills


@Cache
async def viewPillsGiven(userID: int):
    _log.debug("SELECT pills given by %s", userID)
    db: aiosqlite.Connection = await aiosqlite.connect("../data.db")
    db.row_factory = pharmacy
    cursor = await db.cursor()
    await cursor.execute("SELECT * FROM pills WHERE senderID = ?", (userID,))
    pills = await cursor.fetchall()
    await db.close()
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
    data = astuple(pill)
    await db.execute("INSERT INTO pills VALUES(?, ?, ?, ?, ?, ?, ?, ?)", data)
    await db.commit()


async def makePillsTable():
    db: aiosqlite.Connection = await aiosqlite.connect("../data.db")
    cursor: aiosqlite.Cursor = await db.cursor()
    await cursor.execute(
        """CREATE TABLE IF NOT EXISTS pills(
            timestamp INTEGER,
            pill TEXT,
            basedMessage TEXT,
            senderID INTEGER,
            receiverID INTEGER,
            channelID INTEGER,
            messageID INTEGER,
            guildID INTEGER
        );
    """
    )
    await cursor.close()
    await db.close()
    print("Pills table was created!")


def makeRandomPills(n):
    """
    Just for testing purposes
    """
    import string
    import random

    pills: List[Pill] = []
    for _ in range(n):
        timestamp = random.randint(10**10, 10**11)
        pill = "".join(random.choices(string.ascii_letters, k=random.randint(3, 40)))
        basedMessage = "".join(
            random.choices(string.ascii_letters, k=random.randint(3, 120))
        )
        senderID, receiverID, channelID, messageID, guildID = (
            random.randint(10**18, 10**19) for _ in range(5)
        )
        pills.append(
            Pill(
                timestamp,
                pill,
                basedMessage,
                senderID,
                receiverID,
                channelID,
                messageID,
                guildID,
            )
        )

    return pills


async def viewAllPills():
    db: aiosqlite.Connection = await aiosqlite.connect("../data.db")
    db.row_factory = pharmacy
    cursor = await db.cursor()
    await cursor.execute("SELECT * FROM pills")
    pills = await cursor.fetchall()
    await db.close()
    return pills


async def main():
    await makePillsTable()
    pills = await viewAllPills()
    for i, pill in enumerate(pills):
        print(i, pill)


if __name__ == "__main__":
    asyncio.run(main())
