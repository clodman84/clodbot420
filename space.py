from utils import get
from httpx import AsyncClient
from bs4 import BeautifulSoup
import asyncio
import config


async def apod():
    """For space related operations that have no parameters"""
    url = "https://api.nasa.gov/planetary/apod"
    querystring = {"api_key": config.NASA_KEY, "thumbs": True}
    response = await get(url=url, params=querystring)
    if response.json()["media_type"] == "video":
        img_url = response.json()["thumbnail_url"]
        description = (
            response.json()["explanation"] + "\n Video Link : " + response.json()["url"]
        )
    else:
        try:
            img_url = response.json()["hdurl"]
        except KeyError:
            img_url = response.json()["url"]
        description = response.json()["explanation"]
    return description, img_url, response.json()["title"]


async def people():
    url = "http://api.open-notify.org/astros.json"
    response = await get(url=url)
    A = response.json()
    people_in_space = A["people"]
    text = ""
    for i in people_in_space:
        text += str(i) + "\n"
    number = A["number"]
    return "There are currently " + str(number) + " people in space\n" + text


async def iss():
    url = "http://api.open-notify.org/iss-now.json"
    response = await get(url=url)
    pos = response.json()["iss_position"]
    return pos


def EPIC():
    """A function for EPIC images from NASA. Should this be a class?"""

    url = "https://epic.gsfc.nasa.gov/api/images.php"
    querystring = {"api_key": "YdNyGnuk3Mr5El8cBLCSSOrAJ7ymjtjuRE3OfBUJ"}
    request = get(url=url, params=querystring)
    return request


async def isro_BIMG(date, year, time):
    """Generates URLs and performs a GET request on them and gets the latest ISRO satellite image, plans to open this
    to every type of image"""
    count = 0
    urls = []
    if int(time[2:]) >= 30:
        time = str(int(time[0:2]) + 1) + "00"
        if len(time) == 3:
            time = "0" + time
    else:
        time = time[0:2] + "30"
    while int(time) > 0 and count <= 5:
        count += 1
        if time[2:] == "00":
            time = str(int(time[:-2]) - 1) + "30"
        else:
            time = time[:-2] + "00"
        if len(time) == 3:
            time = "0" + time
        url = f"https://mosdac.gov.in/look/3D_IMG/preview/{year}/{date}/3DIMG_{date}{year}_{time}_L1C_ASIA_MER_BIMG.jpg"
        urls.append(url)
        # trying 29 and 59
        if time[2:] == "00":
            NEWtime = str(int(time[:-2]) - 1) + "59"
        else:
            NEWtime = time[:-2] + "29"
        if len(NEWtime) == 3:
            NEWtime = "0" + NEWtime
            url = (
                f"https://mosdac.gov.in/look/3D_IMG/gallery/{year}/{date}/3DIMG_{date}{year}_{NEWtime}_"
                f"L1C_ASIA_MER_BIMG.jpg "
            )
            urls.append(url)
    async with AsyncClient(timeout=None) as client:
        tasks = (client.get(url) for url in urls)
        reqs = await asyncio.gather(*tasks)
    statusCodes = [req.status_code for req in reqs]

    for i in range(len(statusCodes)):
        if statusCodes[i] == 200:
            return 200, urls[i]
    else:
        return 404, "Alas Moment"


async def feed(sat):
    """Extracts data from the rich site summary of the mosdac website"""

    response = []
    request = await get(f"https://mosdac.gov.in/{sat}.xml")
    soup = BeautifulSoup(request, "lxml")
    for item in soup.find_all("item"):
        response.append(
            [item.title.text, item.guid.text, item.description.text, item.pubdate.text]
        )
    return response


def EONET():
    return


def MARS():
    return


if __name__ == "__main__":

    import cProfile
    import pstats

    pr = cProfile.Profile()
    pr.enable()
    asyncio.run(feed("3drimager"))
    pr.disable()
    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.print_stats()
