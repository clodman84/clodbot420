from country_bounding_boxes import (country_subunits_by_iso_code)
import requests
import random
import sqlite3 as sql
from datetime import datetime
import xml.etree.ElementTree as ET

mycon = sql.connect('data.db')
cursor = mycon.cursor()

"""Only for cosmetic purposes."""

def generator(list_name): # Generates curse words and spicy phrases to make the bot feel alive
    
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

def ammo(): # tells how many of the above phrases are available for use
    """Shows how many of the phrases haven't been used yet"""
    count = []
    for i in ['phrases', 'sentences', 'minecraft', 'sites']:
        cursor.execute(f' select {i}_black from {i} where {i}_black = "not used"')
        data = len(cursor.fetchall())
        count.append(data)
    return (f"Porn Titles :- {count[0]}\nPink Guy Lyrics :- {count[1]}\nMinecraft Yellow Text :- {count[2]}\nPorn Sites :- {count[3]}")

def clear(a): # clears the blacklist in case the bot runs out of phrases
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
        
    if random.randint(0,10) <= 6:
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
            return response.json()['setup'] + '\n' + response.json()['delivery']
    else:
        url = 'https://official-joke-api.appspot.com/random_joke'
        response = requests.request('GET', url)

        return response.json()['setup'] + '\n' + response.json()['punchline']

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
        time = str(int(time[0:2])+1) + '00'
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
            time = '0'+time
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
            count +=1
            a = request.status_code
    return a, url

async def feed(sat):
    """Extracts data from the rich site summary of the mosdac website"""
        
    response = []
    request = requests.get(f'https://mosdac.gov.in/{sat}.xml')
    root = ET.fromstring(request.text)[0]
    for item in root.findall('item'):
        if item.find('guid').attrib['isPermaLink'] == 'true':
            response.append([item.find('title').text, item.find('link').text, item.find('description').text, item.find('pubDate').text])
    return response

def F1():
    """"Formula One API. Might use Ergast"""
    url = "https://api-formula-1.p.rapidapi.com/timezone"

    headers = {
        'x-rapidapi-key': "b2efcc243dmsh9563d2fd99f8086p161761jsn0796dda8a1e7",
        'x-rapidapi-host': "api-formula-1.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers)

    return response.text
