import requests
import time
from country_bounding_boxes import (country_subunits_by_iso_code, country_subunits_containing_point)
def aero(type,iso=1,bbox=1, icao=1):
    url = 'https://opensky-network.org/api'
    if type == 'all':
        url = url+'/states/all'
        response = requests.get(url=url)
        return response.json()['states']
    if type == 'bbox':
        if iso != 1:
            url = url + '/states/all'
            box = [c.bbox for c in country_subunits_by_iso_code(iso)]
            print(box)
            name = [c.name for c in country_subunits_by_iso_code(iso)]
            result = []
            for i in range(0, len(box)):
                b = box[i]
                n = name[i]
                param = {'lomin':b[0], 'lamin':b[1], 'lomax':b[2], 'lamax':b[3]}
                response = requests.get(url=url, params=param)
                try:
                    data = response.json()['states']
                    number = len(data)
                except TypeError:
                    data ='Wow such nothing'
                    number = "<=3"
                result.append([n, number, data])
            return result

        if bbox != 1:
            url = url + '/states/all'
            b = bbox
            param = {'lomin': b[0], 'lamin': b[1], 'lomax': b[2], 'lamax': b[3]}
            response = requests.get(url=url, params=param)
            return response.json()['states']

    if type == 'ind' and icao != 1:
            url = url+ '/states/all'
            param = {"icao24":icao}
            response = requests.get(url=url, params=param)
            return response.json()['states'][0]

print(aero('ind', icao='a9a399'))




