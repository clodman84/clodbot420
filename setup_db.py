import aiosqlite
import asyncio
from clodbot.database import Pill

# doing this because discord IDs are bigger than the maximum size of sqlite integers
_MAX_SQLITE_INT = 2**63 - 1
aiosqlite.register_adapter(int, lambda x: hex(x) if x > _MAX_SQLITE_INT else x)
aiosqlite.register_converter("integer", lambda b: int(b, 16 if b[:2] == b"0x" else 10))


async def makePillsTable():
    db: aiosqlite.Connection = await aiosqlite.connect("data.db")
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
            guildID INTEGER,
            UNIQUE(pill, guildID)
        );
    """
    )
    await cursor.close()
    await db.close()
    print("Pills table was created!")


async def setupFTS4pills():
    db: aiosqlite.Connection = await aiosqlite.connect("data.db")
    await db.executescript(
        """ DROP table IF EXISTS pills_fts;
            CREATE VIRTUAL TABLE IF NOT EXISTS pills_fts USING fts5(
                pill,
                guildID UNINDEXED,
                content='pills',
                tokenize='trigram'
            );
        """
    )
    print("fts table for pills has been made!")
    await db.executescript(
        """
        DROP TRIGGER IF EXISTS pills_ai;
        DROP TRIGGER IF EXISTS pills_ad;
        DROP TRIGGER IF EXISTS pills_au;
        CREATE TRIGGER pills_ai AFTER INSERT ON pills BEGIN
            INSERT INTO pills_fts(rowid, pill, guildID) VALUES(new.rowid, new.pill, new.guildID);
        END;
        CREATE TRIGGER pills_ad AFTER DELETE ON pills BEGIN
            INSERT INTO pills_fts(pills_fts, rowid, pill, guildID) VALUES('delete', old.rowid, old.pill, old.guildID);
        END;
        CREATE TRIGGER pills_au AFTER UPDATE ON pills BEGIN
            INSERT INTO pills_fts(pills_fts, rowid, pill, guildID) VALUES('delete', old.rowid, old.pill, old.guildID);
            INSERT INTO pills_fts(rowid, pill, guildID) VALUES(new.rowid, new.pill, new.guildID);
        END;
        INSERT INTO pills_fts SELECT pill, guildID FROM pills;
    """
    )
    print("update triggers for pills have been set up")
    await db.close()


def makeRandomPills(n):
    """
    Just for testing purposes
    """
    import string
    import random

    for _ in range(n):
        timestamp = random.randint(10**10, 10**11)
        pill = "".join(random.choices(string.ascii_letters, k=random.randint(3, 40)))
        basedMessage = "".join(
            random.choices(string.ascii_letters, k=random.randint(3, 120))
        )
        senderID, receiverID, channelID, messageID, guildID = (
            random.randint(10**18, 10**19) for _ in range(5)
        )
        yield Pill(
            timestamp,
            pill,
            basedMessage,
            senderID,
            receiverID,
            channelID,
            messageID,
            guildID,
        )


async def viewAllPills():
    db: aiosqlite.Connection = await aiosqlite.connect("data.db")
    cursor = await db.cursor()
    await cursor.execute("SELECT * FROM pills;")
    pills = await cursor.fetchall()
    await db.close()
    return pills


async def main():
    await makePillsTable()
    await setupFTS4pills()
    pills = await viewAllPills()
    for i, pill in enumerate(pills):
        print(i, pill)


if __name__ == "__main__":
    asyncio.run(main())
