import requests
import random
import time
async def joke():
    if random.randint(0,10) < 7:
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
        return
def joke2():
    url = 'https://official-joke-api.appspot.com/random_joke'
    response = requests.request('GET', url)

    return response.json()['setup'], response.json()['punchline']


