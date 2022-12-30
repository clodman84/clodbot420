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


async def result_factory(row: tuple):  # no puns here
    student = await get_student_from_roll(row[0])
    test = await get_test_from_id(row[1])
    return Result(student, test, *row[2:])


@dataclass(slots=True, frozen=True)
class Student:
    roll_no: str
    name: str
    psid: str  # these are strings because aakash ids have random leading Zeros
    batch: str


@dataclass(slots=True, frozen=True)
class Test:
    test_id: str
    name: str
    date: str
    national_attendance: int
    centre_attendance: int


@Cache(maxsize=128)
async def get_student_from_roll(roll_no: str) -> Student:
    async with database.ConnectionPool(kota) as db:
        res = await db.execute("SELECT * FROM students WHERE roll_no = ?", (roll_no,))
        # noinspection PyTypeChecker
        return await res.fetchone()


@Cache(maxsize=50)
async def get_test_from_id(test_id: str) -> Test:
    async with database.ConnectionPool(nta) as db:
        res = await db.execute("SELECT * FROM tests WHERE test_id = ?", (test_id,))
        # noinspection PyTypeChecker
        return await res.fetchone()


@dataclass(slots=True)
class Result:
    student: Student
    test: Test
    AIR: int  # for sorting
    physics: int
    chemistry: int
    maths: int

    @property
    def total(self):
        return self.physics + self.chemistry + self.maths


@Cache(maxsize=128)
async def get_student_results(roll_no: str):
    results = []
    async with database.ConnectionPool(None) as db:
        async with db.execute(
            "SELECT roll_no, results.test_id, air, physics, chemistry, maths FROM results "
            "INNER JOIN tests on results.test_id=tests.test_id WHERE roll_no = ?"
            "ORDER BY tests.date",
            (roll_no,),
        ) as cursor:
            async for row in cursor:
                result = await result_factory(row)
                results.append(result)
    return results


@Cache(maxsize=128)
async def get_student_ranks(roll_no):
    async with database.ConnectionPool(lambda _, x: x) as db:
        res = await db.execute(
            """SELECT * FROM
                (SELECT roll_no,
                RANK() OVER( PARTITION by test_id ORDER by physics desc),
                RANK() OVER( PARTITION by test_id ORDER by chemistry desc),
                RANK() OVER( PARTITION by test_id ORDER by maths desc)
                from results)
                WHERE roll_no = ?
            """,
            (roll_no,),
        )
        return await res.fetchall()


@Cache
async def view_results(test_id: str):
    results = []
    async with database.ConnectionPool(None) as db:
        async with db.execute(
            "SELECT * FROM results WHERE test_id = ? ORDER BY air", (test_id,)
        ) as cursor:
            async for row in cursor:
                result = await result_factory(row)
                results.append(result)
    return results


@Cache
async def view_last_15_tests():
    async with database.ConnectionPool(lambda _, y: y) as db:
        res = await db.execute(
            "SELECT name, test_id FROM tests ORDER BY date DESC LIMIT 15"
        )
        tests = await res.fetchall()
        return tests


@Cache
async def view_15_students_sorted_alpha():
    async with database.ConnectionPool(lambda _, y: y) as db:
        res = await db.execute(
            "SELECT name, roll_no FROM students ORDER BY name LIMIT 15"
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


@Cache(maxsize=32, ttl=120)
async def students_fts(text: str):
    async with database.ConnectionPool(lambda _, y: y) as db:
        res = await db.execute(
            "SELECT name, roll_no, rank FROM students_fts WHERE "
            "name MATCH ? ORDER BY RANK LIMIT 15",
            (text,),
        )
        matched_tests = await res.fetchall()
        return matched_tests


async def insert_test(test: dict, db):
    view_last_15_tests.clear()
    get_student_results.clear()
    get_student_ranks.clear()
    view_results.remove(
        test["test_id"]
    )  # tests are always inserted with results, so just remove them here.
    get_test_from_id.remove(test["test_id"])
    try:
        await db.execute(
            """INSERT INTO tests (test_id, name, date, national_attendance, centre_attendance)
                VALUES (:test_id, :name, :date, :national_attendance, :centre_attendance)
                ON CONFLICT(test_id) DO UPDATE SET national_attendance = :national_attendance,
                centre_attendance = :centre_attendance
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
            """INSERT INTO results (roll_no, test_id, air, physics, chemistry, maths)
                VALUES (:roll_no, :test_id, :air, :physics, :chemistry, :maths)
                ON CONFLICT(roll_no, test_id) DO UPDATE SET air = :air
            """,
            results,
        )
    except Error as e:
        _log.error(f"{e.__class__.__name__} {e.args}")
