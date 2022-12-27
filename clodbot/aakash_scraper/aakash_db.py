import logging
from dataclasses import dataclass
from typing import Iterable

from aiosqlite import Error

from clodbot import database
from clodbot.utils import Cache

_log = logging.getLogger("clodbot.core.aakash_warehouse")


def kota(_, row: tuple):
    """
    A (row) factory for students.
    """
    return Student(*row)


def nta(_, row: tuple):
    """
    A (row) factory for tests
    """
    return Test(*row)


@Cache(maxsize=128)
async def get_student_from_roll(roll_no: str):
    async with database.ConnectionPool(kota) as db:
        res = await db.execute("SELECT * FROM students WHERE roll_no = ?", (roll_no,))
        return await res.fetchone()


@Cache(maxsize=50)
async def get_test_from_id(test_id: str):
    async with database.ConnectionPool(nta) as db:
        res = await db.execute("SELECT * FROM tests WHERE test_id = ?", (test_id,))
        return await res.fetchone()


@dataclass(slots=True, frozen=True)
class Student:
    roll_no: str
    name: str
    psid: str  # these are strings because aakash ids have random leading Zeros
    batch: str

    async def fetch(self):
        return self


@dataclass(slots=True, frozen=True)
class PartialStudent:
    """These are made when the result is fetched from the database"""

    roll_no: str

    async def fetch(self) -> Student:
        return await get_student_from_roll(self.roll_no)


@dataclass(slots=True, frozen=True)
class Test:
    test_id: str
    name: str
    date: str
    national_attendance: int
    centre_attendance: int

    async def fetch(self):
        return self


@dataclass(slots=True, frozen=True)
class PartialTest:
    test_id: str

    async def fetch(self) -> Test:
        return await get_test_from_id(self.test_id)


@dataclass(slots=True, order=True)
class Result:
    student: Student | PartialStudent
    test: Test | PartialTest
    AIR: int  # for sorting
    physics: int
    chemistry: int
    maths: int

    async def resolve_student(self):
        self.student = await self.student.fetch()

    async def resolve_test(self):
        self.test = await self.test.fetch()

    async def resolve(self):
        """A method to convert student and test attributes to their fuller forms with all their data."""
        self.student = await self.student.fetch()
        self.test = await self.test.fetch()


def result_factory(_, row: tuple):  # no puns here
    # I could have done this with convertors as well, but don't feel like it.
    student = PartialStudent(row[0])
    test = PartialTest(row[1])
    return Result(student, test, *row[2:])


@Cache
async def view_results(test_id: str):
    async with database.ConnectionPool(result_factory) as db:
        res = await db.execute(
            "SELECT * FROM results WHERE test_id = ? ORDER BY air", (test_id,)
        )
        return await res.fetchall()


@Cache
async def view_last_15_tests():
    async with database.ConnectionPool(lambda _, y: y) as db:
        res = await db.execute(
            "SELECT name, test_id FROM tests ORDER BY date DESC LIMIT 15"
        )
        tests = await res.fetchall()
        return tests


@Cache(maxsize=32, ttl=120)
async def tests_fts(text: str):
    async with database.ConnectionPool(lambda _, y: y) as db:
        res = await db.execute(
            "SELECT name, test_id, rank FROM tests_fts WHERE "
            "name MATCH ? ORDER BY RANK LIMIT 15",
            (text,),
        )
        matched_tests = await res.fetchall()
        return matched_tests


async def insert_test(test: dict, db):
    view_last_15_tests.clear()
    try:
        await db.execute(
            """INSERT OR IGNORE INTO tests (test_id, name, date, national_attendance, centre_attendance)
                VALUES (:test_id, :name, :date, :national_attendance, :centre_attendance)
            """,
            test,
        )
    except Error as e:
        _log.error(f"{e.__class__.__name__} {e.args}")


async def insert_students(students: Iterable[dict], db):
    try:
        await db.executemany(
            """INSERT OR IGNORE INTO students (roll_no, name, psid, batch)
                VALUES (:roll_no, :name, :psid, :batch)
            """,
            students,
        )
    except Error as e:
        _log.error(f"{e.__class__.__name__} {e.args}")


async def insert_results(results: Iterable[dict], db):
    try:
        await db.executemany(
            """INSERT OR IGNORE INTO results (roll_no, test_id, air, physics, chemistry, maths)
                VALUES (:roll_no, :test_id, :air, :physics, :chemistry, :maths)
            """,
            results,
        )
    except Error as e:
        _log.error(f"{e.__class__.__name__} {e.args}")
