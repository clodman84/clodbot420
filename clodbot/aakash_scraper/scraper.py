import asyncio

import aakash
from bs4 import BeautifulSoup

from clodbot import http

ROOT_URL = "http://aakashleap.com:3131/API/GetIndividualResultByFrmRoll?PageSize=1&id={}&fromRoll={}"


async def get_student_reports(testID, roll_numbers):
    data = await asyncio.gather(
        *[http.get(ROOT_URL.format(testID, roll)) for roll in roll_numbers]
    )
    return data


def extract_test_info(data):
    soup = BeautifulSoup(data.text, "lxml")
    performanceTable = soup.find("div", {"class", "score-analysis"})
    if not performanceTable:
        print(data.url, "discarded")
        return None
    rows = performanceTable.find_all("tr")
    summary = {
        "AIR": soup.u.text.split("\n")[1].strip(),
        "Physics": rows[1]("td")[2].text.strip(),
        "Chemistry": rows[2]("td")[2].text.strip(),
        "Maths": rows[3]("td")[2].text.strip(),
    }
    return summary


def extract_student_info(data):
    soup = BeautifulSoup(data.text, "lxml")

    details = [i for i in soup.find_all("td", {"class": "second-td-st"})]
    if len(details) == 0:
        print(data.url, "discarded")
        return None

    summary = (
        details[0].text.strip(),
        details[1].text.strip(),
        details[3].text.strip(),
    )
    return summary
