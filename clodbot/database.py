import datetime
import logging
import queue

import aiosqlite

_log = logging.getLogger("clodbot.core.db")

# doing this because discord IDs are bigger than the maximum size of sqlite integers
_MAX_SQLITE_INT = 2**63 - 1
aiosqlite.register_adapter(int, lambda x: hex(x) if x > _MAX_SQLITE_INT else x)
aiosqlite.register_converter("integer", lambda b: int(b, 16 if b[:2] == b"0x" else 10))


class ConnectionPool:
    _q = queue.SimpleQueue()

    def __init__(self, row_factory):
        self.connection = None
        self.row_factory = row_factory

    async def __aenter__(self) -> aiosqlite.Connection:
        try:
            self.connection = self._q.get_nowait()
        except queue.Empty:
            self.connection = await aiosqlite.connect("data.db")
            await self.connection.execute("pragma journal_mode=wal;")
        self.connection.row_factory = self.row_factory
        return self.connection

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._q.put(self.connection)

    @classmethod
    async def close(cls):
        while not cls._q.empty():
            await cls._q.get_nowait().close()
        _log.info("ConnectionPool Closed")


async def insert_timers(times, db: aiosqlite.Connection) -> None:
    """
    Inserts timers
    """
    try:
        await db.executemany("INSERT INTO timers VALUES(?, ?, ?)", times)
    except aiosqlite.Error as e:
        _log.exception(e)
