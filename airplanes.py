from utils import get
from datetime import datetime
from country_bounding_boxes import country_subunits_by_iso_code

async def globe():
    """OPEN SKY API. Global airplane data"""
    url = 'https://opensky-network.org/api/states/all'
    response = await get(url=url)
    return response.json()['states']


async def bbox(bbox):
    """OPEN SKY API. Returns data within a specofic bounding box, not implemented yet"""

    url = 'https://opensky-network.org/api/states/all'
    b = bbox
    param = {'lomin': b[0], 'lamin': b[1], 'lomax': b[2], 'lamax': b[3]}
    response = await get(url=url, params=param)
    return response.json()


async def iso(iso):
    """OPEN SKY API. Uses the same bounding box parameters as before but instead the data comes from a database of
    bounding boxes of various areas by iso code """

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
        response = await get(url=url, params=param)
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
    response = await get(url=url, params=param)
    try:
        return response.json()['states'][0]
    except TypeError:
        return None


async def history(icao):
    """OPEN SKY API. Searches the history of an airplane with its icao code"""

    url = 'https://opensky-network.org/api/flights/aircraft'
    param = {'icao24': icao, 'begin': int(datetime.utcnow().timestamp()) - 604800,
             'end': int(datetime.utcnow().timestamp())}
    response = await get(url=url, params=param)
    return response.json()


async def airport(type, icao):
    """OPEN SKY API. 7 days of arrival or departure data for an aiport's icao code"""

    if type == 'arrival' and icao != 1:
        url = 'https://opensky-network.org/api/flights/arrival'
        param = {'airport': icao, 'begin': int(datetime.utcnow().timestamp()) - 604800,
                 'end': int(datetime.utcnow().timestamp())}
        response = await get(url=url, params=param)
        return response.json()
    if type == 'departure' and icao != 1:
        url = 'https://opensky-network.org/api/flights/departure'
        param = {'airport': icao, 'begin': int(datetime.utcnow().timestamp()) - 604800,
                 'end': int(datetime.utcnow().timestamp())}
        response = await get(url=url, params=param)
        return response.json()

if __name__ == '__main__':
    import asyncio
    import cProfile
    import pstats
    pr = cProfile.Profile()
    pr.enable()
    asyncio.run(airport('arrival', 'kjfk'))
    pr.disable()
    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.print_stats()