import asyncio
import csv
import io

from clodbot.utils import Cache, mean_stddev

from . import aakash_db


def compounded_growth_rate(data: tuple):
    rate = (data[-1] / data[0]) ** (1 / len(data))
    return (rate - 1) * 100


def make_subject_wise_rank_list(ranklist: tuple):
    ranks = {
        "physics": tuple(rank[1] for rank in ranklist),
        "chemistry": tuple(rank[2] for rank in ranklist),
        "maths": tuple(rank[3] for rank in ranklist),
    }
    return ranks


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


async def make_student_report(roll_no: str):
    results = await aakash_db.get_student_results(roll_no)
    ranks = await aakash_db.get_student_ranks(roll_no)
    ranks = make_subject_wise_rank_list(ranks)

    metrics = {"physics", "chemistry", "maths", "total"}
    report = {}
    for metric in metrics:
        values = tuple(result.__getattribute__(metric) for result in results)
        growth_rate = compounded_growth_rate(values)
        mean, dev = mean_stddev(values)
        average_score = f"{mean:.2f} \N{PLUS-MINUS SIGN} {dev:.2f}"
        if metric == "total":
            avg_rank = (
                sum(
                    1 - (result.AIR / result.test.national_attendance)
                    for result in results
                )
                / len(results)
                * 100
            )
        else:
            avg_rank = sum(ranks[metric]) / len(ranks[metric])

        report[metric] = {
            "growth_rate": growth_rate,
            "average_score": average_score,
            "average_rank": avg_rank,
        }
    return report
