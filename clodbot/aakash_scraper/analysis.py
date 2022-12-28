import asyncio
import csv
import io

from clodbot.utils import Cache

from . import aakash_db


@Cache
async def make_csv(test):
    results = await aakash_db.view_results(test)

    def get_required_data_from_result(result: aakash_db.Result):
        return (
            result.AIR,
            result.student.name,
            result.physics,
            result.chemistry,
            result.maths,
            result.total,
        )

    def func():
        data = map(get_required_data_from_result, results)
        with io.StringIO() as file:
            writer = csv.writer(file)
            writer.writerow(["AIR", "Name", "PHY", "CHM", "MTH", "TOT"])
            writer.writerows(data)
            return file.getvalue()

    loop = asyncio.get_running_loop()
    val = await loop.run_in_executor(None, func)

    return val.encode()
