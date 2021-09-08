import utils
from bs4 import BeautifulSoup
from datetime import datetime
from errors import MissingDataError
import asyncio

BASE_URL = "http://ergast.com/api/f1"
DRIVERS = utils.load_drivers()


async def get_soup(url):
    """Request the URL and return response as BeautifulSoup object or None."""
    res = await utils.get(url)
    if res is None:
        print("Unable to get soup, response was None.")
        return None
    return BeautifulSoup(res, "lxml")


async def check_status():
    """Monitor connection to Ergast API by recording connection status and time for response.
    Returns int: 1 = Good, 2 = Medium, 3 = Bad, 0 = Down.
    """
    start_time = datetime.now()
    res = await get_soup(f"{BASE_URL}/current/driverStandings")
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
    """Fetch all driver data as JSON. Returns a dict. Useless, but its there lmao"""
    url = f"{BASE_URL}/drivers.json?limit=1000"
    # Get JSON data as dict
    res = utils.get(url)
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
        "firstname": driver["givenName"],
        "surname": driver["familyName"],
        "code": driver.get("code", None),
        "id": driver["driverId"],
        "url": driver.get("url", None),
        "number": driver.get("permanentNumber", None),
        "age": utils.age(driver["dateOfBirth"][:4]),
        "nationality": driver["nationality"],
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
    url = f"{BASE_URL}/{season}/driverStandings"
    soup = await get_soup(url)
    if soup:
        # tags are lowercase
        standings = soup.standingslist
        results = {
            "season": standings["season"],
            "round": standings["round"],
            "data": [],
        }
        for standing in standings.find_all("driverstanding"):
            results["data"].append(
                {
                    "Pos": int(standing["position"]),
                    "Driver": f"{standing.driver.givenname.string[0]} {standing.driver.familyname.string}",
                    "Points": standing["points"],
                    "Wins": int(standing["wins"]),
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
    url = f"{BASE_URL}/{season}/constructorStandings"
    soup = await get_soup(url)
    if soup:
        standings = soup.standingslist
        results = {
            "season": standings["season"],
            "round": standings["round"],
            "data": [],
        }
        for standing in standings.find_all("constructorstanding"):
            results["data"].append(
                {
                    "Pos": int(standing["position"]),
                    "Team": standing.constructor.find("name").string,
                    "Points": standing["points"],
                    "Wins": int(standing["wins"]),
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
        url = f"{BASE_URL}/{season}/{rnd}/results/1"
    else:
        url = f"{BASE_URL}/{season}/{rnd}/results"
    soup = await get_soup(url)
    if soup:
        race = soup.race
        race_results = race.resultslist.find_all("result")
        date, time = (race.date.string, race.time.string)
        res = {
            "season": race["season"],
            "round": race["round"],
            "race": race.racename.string,
            "url": race["url"],
            "date": f"{utils.date_parser(date)} {race['season']}",
            "time": utils.time_parser(time),
            "data": [],
            "timings": [],
        }
        for result in race_results:
            driver = result.driver
            # Now get the fastest lap time element
            fastest_lap = result.fastestlap
            res["data"].append(
                {
                    "Pos": int(result["position"]),
                    "Driver": f"{driver.givenname.string[0]} {driver.familyname.string}",
                    "Team": result.constructor.find("name").string,
                    "Start": int(result.grid.string),
                    "Laps": int(result.laps.string),
                    "Status": result.status.string,
                    "Points": result["points"],
                }
            )
            # Fastest lap data if available
            if fastest_lap is not None:
                res["timings"].append(
                    {
                        "Rank": int(fastest_lap["rank"]),
                        "Driver": driver["code"],
                        "Time": fastest_lap.time.string,
                        "Speed (kph)": int(float(fastest_lap.averagespeed.string)),
                    }
                )
        return res
    raise MissingDataError()


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
    url = f"{BASE_URL}/{season}/{rnd}/qualifying"
    soup = await get_soup(url)
    if soup:
        race = soup.race
        quali_results = race.qualifyinglist.find_all("qualifyingresult")
        date, time = (race.date.string, race.time.string)
        res = {
            "season": race["season"],
            "round": race["round"],
            "race": race.racename.string,
            "url": race["url"],
            "date": f"{utils.date_parser(date)} {race['season']}",
            "time": utils.time_parser(time),
            "data": [],
        }
        for result in quali_results:
            res["data"].append(
                {
                    "Pos": int(result["position"]),
                    "Driver": result.driver["code"],
                    "Team": result.constructor.find("name").string,
                    "Q1": result.q1.string if result.q1 is not None else None,
                    "Q2": result.q2.string if result.q2 is not None else None,
                    "Q3": result.q3.string if result.q3 is not None else None,
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
        races = soup.racetable.find_all("race")
        res = {"total": int(soup.mrdata["total"]), "data": []}
        for race in races:
            race_result = race.resultslist.result
            res["data"].append(
                {
                    "Race": race.racename.string,
                    "Date": utils.date_parser(race.date.string, type="dick"),
                    "Team": race_result.constructor.find("name").string,
                    "Grid": int(race_result.grid.string),
                    "Time": race_result.time.string,
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
        races = soup.racetable.find_all("race")
        res = {"total": int(soup.mrdata["total"]), "data": []}
        for race in races:
            quali_result = race.qualifyinglist.qualifyingresult
            res["data"].append(
                {
                    "Race": race.racename.string,
                    "Date": utils.date_parser(race.date.string, type="benis"),
                    "Team": quali_result.constructor.find("name").string,
                    "Q1": quali_result.q1.string
                    if quali_result.q1 is not None
                    else None,
                    "Q2": quali_result.q2.string
                    if quali_result.q2 is not None
                    else None,
                    "Q3": quali_result.q3.string
                    if quali_result.q3 is not None
                    else None,
                }
            )
        return res


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
        standings = soup.standingstable.find_all("standingslist")
        res = {"total": int(soup.mrdata["total"]), "data": []}
        for standing in standings:
            res["data"].append(
                {
                    "Season": standing["season"],
                    "Pos": int(standing.driverstanding["position"]),
                    "Wins": int(standing.driverstanding["wins"]),
                    "Points": int(standing.driverstanding["points"]),
                    "Team": standing.driverstanding.constructor.find("name").string,
                }
            )
        return res
    raise MissingDataError()


async def get_driver_seasons(driver_id):
    """Get all seasons the driver has participated in as a dict.
    Raises `MissingDataError`.
    """
    url = f"{BASE_URL}/drivers/{driver_id}/seasons"
    soup = await get_soup(url)
    if soup:
        seasons = soup.seasontable.find_all("season")
        res = {
            "total": int(soup.mrdata["total"]),
            "data": [{"year": int(s.string), "url": s["url"]} for s in seasons],
        }
        return res


async def get_driver_teams(driver_id):
    """Get all teams the driver has driven with as a dict containing list of constructor names.
    Raises `MissingDataError`.
    """
    url = f"{BASE_URL}/drivers/{driver_id}/constructors"
    soup = await get_soup(url)
    if soup:
        constructors = soup.constructortable.find_all("constructor")
        res = {
            "total": int(soup.mrdata["total"]),
            "data": [c.find("name").string for c in constructors],
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
    driverID = driver["driverID"]
    # prefire standings req first as it takes longest
    standings_task = asyncio.create_task(get_driver_championship_wins(driverID))
    # Get results concurrently
    [wins, poles, seasons, teams, champs] = await asyncio.gather(
        get_driver_wins(driverID),
        get_driver_poles(driverID),
        get_driver_seasons(driverID),
        get_driver_teams(driverID),
        standings_task,
    )
    res = {
        "driver": driver,
        "data": {
            "Wins": wins["total"],
            "Poles": poles["total"],
            "Championships": {
                "total": champs["total"],
                "years": [x["Season"] for x in champs["data"]],
            },
            "Seasons": {
                "total": seasons["total"],
                "years": [x["year"] for x in seasons["data"]],
            },
            "Teams": {
                "total": teams["total"],
                "names": teams["data"],
            },
        },
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
        "season": race_results["season"],
        "round": race_results["round"],
        "race": race_results["race"],
        "data": race_results["timings"],
    }
    return res


async def get_wiki_thumbnail(url):
    """Get image thumbnail from Wikipedia link. Returns the thumbnail URL."""
    if url is None or url == "":
        return "https://i.imgur.com/kvZYOue.png"
    # Get URL name after the first '/'
    wiki_title = url.rsplit("/", 1)[1]
    # Get page thumbnail from wikipedia API if it exists
    api_query = (
        "https://en.wikipedia.org/w/api.php?action=query&format=json&formatversion=2"
        + "&prop=pageimages&piprop=thumbnail&pithumbsize=600"
        + f"&titles={wiki_title}"
    )
    res = await utils.get(api_query)
    res = res.json()
    first = res["query"]["pages"][0]
    # Get page thumb or return placeholder
    if "thumbnail" in first:
        return first["thumbnail"]["source"]
    else:
        return "https://i.imgur.com/kvZYOue.png"


async def schedule(season):
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
    url = f"http://ergast.com/api/f1/{season}.json"
    request = await utils.get(url)
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
    url: str = f"http://ergast.com/api/f1/current/next.json"
    request = await utils.get(url)
    root = request.json()["MRData"]["RaceTable"]
    season = root["season"]

    root = root["Races"][0]
    date, time = (root["date"], root["time"])
    cd = utils.countdown(datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%SZ"))
    result = {
        "season": season,
        "countdown": cd[0],
        "url": root["url"],
        "data": {
            "Round": int(root["round"]),
            "Name": root["raceName"],
            "Date": f"{utils.date_parser(date)} {root['season']}",
            "Time": utils.time_parser(time),
            "Circuit": root["Circuit"]["circuitName"],
            "Country": f"{root['Circuit']['Location']['locality']} , {root['Circuit']['Location']['country']}",
            "url": root["Circuit"]["url"],
            "id": root["Circuit"]["circuitId"],
        },
    }
    return result


if __name__ == "__main__":
    import cProfile
    import pstats

    pr = cProfile.Profile()
    pr.enable()
    asyncio.run(nextRace())
    pr.disable()
    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.print_stats()
