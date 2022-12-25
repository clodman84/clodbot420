import datetime
import logging
from dataclasses import dataclass

from aiosqlite import IntegrityError

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
    date: datetime.date
    national_attendance: int
    centre_attendance: int


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

    async def resolve(self):
        """A method to convert student and test attributes to their fuller forms with all their data."""
        self.student = await self.student.fetch()
        self.test = await self.test.fetch()


def result_factory(_, row: tuple):  # no puns here
    # I could have done this with convertors as well, but don't feel like it.
    student = PartialStudent(row[0])
    test = PartialTest(row[1])
    return Result(student, test, *row[2:])


async def view_result(test_id: str):
    async with database.ConnectionPool(result_factory) as db:
        res = await db.execute("SELECT * FROM results WHERE test_id = ?", (test_id,))
        return await res.fetchall()


async def insert_test(test: dict, db):
    try:
        await db.execute(
            """INSERT INTO tests (test_id, name, date, national_attendance, centre_attendance)
                SELECT :test_id, :name, :date, :national_attendance, :centre_attendance
                WHERE NOT EXISTS
                (
                SELECT test_id
                FROM tests
                WHERE test_id = :test_id
            )
            """,
            test,
        )
    except IntegrityError as e:
        _log.error(f"{e.__class__.__name__} {e.args}")


async def insert_students(students: tuple[dict, ...], db):
    try:
        await db.executemany(
            """INSERT INTO students (roll_no, name, psid)
                SELECT :roll_no, :name, :psid, :batch
                WHERE NOT EXISTS
                (
                SELECT roll_no
                FROM students
                WHERE roll_no = :roll_no
            )
            """,
            students,
        )
    except IntegrityError as e:
        _log.error(f"{e.__class__.__name__} {e.args}")


async def insert_results(results: tuple[dict, ...], db):
    try:
        await db.executemany(
            """INSERT INTO students
                VALUES (:roll_no, :test_id, :air, :physics, :chemistry, :maths)
            """,
            results,
        )
    except IntegrityError as e:
        _log.error(f"{e.__class__.__name__} {e.args}")
