import asyncio
import concurrent.futures
import functools
import logging
import re
from datetime import datetime

from bs4 import BeautifulSoup

from clodbot import http

_log = logging.getLogger("clodbot.core.aakash_scraper")

ROOT_URL = "http://aakashleap.com:3131/API/GetIndividualResultByFrmRoll?PageSize=1&id={}&fromRoll={}"
roll_types = ["0642220600", "0642121200", "0642220500", "0642151200"]


async def get(url):
    session = http.SingletonSession()
    async with session.get(url) as response:
        return await response.text()


async def get_student_reports(testID, roll_numbers):
    data = await asyncio.gather(
        *[get(ROOT_URL.format(testID, roll)) for roll in roll_numbers]
    )
    return data


def extract_data(data, test_id):
    soup = BeautifulSoup(data, "lxml")

    if soup.h3.text.strip() == "Sorry Request can not be completed":
        return None

    details = [i for i in soup.find_all("td", {"class": "second-td-st"})]
    student = {
        "name": details[0].text.strip(),
        "psid": details[1].text.strip(),
        "roll_no": details[3].text.strip(),
        "batch": details[-1].text.strip(),
    }

    performanceTable = soup.find("div", {"class", "score-analysis"})
    rows = performanceTable.find_all("tr")

    result = {
        "roll_no": student["roll_no"],
        "test_id": test_id,
        "air": soup.u.text.split("\n")[1].strip(),
        "physics": rows[1]("td")[2].text.strip(),
        "chemistry": rows[2]("td")[2].text.strip(),
        "maths": rows[3]("td")[2].text.strip(),
    }

    return student, result


def extract_test(data) -> dict | None:
    soup = BeautifulSoup(data, "lxml")

    if soup.h3.text.strip() == "Sorry Request can not be completed":
        return None

    name_regex = re.compile(r"result of '(.*?)'")
    date_regex = re.compile(r"(\d{0,2}/\d{0,2}/\d{4})")
    attendance_regex = re.compile(r"of\s*(\d*)")

    string = soup.p.next_sibling.text
    name_match = name_regex.search(string)
    date_match = date_regex.search(string)
    attendance_match = attendance_regex.findall(string)

    date = datetime.strptime(date_match.group(1), "%d/%m/%Y")

    test = {
        "name": name_match.group(1),
        "centre_attendance": attendance_match[1],
        "date": date,
        "national_attendance": attendance_match[2],
    }
    return test


async def extract_all(data_set, extractor):
    loop = asyncio.get_running_loop()

    def func():
        # a generator would have been exhausted.
        return tuple(filter(None, map(extractor, data_set)))

    with concurrent.futures.ThreadPoolExecutor() as pool:
        _log.debug("Running with ThreadPoolExecutor")
        return await loop.run_in_executor(pool, func)


async def scrape(test_id):
    responses = []
    _log.debug("Getting data from Aakash...")
    for roll_type in roll_types:
        roll_numbers = (f"{roll_type}{roll:02}" for roll in range(100))
        response = await get_student_reports(test_id, roll_numbers)
        responses.extend(response)

    _log.debug("Extracting information...")
    extractor = functools.partial(extract_data, test_id=test_id)
    parsed_responses = await extract_all(responses, extractor)

    # to extract test data only once next() will give use the first valid output from the filter
    # if there are no results at all, this will raise a StopIteration
    try:
        test = next(filter(None, map(extract_test, responses)))
        test["test_id"] = test_id
    except StopIteration:
        _log.error("No valid responses received from Aakash!")
        return

    _log.debug("Done!")
    students = (value[0] for value in parsed_responses)
    results = (value[1] for value in parsed_responses)
    return students, results, test
