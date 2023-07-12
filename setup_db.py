import asyncio

import aiosqlite

from clodbot.pills import Pill

# doing this because discord IDs are bigger than the maximum size of sqlite integers
_MAX_SQLITE_INT = 2**63 - 1
aiosqlite.register_adapter(int, lambda x: hex(x) if x > _MAX_SQLITE_INT else x)
aiosqlite.register_converter("integer", lambda b: int(b, 16 if b[:2] == b"0x" else 10))


async def make_tests_table():
    db: aiosqlite.Connection = await aiosqlite.connect("data/data.db")
    cursor: aiosqlite.Cursor = await db.cursor()
    await cursor.execute(
        """CREATE TABLE IF NOT EXISTS tests(
            test_id TEXT PRIMARY KEY,
            name TEXT,
            date DATE,
            national_attendance INTEGER,
            centre_attendance INTEGER
        );
    """
    )
    await cursor.close()
    await db.close()
    print("Tests table was created!")


async def make_results_table():
    db: aiosqlite.Connection = await aiosqlite.connect("data/data.db")
    cursor: aiosqlite.Cursor = await db.cursor()
    await cursor.execute(
        """CREATE TABLE IF NOT EXISTS results(
            roll_no TEXT,
            test_id TEXT,
            air INTEGER,
            physics INTEGER,
            chemistry INTEGER,
            maths INTEGER,
            CONSTRAINT p_key PRIMARY KEY (test_id, roll_no)
            CONSTRAINT f_test_key FOREIGN KEY (test_id) REFERENCES tests(test_id)
            CONSTRAINT f_roll_key FOREIGN KEY (roll_no) REFERENCES students(roll_no)
        );
    """
    )
    await cursor.close()
    await db.close()
    print("Results table was created!")


async def make_students_table():
    db: aiosqlite.Connection = await aiosqlite.connect("data/data.db")
    cursor: aiosqlite.Cursor = await db.cursor()
    await cursor.execute(
        """CREATE TABLE IF NOT EXISTS students(
            roll_no TEXT PRIMARY KEY,
            name TEXT,
            psid TEXT,
            batch TEXT
        );
    """
    )
    await cursor.close()
    await db.close()
    print("Student table was created!")


async def make_pills_table():
    db: aiosqlite.Connection = await aiosqlite.connect("data/data.db")
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


async def make_timer_table():
    db: aiosqlite.Connection = await aiosqlite.connect("data/data.db")
    cursor: aiosqlite.Cursor = await db.cursor()
    await cursor.execute(
        """CREATE TABLE IF NOT EXISTS timers(
            timestamp REAL,
            timer_name TEXT,
            time REAL
        );
    """
    )
    await cursor.close()
    await db.close()
    print("Timer table was created!")


async def make_files_table():
    db: aiosqlite.Connection = await aiosqlite.connect("data/data.db")
    cursor: aiosqlite.Cursor = await db.cursor()
    await cursor.execute(
        """CREATE TABLE IF NOT EXISTS files(
            created_on TIMESTAMP,
            userID INTEGER,
            filename TEXT,
            content BLOB,
            last_updated TIMESTAMP,
            UNIQUE(userID, filename)
        );
    """
    )
    await cursor.close()
    await db.close()
    print("files table was created!")


async def setup_fts_for_pills():
    db: aiosqlite.Connection = await aiosqlite.connect("data/data.db")
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


async def setup_fts_for_tests():
    db: aiosqlite.Connection = await aiosqlite.connect("data/data.db")
    await db.executescript(
        """ DROP table IF EXISTS tests_fts;
            CREATE VIRTUAL TABLE IF NOT EXISTS tests_fts USING fts5(
                test_id UNINDEXED,
                name,
                content='tests',
                tokenize='trigram'
            );
        """
    )
    print("fts table for tests has been made!")
    # there are no update and delete triggers because that will never happen
    await db.executescript(
        """
        DROP TRIGGER IF EXISTS tests_ai;
        CREATE TRIGGER tests_ai AFTER INSERT ON tests BEGIN
            INSERT INTO tests_fts(test_id, name) VALUES(new.test_id, new.name);
        END;
        INSERT INTO tests_fts SELECT test_id, name FROM tests;
    """
    )
    print("update triggers for tests have been set up")
    await db.close()


async def setup_fts_for_students():
    db: aiosqlite.Connection = await aiosqlite.connect("data/data.db")
    await db.executescript(
        """ DROP table IF EXISTS students_fts;
            CREATE VIRTUAL TABLE IF NOT EXISTS students_fts USING fts5(
                roll_no UNINDEXED,
                name,
                content='students',
                tokenize='trigram'
            );
        """
    )
    print("fts table for students has been made!")
    # there are no update and delete triggers because that will never happen
    await db.executescript(
        """
        DROP TRIGGER IF EXISTS students_ai;
        CREATE TRIGGER students_ai AFTER INSERT ON students BEGIN
            INSERT INTO students_fts(roll_no, name) VALUES(new.roll_no, new.name);
        END;
        INSERT INTO students_fts SELECT roll_no, name FROM students;
    """
    )
    print("update triggers for students have been set up")
    await db.close()


def make_random_pills(n):
    """
    Just for testing purposes
    """
    import random
    import string

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


async def setup_fts_for_files():
    db: aiosqlite.Connection = await aiosqlite.connect("data/data.db")
    await db.executescript(
        """ DROP table IF EXISTS files_fts;
            CREATE VIRTUAL TABLE IF NOT EXISTS files_fts USING fts5(
                filename,
                userID UNINDEXED,
                content='files',
                tokenize='trigram'
            );
        """
    )
    print("fts table for files has been made!")
    await db.executescript(
        """
        DROP TRIGGER IF EXISTS files_ai;
        DROP TRIGGER IF EXISTS files_ad;
        DROP TRIGGER IF EXISTS files_au;
        CREATE TRIGGER files_ai AFTER INSERT ON files BEGIN
            INSERT INTO files_fts(rowid, filename, userID) VALUES(new.rowid, new.filename, new.userID);
        END;
        CREATE TRIGGER files_ad AFTER DELETE ON files BEGIN
            INSERT INTO files_fts(files_fts, rowid, filename, userID)
            VALUES('delete', old.rowid, old.filename, old.userID);
        END;
        CREATE TRIGGER files_au AFTER UPDATE ON files BEGIN
            INSERT INTO files_fts(files_fts, rowid, filename, userID)
            VALUES('delete', old.rowid, old.filename, old.userID);
            INSERT INTO files_fts(rowid, filename, userID) VALUES(new.rowid, new.filename, new.userID);
        END;
        INSERT INTO files_fts SELECT filename, userID FROM files;
    """
    )
    print("update triggers for files have been set up")
    await db.close()


async def view_all_pills():
    db: aiosqlite.Connection = await aiosqlite.connect("data/data.db")
    cursor = await db.cursor()
    await cursor.execute("SELECT * FROM pills;")
    pills = await cursor.fetchall()
    await db.close()
    return pills


async def main():
    # don't change this order
    await make_pills_table()
    await make_timer_table()
    await make_students_table()
    await make_tests_table()
    await make_results_table()
    await make_files_table()
    await setup_fts_for_students()
    await setup_fts_for_tests()
    await setup_fts_for_pills()
    await setup_fts_for_files()


if __name__ == "__main__":
    asyncio.run(main())
