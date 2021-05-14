import random
from datetime import datetime
import sqlite3 as sql
from country_bounding_boxes import (country_subunits_by_iso_code)
import discord
import requests
import texttable as T
from discord.ext import tasks

# Words and phrases update _____________________________________________________________________________________________

mycon = sql.connect('data.db')
cursor = mycon.cursor()


def generator(list_name): # This is pure bullshit, I wrote it and now I regret it, it could be much smaller, just select  once :facepalm:
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


def ammo():
    count = []
    for i in ['phrases', 'sentences', 'minecraft', 'sites']:
        cursor.execute(f' select {i}_black from {i} where {i}_black = "not used"')
        data = len(cursor.fetchall())
        count.append(data)
    return (f"Porn Titles :- {count[0]}\nPink Guy Lyrics :- {count[1]}\nMinecraft Yellow Text :- {count[2]}\nPorn Sites :- {count[3]}")



def clear(a):
    try:
        cursor.execute(f'update {a} set {a}_black = "not used"')
        return "A blacklist was cleared on " + str(datetime.utcnow())
    except:
        return "Something went wrong"


# ______________________________________________________________________________________________________________________

cooldown = 0
loud = True
client = discord.Client()

# defining the functions here only


outputs = [["Thee men talk too much i am did tire of translating thy words especially ", "Shakespeare_CUNT"],
           ["Tired of translating I am, talk too much you do ", 'Yoda_CUNT'],
           ["I am tired of translatin' you dudes. I just wanna smoke crack with ", "Valley_CUNT"],
           ['I im su tured ouff truonsleting yuou, zeet talkateev ', 'European_CUNT'],
           ["I be so tired o' translatin' ye, that talkative ", 'Pirates_of_the_CUNT']]
links = ['shakespeare.json', 'pirate.json', 'yoda.json', 'chef.json', 'valspeak.json']


#  API update __________________________________________________________________________________________________________
async def translate(txt, author):
    global cooldown
    response = requests.get('https://api.funtranslations.com/translate/' + links[random.randint(0, len(links) - 1)],
                            params={"text": txt})
    if response.status_code == 200:
        output = response.json()['contents']['translated']
        auth = author.split('#')[0]
    else:
        A = outputs[random.randint(0, len(outputs) - 1)]
        output = A[0] + author.split('#')[0]
        auth = A[1]
        cooldown = 3600
    return output, auth


async def aero(type, iso=1, bbox=1, icao=1):
    url = 'https://opensky-network.org/api'
    if type == 'all':
        url = url + '/states/all'
        response = requests.get(url=url)
        return response.json()['states']
    # Searches a geographic area
    if type == 'bbox':
        # If an area iso is provided it searches through the database and returns thr correct bounding boxes and
        # performs the query

        if iso != 1:
            url = url + '/states/all'
            box = [c.bbox for c in country_subunits_by_iso_code(iso)]  # the bounding box coords
            name = [c.name for c in country_subunits_by_iso_code(iso)]  # the name of the corresponding bounding box
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
            return result  # returns a multi dimensional list, which element containinng the name of the bounding box
            # specified, the number of aircraft and the data of each and every aircraft

        # this search is raw bounding box search, yet to be implemented
        if bbox != 1:
            url = url + '/states/all'
            b = bbox
            param = {'lomin': b[0], 'lamin': b[1], 'lomax': b[2], 'lamax': b[3]}
            response = requests.get(url=url, params=param)
            return response.json()

    # searches an individual aircraft
    if type == 'ind' and icao != 1:
        url = url + '/states/all'
        param = {"icao24": icao}
        response = requests.get(url=url, params=param)
        try:
            return response.json()['states'][0]
        except TypeError:
            return None
    # Gives One week of Data
    if type == 'plan' and icao != 1:
        url = url + '/flights/aircraft'
        param = {'icao24': icao, 'begin': int(datetime.utcnow().timestamp()) - 604800,
                 'end': int(datetime.utcnow().timestamp())}
        response = requests.get(url=url, params=param)
        return response.json()
    # searches 7 days of data and returns latest 20
    if type == 'arrival' and icao != 1:
        url = url + '/flights/arrival'
        param = {'airport': icao, 'begin': int(datetime.utcnow().timestamp()) - 604800,
                 'end': int(datetime.utcnow().timestamp())}
        response = requests.get(url=url, params=param)
        return response.json()
    if type == 'departure' and icao != 1:
        url = url + '/flights/departure'
        param = {'airport': icao, 'begin': int(datetime.utcnow().timestamp()) - 604800,
                 'end': int(datetime.utcnow().timestamp())}
        response = requests.get(url=url, params=param)
        return response.json()


async def joke():
    if random.randint(0,10) < 5:
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


# ______________________________________________________________________________________________________________________

@client.event
async def on_ready():
    now = datetime.now()
    current_time = now.strftime("%d/%m/%Y %H:%M:%S")  # logs into aternos
    channel = client.get_channel(799957897017688065)
    print(channel)
    print('The bot is logged in as {0.user}'.format(client))
    if loud:
        de = "Guess who's back."
        embed = discord.Embed(title=generator('phrases'), description=de, colour=0x1ed9c0)

        embed.set_footer(text="That's it nothing more " + current_time)
        await channel.send(embed=embed)
    serverStatus.start()  # starts the presence update loop


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    # commands

    if message.content.startswith('--'):
        now = datetime.now()
        current_time = now.strftime("%d/%m/%Y %H:%M:%S")
        print(str(message.author) + ' said ' + str(message.content) + ' at ' + current_time)
        # New Commands _________________________________________________________________________________________________
        if message.content.lower() == '--map':
            embed = discord.Embed(title='Overworld', color=0x1ed9c0)
            embed.set_image(url='https://cdn.discordapp.com/attachments/830074957954023427/842644631195353088/map-min_1.png')
            embed.set_footer(text="Original was 300 megapixels this one is 75")
            await message.channel.send(embed=embed)
        if message.content.lower() == '--map riccardo':
            embed = discord.Embed(title='Riccardo\'s Domain', color=0x1ed9c0)
            embed.set_image(url='https://cdn.discordapp.com/attachments/830074957954023427/842668179460325440/riccardo.png')
            embed.set_footer(text="View original and zoom in")
            await message.channel.send(embed=embed)
        if message.content.lower() == '--apod':
            APoD = await Nasa('APoD')
            embed = discord.Embed(title=APoD[2], description=APoD[0], colour=0x1ed9c0)
            embed.set_image(url=APoD[1])
            await message.channel.send(embed=embed)

        elif message.content.lower()[0:8] == "--icao24":
            aircraft = await aero('ind', icao=message.content.lower()[9:])
            await message.channel.send('Searching ...')
            if aircraft != None:
                embed = discord.Embed(title=aircraft[1])
                embed.add_field(name="icao24", value=aircraft[0])
                embed.add_field(name='Origin', value=aircraft[2])
                embed.add_field(name='Time_Pos',
                                value=datetime.fromtimestamp(aircraft[3]).strftime('%H:%M:%S  %d/%m/%y'))
                embed.add_field(name='Last_Contact',
                                value=datetime.fromtimestamp(aircraft[4]).strftime('%H:%M:%S  %d/%m/%y'))
                embed.add_field(name="Longitude", value=aircraft[5])
                embed.add_field(name='Latitude', value=aircraft[6])
                embed.add_field(name='Baro_Altitude', value=aircraft[7])
                embed.add_field(name='On_Ground', value=aircraft[8])
                embed.add_field(name='Velocity', value=aircraft[9])
                embed.add_field(name='True_Track', value=aircraft[10])
                embed.add_field(name='Vertical Rate', value=aircraft[11])
                embed.add_field(name='Geo_Altitude', value=aircraft[13])
                await message.channel.send(embed=embed)
            else:
                await message.channel.send("Can't spot it chief, try another aircraft or try again later.")

        elif message.content.lower()[0:5] == '--iso':
            await message.channel.send('Searching ...')
            for area in await aero(type='bbox', iso=message.content.lower()[6:]):
                Name = area[0]
                Number = area[1]
                # Generating tables hehe boai
                table = T.Texttable()
                table.set_deco(T.Texttable.VLINES | T.Texttable.HEADER | T.Texttable.BORDER)
                table.set_cols_width([3, 8, 6, 13, 10, 8, 8, 10])
                table.set_cols_align(['l', 'l', 'l', 'c', 'r', 'r', 'r', 'c'])
                data = [['No.', 'CallSign', 'Icao24', 'Coords', 'Altitude', 'Vertical', 'Velocity', 'True Track']]
                a = 1
                for aircraft in area[2]:
                    if len(aircraft) == 17 and a < 11:
                        try:
                            coords = str(round(aircraft[6], 1)) + ' ' + str(round(aircraft[5], 1))
                        except TypeError:
                            coords = 'Unknown'
                        try:
                            alt = round(aircraft[13], 0)
                        except TypeError:
                            alt = 'Unknown'
                        data.append(
                            [a, aircraft[1], aircraft[0], coords,
                             alt, aircraft[11], aircraft[9], aircraft[10]])
                        a += 1
                else:
                    if a > 1:
                        table.add_rows(data)
                        embed = discord.Embed(title=Name,
                                              description="```" + table.draw() + '```',
                                              colour=0x1ed9c0)
                        embed.set_footer(text="I can sense " + str(Number) + ' aircrafts in this area')
                        await message.channel.send(embed=embed)

        # Global Aircraft Data
        elif message.content.lower() == '--global':
            penis = await aero(type='all')
            embed = discord.Embed(title='World',
                                  description="I can sense " + str(len(penis)) + ' aircrafts in this area',
                                  colour=0x1ed9c0)
            table = T.Texttable()
            table.set_deco(T.Texttable.VLINES | T.Texttable.HEADER | T.Texttable.BORDER)
            table.set_cols_width([3, 8, 6, 11, 8, 8, 13, 10])
            table.set_cols_align(['l', 'l', 'l', 'c', 'r', 'r', 'c', 'c'])
            data = [['No.', 'CallSign', 'Icao24', 'Coords', 'Altitude', 'Vertical', 'Origin', 'True Track']]
            a = 1
            for aircraft in penis:
                try:
                    coords = str(round(aircraft[6], 1)) + ' ' + str(round(aircraft[5], 1))
                except TypeError:
                    coords = 'Unknown'

                try:
                    alt = round(aircraft[13], 0)
                except TypeError:
                    alt = 'Unknown'
                if len(aircraft) == 17 and a < 11:
                    data.append(
                        [a, aircraft[1], aircraft[0], coords, alt, aircraft[11], aircraft[2], aircraft[10]])
                    a += 1
            else:
                if a > 1:
                    table.add_rows(data)
                    await message.channel.send(f"**World**``` {table.draw()} ```\nI can sense {len(penis)} aircrafts in this area")

        # tells a single aircraft's history for one week
        elif message.content.lower()[0:9] == '--history':
            await message.channel.send('Searching ...')
            table = T.Texttable()
            table.set_cols_width([3, 8, 6, 20, 6])
            table.set_cols_align(['l', 'l', 'c', 'c', 'c'])
            table.set_deco(T.Texttable.VLINES | T.Texttable.HEADER | T.Texttable.BORDER)
            data = [['No.', 'Callsign', 'Depart', 'LastSeen', 'Arive']]
            a = 1
            for plan in await aero(type='plan', icao=message.content.lower()[10:]):
                if a < 16:
                    data.append(
                        [a, plan['callsign'],
                         plan['estDepartureAirport'],
                         datetime.fromtimestamp(plan['lastSeen']).strftime('%H:%M:%S  %d/%m/%y'),
                         plan['estArrivalAirport']])
                    a += 1
            else:
                table.add_rows(data)
                if len(data) > 1:
                    await message.channel.send('```' + table.draw() + '```')
                else:
                    await message.channel.send('Aircraft not found')

        # displays 20 most recent flights and tells how many flights in last 7 days arrived here
        elif message.content.lower()[0:9] == '--arrival':
            await message.channel.send('Searching ...')
            penis = await aero(type='arrival', icao=message.content.lower()[10:])
            table = T.Texttable()
            table.set_cols_width([3, 6, 8, 20, 6, 20])
            table.set_cols_align(['l', 'c', 'l', 'c', 'c', 'c'])
            table.set_deco(T.Texttable.VLINES | T.Texttable.HEADER)
            data = [['No.', 'Icao24', 'CallSign', 'FirstSeen', 'Depart', 'LastSeen']]
            a = 1
            for plan in penis:
                if a < 21:
                    data.append([a, plan['icao24'], plan['callsign'],
                                 datetime.fromtimestamp(plan['firstSeen']).strftime('%H:%M:%S  %d/%m/%y'),
                                 plan['estDepartureAirport'],
                                 datetime.fromtimestamp(plan['lastSeen']).strftime('%H:%M:%S  %d/%m/%y'), ])
                    a += 1
            else:
                if len(data) > 1:
                    table.add_rows(data)
                    await message.channel.send(f"``` {table.draw()}```\nI have tracked {len(penis)} aircraft arriving at this airport in the last 7 days")
                else:
                    await message.channel.send('Airport not found')

        # departures in the last week
        elif message.content.lower()[0:11] == '--departure':
            await message.channel.send('Searching ...')
            penis = await aero(type='departure', icao=message.content.lower()[12:])
            table = T.Texttable()
            table.set_cols_width([3, 6, 8, 20, 6, 20])
            table.set_cols_align(['l', 'c', 'l', 'c', 'c', 'c'])
            table.set_deco(T.Texttable.VLINES | T.Texttable.HEADER)
            data = [['No.', 'Icao24', 'CallSign', 'FirstSeen', 'Arrive', 'LastSeen']]
            a = 1
            for plan in penis:
                if a < 21:
                    data.append([a, plan['icao24'], plan['callsign'],
                                 datetime.fromtimestamp(plan['firstSeen']).strftime('%H:%M:%S  %d/%m/%y'),
                                 plan['estArrivalAirport'],
                                 datetime.fromtimestamp(plan['lastSeen']).strftime('%H:%M:%S  %d/%m/%y'), ])
                    a += 1
            else:
                if len(data) > 1:
                    table.add_rows(data)
                    await message.channel.send(f"``` {table.draw()}```\nI have tracked {len(penis)} aircraft departing from this airport in the last 7 days")
                else:
                    await message.channel.send('Airport not found')


        # OLD COMMANDS R.I.P ___________________________________________________________________________________________
        elif message.content.lower() == '--start':
            await message.channel.send("I don't do that anymore :-P\n" + generator('minecraft'))

        elif message.content.lower() == '--status':
            await message.channel.send("I have no idea bro. \nEnjoying porno : " + generator('phrases'))

        elif message.content.lower() == '--athar1':
            author = message.author
            if str(author) == 'AbsolA1#4589':
                await message.channel.send(f"{author.mention}, the "
                                           f" PussyBitch has been detected \n" + generator('sentences'))
                await message.channel.send("Ah I miss the good old days, alas I am no longer capable of providing "
                                           "that info. All of you have aternos accounts, check it on your own from "
                                           "your phone. But I will give you a cool porn site I found " + generator(
                    'site'))
            else:
                await message.channel.send(
                    "No idea bro, all of you have aternos account now check from phone, take this minecraft yellow "
                    "text instead. " + generator("minecraft"))

        elif message.content.lower() == '--stop':
            await message.channel.send(generator('minecraft'))

        elif message.content.lower() == '--wait':
            await message.channel.send("Time is an infinite void, aren't we all waiting for something that never "
                                       "comes closer yet feels like it is. Certified Billi Eyelash moment. " + generator(
                'phrases') + ' moment')


        # text based _____________________________________________________________________________________
        elif message.content.lower() == '--clear porn':
            await message.channel.send(clear('phrases'))
        elif message.content.lower() == '--clear sites':
            await message.channel.send(clear('sites'))
        elif message.content.lower() == '--clear minecraft':
            await message.channel.send(clear('minecraft'))
        elif message.content.lower() == '--clear monke':
            await message.channel.send(clear('sentences'))
        elif message.content.lower() == '--ammo':
            await message.channel.send(ammo())
        elif message.content.lower() == '--joke':
            await message.channel.send(await joke())
        elif message.content.lower() == '--ping':
            await message.channel.send(
                "pong! " + str(client.latency) + " seconds\n" + generator('minecraft'))
        elif message.content.lower() == '--counter':
            cursor.execute(f'select * from users where userID = "{str(message.author)}"')
            data = cursor.fetchall()[0]
            await message.channel.send(
                message.author.mention + f" you have spoken {data[1]} times today.")
        elif message.content.lower() == '--porn':
            await message.channel.send(generator('phrases'))
        elif message.content.lower() == '--people':
            await message.channel.send(await Nasa('people'))
        elif message.content.lower() == '--iss':
            await message.channel.send(await Nasa('iss'))
        elif message.content.lower() == '--monke':
            await message.channel.send(generator('sentences'))
        elif message.content.lower() == '--cooldown':
            await message.channel.send(cooldown)
        elif message.content.lower() == '--minecraft':
            await message.channel.send(generator('minecraft'))
        elif message.content.lower() == '--website':
            await message.channel.send(generator('sites'))
        # ______________________________________________________________________________________________________________

    author = str(message.author)
    content = str(message.content)
    cursor.execute(f'select * from users where userID = "{author}"')
    data = cursor.fetchall()
    if data == []:
        cursor.execute(f'insert into users values ("{author}", {1}, 0)')
        mycon.commit()
    else:
        cursor.execute(f'update users set daily = {data[0][1] + 1} where userID = "{author}"')
        mycon.commit()

    if message.attachments or any(ele in content for ele in ['/', '%', 'https', ':', 'http', '--']):
        return
    elif (data[0][1] + 1) % 25 == 0 and cooldown == 0 and len(content) <= 2048:
        Text = await translate(message.content, str(author))
        embed = discord.Embed(description="*" + Text[0] + "*", colour=0x1ed9c0)
        embed.set_footer(text="-" + Text[1])
        await message.channel.send(embed=embed)


@tasks.loop(seconds=5.0)
async def serverStatus():
    global cooldown
    if cooldown > 0:
        cooldown = cooldown - 5
    return


client.run("Nzk1OTYwMjQ0MzUzMzY4MTA0.X_Q9vg.gPgPZT4xIY81CQCfPiGYm3NYSPg")
