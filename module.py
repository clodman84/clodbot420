from country_bounding_boxes import (country_subunits_by_iso_code)
import requests
import random
import sqlite3 as sql
import utils
import asyncio
from errors import MissingDataError
from datetime import datetime
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import xml.etree.ElementTree as ET
from operator import itemgetter

mycon = sql.connect('data.db')
cursor = mycon.cursor()

"""Only for cosmetic purposes."""


def generator(list_name):  # Generates curse words and spicy phrases to make the bot feel alive

    """Returns a random phrase from a database of phrases, also ensures that the same phrase is not returned twice. This function is used frequently
    to make the bot's responses more human."""
    cursor.execute(f"select {list_name} from {list_name} where {list_name}_black = 'not used'")
    phrases = cursor.fetchall()
    if len(phrases) == 0:
        return "I am out of ammo chief"
    while True:
        cancer = phrases[random.randint(0, len(phrases) - 1)][0]

        cursor.execute(f'update {list_name} set {list_name}_black = "used" where {list_name} = "{cancer}"')
        mycon.commit()
        if list_name == 'sites':
            if cancer[0] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                cancer = cancer.split(')')[1] + ' (Banned in India) '

            return cancer
        else:
            return cancer


def ammo():  # tells how many of the above phrases are available for use
    """Shows how many of the phrases haven't been used yet"""
    count = []
    for i in ['phrases', 'sentences', 'minecraft', 'sites']:
        cursor.execute(f' select {i}_black from {i} where {i}_black = "not used"')
        data = len(cursor.fetchall())
        count.append(data)
    return (
        f"Porn Titles :- {count[0]}\nPink Guy Lyrics :- {count[1]}\nMinecraft Yellow Text :- {count[2]}\nPorn Sites :- {count[3]}")


def clear(a):  # clears the blacklist in case the bot runs out of phrases
    """Clears the blacklist of phrases and it allows phrases to be used again, just in case"""
    try:
        cursor.execute(f'update {a} set {a}_black = "not used"')
        return "A blacklist was cleared on " + str(datetime.utcnow())
    except:
        return "Something went wrong"


async def translate(txt, author):
    """Translates whatever text is passed through it into 5 different accents. Also strips the author names and returns only the name without the number"""

    outputs = [["Thee men talk too much i am did tire of translating thy words especially ", "Shakespeare_CUNT"],
               ["Tired of translating I am, talk too much you do ", 'Yoda_CUNT'],
               ["I am tired of translatin' you dudes. I just wanna smoke crack with ", "Valley_CUNT"],
               ['I im su tured ouff truonsleting yuou, zeet talkateev ', 'European_CUNT'],
               ["I be so tired o' translatin' ye, that talkative ", 'Pirates_of_the_CUNT']]
    links = ['shakespeare.json', 'pirate.json', 'yoda.json', 'valspeak.json']
    response = requests.get('https://api.funtranslations.com/translate/' + links[random.randint(0, len(links) - 1)],
                            params={"text": txt})
    if response.status_code == 200:
        output = response.json()['contents']['translated']
        auth = author.split('#')[0]
        code = 200
    else:
        A = outputs[random.randint(0, len(outputs) - 1)]
        output = A[0] + author.split('#')[0]
        auth = A[1]
        code = 69
    return output, auth, code


async def globe():
    """OPEN SKY API. Global airplane data"""
    url = 'https://opensky-network.org/api/states/all'
    response = requests.get(url=url)
    return response.json()['states']


async def bbox(bbox):
    """OPEN SKY API. Returns data within a specofic bounding box, not implemented yet"""

    url = 'https://opensky-network.org/api/states/all'
    b = bbox
    param = {'lomin': b[0], 'lamin': b[1], 'lomax': b[2], 'lamax': b[3]}
    response = requests.get(url=url, params=param)
    return response.json()


async def iso(iso):
    """OPEN SKY API. Uses the same bounding box parameters as before but instead the data comes from a database of bounding boxes of various areas by iso code"""

    url = 'https://opensky-network.org/api/states/all'
    box = [c.bbox for c in country_subunits_by_iso_code(iso)]  # the bounding box coords
    name = [c.name for c in country_subunits_by_iso_code(iso)]  # the name of the corresponding bounding box
    if box == [] or name == []:
        return None
    result = []
    for i in range(0, len(box)):
        b = box[i]
        n = name[i]
        param = {'lomin': b[0], 'lamin': b[1], 'lomax': b[2], 'lamax': b[3]}
        response = requests.get(url=url, params=param)
        try:
            data = response.json()['states']
            number = len(data)
        except TypeError:
            data = 'Wow such nothing'
            number = "<=3"
        result.append([n, number, data])
    return result
    # returns a multi dimensional list, which element containinng the name of the bounding box
    # specified, the number of aircraft and the data of each and every aircraft


async def ind(icao):
    """OPEN SKY API. Searches for a specific airplane with its icao code."""

    url = 'https://opensky-network.org/api/states/all'
    param = {"icao24": icao}
    response = requests.get(url=url, params=param)
    try:
        return response.json()['states'][0]
    except TypeError:
        return None


async def history(icao):
    """OPEN SKY API. Searches the history of an airplane with its icao code"""

    url = 'https://opensky-network.org/api/flights/aircraft'
    param = {'icao24': icao, 'begin': int(datetime.utcnow().timestamp()) - 604800,
             'end': int(datetime.utcnow().timestamp())}
    response = requests.get(url=url, params=param)
    return response.json()


async def airport(type, icao):
    """OPEN SKY API. 7 days of arrival or departure data for an aiport's icao code"""

    if type == 'arrival' and icao != 1:
        url = 'https://opensky-network.org/api/flights/arrival'
        param = {'airport': icao, 'begin': int(datetime.utcnow().timestamp()) - 604800,
                 'end': int(datetime.utcnow().timestamp())}
        response = requests.get(url=url, params=param)
        return response.json()
    if type == 'departure' and icao != 1:
        url = 'https://opensky-network.org/api/flights/departure'
        param = {'airport': icao, 'begin': int(datetime.utcnow().timestamp()) - 604800,
                 'end': int(datetime.utcnow().timestamp())}
        response = requests.get(url=url, params=param)
        return response.json()


async def joke():
    """JOKE API. Returns a Joke"""

    if random.randint(0, 10) <= 6:
        url = "https://jokeapi-v2.p.rapidapi.com/joke/Any"
        querystring = {"type": "single, twopart"}
        headers = {
            'x-rapidapi-key': "b2efcc243dmsh9563d2fd99f8086p161761jsn0796dda8a1e7",
            'x-rapidapi-host': "jokeapi-v2.p.rapidapi.com"
        }
        response = requests.request("GET", url, headers=headers, params=querystring)
        if response.json()['type'] == 'single' and response.json()['error'] == False:
            return response.json()['joke']
        elif response.json()['type'] == 'twopart' and response.json()['error'] == False:
            return f"{response.json()['setup']}\n||{response.json()['delivery']}||"
    else:
        url = 'https://official-joke-api.appspot.com/random_joke'
        response = requests.request('GET', url)
        return f"{response.json()['setup']}\n||{response.json()['punchline']}||"


async def Nasa(type):
    """For space related operations that have no paramteres"""

    # Astronomy photo of the day
    if type == 'APoD':
        url = "https://api.nasa.gov/planetary/apod"
        querystring = {'api_key': 'YdNyGnuk3Mr5El8cBLCSSOrAJ7ymjtjuRE3OfBUJ', 'thumbs': True}
        response = requests.request("GET", url, params=querystring)
        if response.json()['media_type'] == "video":
            img_url = response.json()['thumbnail_url']
            description = response.json()['explanation'] + '\n Video Link : ' + response.json()['url']
        else:
            try:
                img_url = response.json()['hdurl']
            except:
                img_url = response.json()['url']
            description = response.json()['explanation']
        return description, img_url, response.json()['title']
    # How many people in space right now
    if type == 'people':
        url = "http://api.open-notify.org/astros.json"
        response = requests.request("GET", url)
        A = response.json()
        people = A['people']
        text = ""
        for i in people:
            text += str(i) + '\n'
        number = A['number']
        return 'There are currently ' + str(number) + ' people in space\n' + text
    # iss location
    if type == 'iss':
        url = "http://api.open-notify.org/iss-now.json"
        response = requests.request("GET", url)
        pos = response.json()['iss_position']
        return pos


def EPIC():
    """A function for EPIC images from NASA. Should this be a class?"""

    url = 'https://epic.gsfc.nasa.gov/api/images.php'
    querystring = {'api_key': 'YdNyGnuk3Mr5El8cBLCSSOrAJ7ymjtjuRE3OfBUJ'}
    request = requests.get(url=url, params=querystring)
    return list(request)


def EONET():
    return


def MARS():
    return


async def isro_BIMG(date, year, time):
    """Generates URLs and performs a GET request on them and and sniffs out the latest ISRO satellite image, plans to open this to every type of image"""
    a = 0
    count = 0
    if int(time[2:]) >= 30:
        time = str(int(time[0:2]) + 1) + '00'
        if len(time) == 3:
            time = '0' + time
    else:
        time = time[0:2] + '30'
    while a != 200 and int(time) > 0 and count < 49:
        if time[2:] == '00':
            time = str(int(time[:-2]) - 1) + '30'
        else:
            time = time[:-2] + "00"
        if len(time) == 3:
            time = '0' + time
        url = f"https://mosdac.gov.in/look/3D_IMG/gallery/{year}/{date}/3DIMG_{date}{year}_{time}_L1C_ASIA_MER_BIMG.jpg"
        request = requests.get(url=url)
        count += 1
        a = request.status_code
        # trying 29 and 59
        if a == 404:
            if time[2:] == '00':
                NEWtime = str(int(time[:-2]) - 1) + '59'
            else:
                NEWtime = time[:-2] + "29"
            if len(NEWtime) == 3:
                NEWtime = '0' + NEWtime
            url = f"https://mosdac.gov.in/look/3D_IMG/gallery/{year}/{date}/3DIMG_{date}{year}_{NEWtime}_L1C_ASIA_MER_BIMG.jpg"
            request = requests.get(url=url)
            count += 1
            a = request.status_code
    return a, url


async def feed(sat):
    """Extracts data from the rich site summary of the mosdac website"""

    response = []
    request = requests.get(f'https://mosdac.gov.in/{sat}.xml')
    root = ET.fromstring(request.text)[0]
    for item in root.findall('item'):
        if item.find('guid').attrib['isPermaLink'] == 'true':
            response.append([item.find('title').text, item.find('link').text, item.find('description').text,
                             item.find('pubDate').text])
    return response


BASE_URL = 'http://ergast.com/api/f1'
DRIVERS = utils.load_drivers()


async def get_soup(url):
    """Request the URL and return response as BeautifulSoup object or None."""
    res = requests.get(url).content
    if res is None:
        print('Unable to get soup, response was None.')
        return None
    return BeautifulSoup(res, 'lxml')


async def check_status():
    """Monitor connection to Ergast API by recording connection status and time for response.
    Returns int: 1 = Good, 2 = Medium, 3 = Bad, 0 = Down.
    """
    start_time = datetime.now()
    res = await get_soup(f'{BASE_URL}/current/driverStandings')
    end_time = datetime.now()
    delta = end_time - start_time
    if res is None:
        return 0
    if delta.seconds > 5:
        return 2
    elif delta.seconds > 15:
        return 3
    else:
        return 1


async def get_all_drivers():
    """Fetch all driver data as JSON. Returns a dict."""
    url = f'{BASE_URL}/drivers.json?limit=1000'
    # Get JSON data as dict
    res = requests.get(url)
    if res is None:
        raise MissingDataError()
    return res


def get_driver_info(driver_id):
    """Get the driver name, age, nationality, code and number.
    Searches a dictionary containing all drivers from the Ergast API for an
    entry with a matching ID, surname or number given in the `driver_id` arg.
    Parameters
    ----------
    `driver_id`
        Either of: a driver ID used by Ergast API, e.g. 'alonso', 'michael_schumacher';
        the driver code, e.g. 'HAM', 'VET'; or the driver number, e.g. 44, 6.
    Returns
    -------
    dict
        {
            'firstname': str,
            'surname': str,
            'code': str,
            'id': str,
            'url': str,
            'number': str,
            'age': int,
            'nationality': str
        }
    Raises
    ------
    `DriverNotFoundError`
        if no match found.
    """
    driver = utils.find_driver(driver_id, DRIVERS)
    res = {
        'firstname': driver['givenName'],
        'surname': driver['familyName'],
        'code': driver.get('code', None),
        'id': driver['driverId'],
        'url': driver.get('url', None),
        'number': driver.get('permanentNumber', None),
        'age': utils.age(driver['dateOfBirth'][:4]),
        'nationality': driver['nationality'],
    }
    return res


async def get_driver_standings(season):
    """Get the driver championship standings.
    Fetches results from API. Response XML is parsed into a list of dicts to be tabulated.
    Data includes position, driver code, total points and wins.
    Parameters
    ----------
    `season` : int
    Returns
    -------
    `res` : dict
        {
            'season': str,
            'round': str,
            'data': list[dict] [{
                'Pos': int,
                'Driver': str,
                'Points': int,
                'Wins': int,
            }]
        }
    Returns None if nothing happens
    """
    url = f'{BASE_URL}/{season}/driverStandings'
    soup = await get_soup(url)
    if soup:
        # tags are lowercase
        standings = soup.standingslist
        results = {
            'season': standings['season'],
            'round': standings['round'],
            'data': [],
        }
        for standing in standings.find_all('driverstanding'):
            results['data'].append(
                {
                    'Pos': int(standing['position']),
                    'Driver': f"{standing.driver.givenname.string[0]} {standing.driver.familyname.string}",
                    'Points': int(standing['points']),
                    'Wins': int(standing['wins']),
                }
            )
        return results
    raise MissingDataError()


async def get_team_standings(season):
    """Get the constructor championship standings.
    Fetches results from API. Response XML is parsed into a list of dicts to be tabulated.
    Data includes position, team, total points and wins.
    Parameters
    ----------
    `season` : int
    Returns
    -------
    `res` : dict
        {
            'season': str,
            'round': str,
            'data': list[dict] [{
                'Pos': int,
                'Team': str,
                'Points': int,
                'Wins': int,
            }]
        }
    Returns None if there is no response
    """
    url = f'{BASE_URL}/{season}/constructorStandings'
    soup = await get_soup(url)
    if soup:
        standings = soup.standingslist
        results = {
            'season': standings['season'],
            'round': standings['round'],
            'data': [],
        }
        for standing in standings.find_all('constructorstanding'):
            results['data'].append(
                {
                    'Pos': int(standing['position']),
                    'Team': standing.constructor.find('name').string,
                    'Points': int(standing['points']),
                    'Wins': int(standing['wins']),
                }
            )
        return results
    raise MissingDataError()


async def get_race_results(rnd, season, winner_only=False):
    """Get race results for `round` in `season` as dict.
    E.g. `get_race_results(12, 2008)` --> Results for 2008 season, round 12.
    Data includes finishing position, fastest lap, finish status, pit stops per driver.
    Parameters
    ----------
    `rnd` : int
    `season` : int
    `winner_only` : bool
    Returns
    -------
    `res` : dict
        {
            'season': str,
            'round': str,
            'race': str,
            'url': str,
            'date': str,
            'time': str,
            'data': list[dict] [{
                'Pos': int,
                'Driver': str,
                'Team': str,
                'Laps': int,
                'Start': int,
                'Time': str,
                'Status': str,
                'Points': int,
            }],
            'timings': list[dict] [{
                'Rank': int,
                'Driver': str,
                'Time': str,
                'Speed': int,
            }]
        }
    Raises
    ------
    `MissingDataError`
        if API response unavailable.
    """
    if winner_only is True:
        url = f'{BASE_URL}/{season}/{rnd}/results/1'
    else:
        url = f'{BASE_URL}/{season}/{rnd}/results'
    soup = await get_soup(url)
    if soup:
        race = soup.race
        race_results = race.resultslist.find_all('result')
        date, time = (race.date.string, race.time.string)
        res = {
            'season': race['season'],
            'round': race['round'],
            'race': race.racename.string,
            'url': race['url'],
            'date': f"{utils.date_parser(date)} {race['season']}",
            'time': utils.time_parser(time),
            'data': [],
            'timings': [],
        }
        for result in race_results:
            driver = result.driver
            # Now get the fastest lap time element
            fastest_lap = result.fastestlap
            res['data'].append(
                {
                    'Pos': int(result['position']),
                    'Driver': f'{driver.givenname.string[0]} {driver.familyname.string}',
                    'Team': result.constructor.find('name').string,
                    'Start': int(result.grid.string),
                    'Laps': int(result.laps.string),
                    'Status': result.status.string,
                    'Points': int(result['points']),
                }
            )
            # Fastest lap data if available
            if fastest_lap is not None:
                res['timings'].append(
                    {
                        'Rank': int(fastest_lap['rank']),
                        'Driver': driver['code'],
                        'Time': fastest_lap.time.string,
                        'Speed (kph)': int(float(fastest_lap.averagespeed.string)),
                    }
                )
        return res
    raise MissingDataError()


async def get_all_laps(rnd, season):
    """Get time and position data for each driver per lap in the race.
    Parameters
    ----------
    `rnd`, `season` : int
    Returns
    -------
    `res` : dict
        {
            'season': str,
            'round': str,
            'race': str,
            'url': str,
            'date': str,
            'time': str,
            'data': dict[list] - dict keys are lap number and values are list of dicts per driver:
                {
                    1: [ {'id': str, 'lap': int, 'pos': int, 'time': str} ... ],
                    2: [ ... ],
                    ...
                }
        }
    Raises
    ------
    `MissingDataError`
        if API response invalid.
    """
    url = f"{BASE_URL}/{season}/{rnd}/laps?limit=2000"
    soup = await get_soup(url)
    if soup:
        race = soup.race
        laps = race.lapslist.find_all('lap')
        date, time = (race.date.string, race.time.string)
        res = {
            'season': race['season'],
            'round': race['round'],
            'race': race.racename.string,
            'url': race['url'],
            'date': f"{utils.date_parser(date)} {race['season']}",
            'time': utils.time_parser(time),
            'data': {},
        }
        for lap in laps:
            res['data'][int(lap['number'])] = [
                {
                    'id': t['driverid'],
                    'Pos': int(t['position']),
                    'Time': t['time']
                }
                for t in lap.find_all('timing')]
        return res
    raise MissingDataError()


async def get_all_laps_for_driver(driver, laps):
    """Get the lap times for each lap of the race for one driver to tabulate.
    Each dict entry contains lap number, race position and lap time. The API can take time to
    process all of the lap time data.
    Parameters
    ----------
    `driver_id` : dict
        Driver dict as returned by `api.get_driver_info()`.
    `laps` : dict
        lap and timing data for the race as returned by `api.get_all_laps`.
    Returns
    -------
    `res` : dict
        {
            'driver': dict,
            'season': race['season'],
            'round': race['round'],
            'race': race.racename.string,
            'url': race['url'],
            'date': f"{utils.date_parser(date)} {race['season']}",
            'time': utils.time_parser(time),
            'data': list[dict] [{
                'No': int,
                'Position': int,
                'Time': str,
            }]
        }
    Raises
    ------
    `MissingDataError`
        if response invalid.
    """
    # Force list as second arg as filter expects
    driver_laps = utils.filter_laps_by_driver(laps, [driver['id']])
    res = {
        'driver': driver,
        'season': laps['season'],
        'round': laps['round'],
        'race': laps['race'],
        'url': laps['url'],
        'date': laps['date'],
        'time': laps['time'],
        'data': []
    }
    # Loop over lap:timing_list pairs from filtered laps dict
    # Only one driver to filter so each lap's timing list should have single entry at index 0
    for lap, timing in driver_laps['data'].items():
        res['data'].append(
            {
                'Lap': int(lap),
                'Pos': int(timing[0]['Pos']),
                'Time': timing[0]['Time'],
            }
        )
    return res


async def get_qualifying_results(rnd, season):
    """Gets qualifying results for `round` in `season`.
    E.g. `get_qualifying_results(12, 2008)` --> Results for round 12 in 2008 season.
    Data includes Q1, Q2, Q3 times per driver, position, laps per driver.
    Parameters
    ----------
    `rnd` : int or str
        Race number or 'last' for the latest race
    `season` : int or str
        Season year or 'current'
    Returns
    -------
    `res` : dict
        {
            'season': str,
            'round': str,
            'race': str,
            'url': str,
            'date': str,
            'time': str,
            'data': list[dict] [{
                'Pos': int,
                'Driver': str,
                'Team': str,
                'Q1': str,
                'Q2': str,
                'Q3': str,
            }]
        }
    Raises
    ------
    `MissingDataError`
        if API response invalid.
    """
    url = f'{BASE_URL}/{season}/{rnd}/qualifying'
    soup = await get_soup(url)
    if soup:
        race = soup.race
        quali_results = race.qualifyinglist.find_all('qualifyingresult')
        date, time = (race.date.string, race.time.string)
        res = {
            'season': race['season'],
            'round': race['round'],
            'race': race.racename.string,
            'url': race['url'],
            'date': f"{utils.date_parser(date)} {race['season']}",
            'time': utils.time_parser(time),
            'data': []
        }
        for result in quali_results:
            res['data'].append(
                {
                    'Pos': int(result['position']),
                    'Driver': result.driver['code'],
                    'Team': result.constructor.find('name').string,
                    'Q1': result.q1.string if result.q1 is not None else None,
                    'Q2': result.q2.string if result.q2 is not None else None,
                    'Q3': result.q3.string if result.q3 is not None else None,
                }
            )
        return res
    raise MissingDataError()


async def get_pitstops(rnd, season):
    """Get the race pitstop times for each driver.
    Parameters
    ----------
    `season`, `rnd` : int
    Returns
    -------
    `res` : list[dict] {
        'season': str,
        'round': str,
        'race': str,
        'date': str,
        'time': str,
        'total_laps': int,
        'data': list[dict] {
            'Driver_id': str,
            'Stop_no': int,
            'Lap': int,
            'Time': str,
            'Duration': str,
        }
    }
    Raises
    ------
    `MissingDataError`
        if API response invalid.
    """
    url = f"{BASE_URL}/{season}/{rnd}/pitstops?limit=100"
    soup = await get_soup(url)
    if soup:
        race = soup.race
        pitstops = race.pitstopslist.find_all('pitstop')
        date, time = (race.date.string, race.time.string)
        results = await get_race_results(rnd, season, winner_only=True)
        laps = results['data'][0]['Laps']
        res = {
            'season': race['season'],
            'round': race['round'],
            'race': race.racename.string,
            'date': f"{utils.date_parser(date)} {race['season']}",
            'time': utils.time_parser(time),
            'total_laps': laps,
            'data': []
        }
        for stop in pitstops:
            driver = get_driver_info(stop['driverid'])
            res['data'].append(
                {
                    'Driver': f"{driver['code']}",
                    'Stop_no': int(stop['stop']),
                    'Lap': int(stop['lap']),
                    'Time': stop['time'],
                    'Duration': stop['duration'],
                }
            )
        return res
    raise MissingDataError()


async def get_driver_championship_wins(driver_id):
    """Returns dict with driver standings results where the driver placed first.
    Parameters
    ----------
    `driver_id` : str
        must be valid Eargast API ID, e.g. 'alonso', 'michael_schumacher'.
    Returns
    -------
    `res` : dict
        {
            'total': int,
            'data': list[dict] [{
                'Season': str,
                'Points': int,
                'Wins': int,
                'Team': str,
            }]
        }
    Raises
    ------
    `MissingDataError`
    """
    url = f"{BASE_URL}/drivers/{driver_id}/driverStandings/1"
    soup = await get_soup(url)
    if soup:
        standings = soup.standingstable.find_all('standingslist')
        res = {
            'total': int(soup.mrdata['total']),
            'data': []
        }
        for standing in standings:
            res['data'].append(
                {
                    'Season': standing['season'],
                    'Pos': int(standing.driverstanding['position']),
                    'Wins': int(standing.driverstanding['wins']),
                    'Points': int(standing.driverstanding['points']),
                    'Team': standing.driverstanding.constructor.find('name').string,
                }
            )
        return res
    raise MissingDataError()


async def get_driver_wins(driver_id):
    """Get total wins for the driver and a list of dicts with details for each race.
    Parameters
    ----------
    `driver_id` : str
        must be valid Eargast API ID, e.g. 'alonso', 'michael_schumacher'.
    Returns
    -------
    `res` : dict
        {
            'total': int,
            'data': list[dict] [{
                'Race': str,
                'Circuit': str,
                'Date': str,
                'Team': str,
                'Grid': int,
                'Laps': int,
                'Time': str,
            }]
        }
    Raises
    ------
    `MissingDataError`
        if API response invalid.
    """
    url = f"{BASE_URL}/drivers/{driver_id}/results/1?limit=200"
    soup = await get_soup(url)
    if soup:
        races = soup.racetable.find_all('race')
        res = {
            'total': int(soup.mrdata['total']),
            'data': []
        }
        for race in races:
            race_result = race.resultslist.result
            res['data'].append(
                {
                    'Race': race.racename.string,
                    'Date': utils.date_parser(race.date.string, type='dick'),
                    'Team': race_result.constructor.find('name').string,
                    'Grid': int(race_result.grid.string),
                    'Time': race_result.time.string,
                }
            )
        return res
    raise MissingDataError()


async def get_driver_poles(driver_id):
    """Get total pole positions for driver with details for each race.
    Parameters
    ----------
    `driver_id` : str
        must be valid Eargast API ID, e.g. 'alonso', 'michael_schumacher'.
    Returns
    -------
    `res` : dict
        {
            'total': int,
            'data': list[dict] [{
                'Race': str,
                'Circuit': str,
                'Date': str,
                'Team': str,
                'Q1': str,
                'Q2': str,
                'Q3': str,
            }]
        }
    Raises
    ------
    `MissingDataError`
        if API response invalid.
    """
    url = f"{BASE_URL}/drivers/{driver_id}/qualifying/1?limit=200"
    soup = await get_soup(url)
    if soup:
        races = soup.racetable.find_all('race')
        res = {
            'total': int(soup.mrdata['total']),
            'data': []
        }
        for race in races:
            quali_result = race.qualifyinglist.qualifyingresult
            res['data'].append(
                {
                    'Race': race.racename.string,
                    'Date': utils.date_parser(race.date.string, type='benis'),
                    'Team': quali_result.constructor.find('name').string,
                    'Q1': quali_result.q1.string if quali_result.q1 is not None else None,
                    'Q2': quali_result.q2.string if quali_result.q2 is not None else None,
                    'Q3': quali_result.q3.string if quali_result.q3 is not None else None,
                }
            )
        return res


async def get_driver_seasons(driver_id):
    """Get all seasons the driver has participated in as a dict.
    Raises `MissingDataError`.
    """
    url = f"{BASE_URL}/drivers/{driver_id}/seasons"
    soup = await get_soup(url)
    if soup:
        seasons = soup.seasontable.find_all('season')
        res = {
            'total': int(soup.mrdata['total']),
            'data': [{'year': int(s.string), 'url': s['url']} for s in seasons]
        }
        return res


async def get_driver_teams(driver_id):
    """Get all teams the driver has driven with as a dict containing list of constructor names.
    Raises `MissingDataError`.
    """
    url = f"{BASE_URL}/drivers/{driver_id}/constructors"
    soup = await get_soup(url)
    if soup:
        constructors = soup.constructortable.find_all('constructor')
        res = {
            'total': int(soup.mrdata['total']),
            'data': [c.find('name').string for c in constructors]
        }
        return res


async def get_driver_career(driver):
    """Total wins, poles, points, seasons, teams and DNF's for the driver.
    Parameters
    ----------
    `driver` : dict
        Driver dict as returned by `api.get_driver_info()`.
    Returns
    -------
    `res` : dict
        {
            'driver': dict,
            'data': dict {
                'Wins': int,
                'Poles': int,
                'Championships': dict {
                    'total': int,
                    'years': list
                },
                'Seasons': dict {
                    'total': int,
                    'years': list
                },
                'Teams': dict {
                    'total': int,
                    'names': list
                }
            }
        }
    """
    id = driver['id']
    # prefire standings req first as it takes longest
    standings_task = asyncio.create_task(get_driver_championship_wins(id))
    # Get results concurrently
    [wins, poles, seasons, teams, champs] = await asyncio.gather(
        get_driver_wins(id),
        get_driver_poles(id),
        get_driver_seasons(id),
        get_driver_teams(id),
        standings_task,
    )
    res = {
        'driver': driver,
        'data': {
            'Wins': wins['total'],
            'Poles': poles['total'],
            'Championships': {
                'total': champs['total'],
                'years': [x['Season'] for x in champs['data']],
            },
            'Seasons': {
                'total': seasons['total'],
                'years': [x['year'] for x in seasons['data']],
            },
            'Teams': {
                'total': teams['total'],
                'names': teams['data'],
            },
        }
    }
    return res


async def get_best_laps(rnd, season):
    """Get the best lap for each driver.
    Parameters
    ----------
    `rnd` : int or str
        Race number or 'last' for the latest race
    `season` : int or str
        Season year or 'current'
    Returns
    -------
    `res` : dict
        {   'season': str,
            'round': str,
            'race': str,
            'data': list[dict] {
                'Rank': int,
                'Driver': str,
                'Time': str,
                'Speed': str,
            }
        }
    Raises
    ------
    `MissingDataError`
        If response invalid.
    """
    race_results = await get_race_results(rnd, season)
    res = {
        'season': race_results['season'],
        'round': race_results['round'],
        'race': race_results['race'],
        'data': race_results['timings'],
    }
    return res

def date_parser(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d').strftime('%d %b')


def time_parser(time_str):
    return datetime.strptime(time_str, '%H:%M:%SZ').strftime('%H:%M UTC')


async def get_wiki_thumbnail(url):
    """Get image thumbnail from Wikipedia link. Returns the thumbnail URL."""
    if url is None or url == '':
        return 'https://i.imgur.com/kvZYOue.png'
    # Get URL name after the first '/'
    wiki_title = url.rsplit('/', 1)[1]
    # Get page thumbnail from wikipedia API if it exists
    api_query = ('https://en.wikipedia.org/w/api.php?action=query&format=json&formatversion=2' +
                 '&prop=pageimages&piprop=thumbnail&pithumbsize=600' + f'&titles={wiki_title}')
    res = requests.get(api_query).json()
    first = res['query']['pages'][0]
    # Get page thumb or return placeholder
    if 'thumbnail' in first:
        return first['thumbnail']['source']
    else:
        return 'https://i.imgur.com/kvZYOue.png'


async def schedule(season='current'):
    """
    Returns the schedule for the season.
    -------
    List
    [
        ResponeStatusCode,

        List[dict]
        [
        {
            'season': str,
            'round': str ,
            'url': url,
            'raceName': str,
            'Circuit': dict {
                'circuitId': str,
                'url': str,
                'circuitName': str,
                'location': dict {
                    'lat': str,
                    'long': str,
                    'locality': str,
                    'country' : str,
                }
            }
        }]


    """
    url = f'http://ergast.com/api/f1/{season}.json'
    request = requests.get(url)
    return [request.status_code, request.json()["MRData"]["RaceTable"]["Races"]]

async def nextRace():
    """Get the next race in the calendar and a countdown (from moment of req) as dict.
        Returns
        -------
        `res` : dict
            {
                'season': str,
                'countdown': str,
                'url': str,
                'data': list[dict] [{
                    'Round': int,
                    'Name': str,
                    'Date': str,
                    'Time': str,
                    'Circuit': str,
                    'Country': str,
                    'id':str
                    'url':str
                }]
            }
        Raises
        ------
        `MissingDataError`
            if API response unavailable.
        """
    url: str = f'http://ergast.com/api/f1/current/next.json'
    request = requests.get(url)
    root = request.json()["MRData"]["RaceTable"]
    season = root['season']

    root = root["Races"][0]
    date, time = (root["date"], root["time"])
    cd = utils.countdown(datetime.strptime(f'{date} {time}', '%Y-%m-%d %H:%M:%SZ'))
    result = {
        'season': season,
        'countdown': cd[0],
        'url': root['url'],
        'data': {
            'Round': int(root['round']),
            'Name': root["raceName"],
            'Date': f"{date_parser(date)} {root['season']}",
            'Time': time_parser(time),
            'Circuit': root["Circuit"]['circuitName'],
            'Country': f"{root['Circuit']['Location']['locality']} , {root['Circuit']['Location']['country']}",
            'url': root['Circuit']['url'],
            'id': root["Circuit"]['circuitId']
        }
    }
    return result


async def get_status():
    status = requests.get('https://livetiming.formula1.com/static/StreamingStatus.json')

    if status.status_code == 200:
        status.encoding = 'utf-8-sig'
        if status.json()['Status'] == 'Offline':
            return False
        else:
            return True
    else:
        return False

async def get_session_info():
    info = requests.get('https://livetiming.formula1.com/static/SessionInfo.json')
    info.encoding = 'utf-8-sig'
    info = info.json()
    resDICT = {
        'name': info['Meeting']['Name'],
        'location': f"{info['Meeting']['Location']}, {info['Meeting']['Country']['Name']}",
        'circuit': info['Meeting']['Circuit']['ShortName'],
        'path': info['Path']
    }
    return resDICT


async def get_live(path):
    code = 404
    counter = 0
    while code != 200 and counter <= 3:
        live = requests.get(f'https://livetiming.formula1.com/static/{path}SPFeed.json')
        code = live.status_code
        counter += 1
    if code == 200:
        live.encoding = 'utf-8-sig'
        live = live.json()
        return live
    else:
        return 404


def weather(live):
    data = live['Weather']['graph']['data']
    temps = {
        'trackTemp': data['pTrack'][-1],
        'airTemp': data['pAir'][-1],
        'Rain': data['pRaining'][-1],
        'windSpeed': data['pWind Speed'][-1],
        'humidity': data['pHumidity'][-1],
        'pressure': data['pPressure'][-1],
        'windDir': data['pWind Dir'][-1]
    }
    return temps


def scores(live):
    res = {}
    for metric in live['Scores']['graph'].keys():
        data = live['Scores']['graph'][metric]

        if metric == 'TrackStatus':
            status = {'lap': data[-2], 'status': data[-1]}
            break

        res.setdefault(str(metric), [])
        if metric == 'Performance':
            searchIndex = -1
        else:
            searchIndex = 1
        for i in data.keys():
            dic = {'Driver': i[1:], 'Value': data[i][searchIndex]}
            res[str(metric)].append(dic)
    return res, status

def save_figure(fig, name='plot.png'):
    """Save the figure as a file."""
    fig.savefig(name, bbox_inches='tight')
    print(f"Figure saved as {name}")

def get_colours(live):
    data = live['init']['data']['Drivers']
    res = {}
    for i in data:
        res.setdefault(i['Initials'], i['Color'])
    return res

def pos(live):
    data = live['LapPos']['graph']['data']
    res = {}
    for i in data.keys():
        res.setdefault(i[1:], {'laps':[], 'position':[]})
        for x in range(len(data[i])):
            if x%2==0:
                res[i[1:]]['laps'].append(data[i][x])
            else:
                res[i[1:]]['position'].append(data[i][x])
    return res

async def plotPos(live, colours):
    """Plots the position over lap time"""
    data = pos(live)
    plt.style.use('dark_background')
    fig, ax= plt.subplots()
    fig.set_size_inches(12, 6)
    lastpos = []
    laps = 0
    for driver in data.keys():
        driverData = data[driver]
        plt.plot(driverData['laps'], driverData['position'], figure=fig, color=f"#{colours[driver]}", label=driver)
        lastpos.append(driverData['position'][-1])
        if driverData['laps'][-1] > laps:
            laps = driverData['laps'][-1]
    else:
        plt.xlabel('Lap')
        plt.ylabel('Position')
        plt.gca().invert_yaxis()
        plt.yticks(lastpos, data.keys())
        plt.gca().tick_params(axis='y', right=True, left=True, labelleft=False,labelright=True)
        ax.xaxis.set_minor_locator(MultipleLocator(1))
        save_figure(fig, name='position-plot.png')
    return

def numberRelations(live):
    '''Tells what the driver's name and team is from its number'''
    res = {}
    for i in live['init']['data']['Drivers']:
        res.setdefault(i['Num'], [i['Initials'], i['Team']])
    return res

async def extracTimeData(path):
    res = []
    timeData = requests.get(f'https://livetiming.formula1.com/static/{path}TimingData.json')
    timeData.encoding = 'utf-8-sig'
    timeData = timeData.json()
    for i in timeData['Lines'].keys():
        data = timeData['Lines'][i]
        data['Position'] = int(data['Position'])
        for i in data['Sectors']:
            del i['Segments']
        res.append(data)
        sorted_Position = sorted(res, key=itemgetter('Position'))
    return sorted_Position

async def plotScores(colours, score):
    filenames = []
    for i in score.keys():
        sorted_metric = sorted(score[i], key=itemgetter('Value'))
        drivers = []
        values = []
        colour = []
        for j in sorted_metric:
            drivers.append(j['Driver'])
            colour.append(f"#{colours[j['Driver']]}")
            values.append(j['Value'])
        plt.style.use('dark_background')
        fig = plt.figure(figsize=(12,6))
        plt.title(i)
        plt.grid(axis='y')
        plt.bar(drivers, values, color=colour)
        save_figure(fig, name=f'{i}.png')
        filenames.append(f"{i}.png")
    return filenames

'''
data  = scores()
for i in data[0].keys():
    print(i)
    print(utils.make_table(utils.rank_values(data[0][i]),))
    print()
else:
    print(data[1])
'''
