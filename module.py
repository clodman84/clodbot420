import random
from utils import get
import sqlite3 as sql
import asyncio
from datetime import datetime


mycon = sql.connect('data.db')
cursor = mycon.cursor()


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
    response = await get('https://api.funtranslations.com/translate/' + links[random.randint(0, len(links) - 1)], params={"text": txt})
    if response.status == 200:
        output = response.json()['contents']['translated']
        auth = author.split('#')[0]
        code = 200
    else:
        A = outputs[random.randint(0, len(outputs) - 1)]
        output = A[0] + author.split('#')[0]
        auth = A[1]
        code = 69
    return output, auth, code


async def joke():
    """JOKE API. Returns a Joke"""

    if random.randint(0, 10) <= 6:
        url = "https://jokeapi-v2.p.rapidapi.com/joke/Any"
        querystring = {"type": "single, twopart"}
        headers = {
            'x-rapidapi-key': "b2efcc243dmsh9563d2fd99f8086p161761jsn0796dda8a1e7",
            'x-rapidapi-host': "jokeapi-v2.p.rapidapi.com"
        }
        response = await get(url=url, headers=headers, params=querystring)
        if response.json()['type'] == 'single' and response.json()['error'] == False:
            return response.json()['joke']
        elif response.json()['type'] == 'twopart' and response.json()['error'] == False:
            return f"{response.json()['setup']}\n||{response.json()['delivery']}||"
    else:
        url = 'https://official-joke-api.appspot.com/random_joke'
        response = await get(url=url)
        return f"{response.json()['setup']}\n||{response.json()['punchline']}||"


if __name__ == '__main__':
    import cProfile
    import pstats
    pr = cProfile.Profile()
    pr.enable()
    asyncio.run(joke())
    pr.disable()
    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.print_stats()
