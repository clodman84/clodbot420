import random
from datetime import datetime
import sqlite3 as sql
import asyncio
import discord
import texttable as T
from discord.ext import tasks
import module

# Words and phrases update _____________________________________________________________________________________________

mycon = sql.connect('data.db')
cursor = mycon.cursor()
reply_url = ['https://media1.tenor.com/images/5fc568729ede3645080391e871bce197/tenor.gif?itemid=20747133','https://tenor.com/view/stop-it-stop-get-some-help-michael-jordan-gif-7964841','https://tenor.com/view/its-time-to-stop-stop-clock-time-gif-5001372','https://tenor.com/view/clapping-leonardo-dicaprio-leo-dicaprio-gif-10584134' ]

# ______________________________________________________________________________________________________________________

cooldown = 0
loud = True
client = discord.Client()

# ______________________________________________________________________________________________________________________

@client.event
async def on_ready():
    now = datetime.utcnow()
    current_time = now.strftime("%d/%m/%Y %H:%M:%S")  # starts server
    channel = client.get_channel(799957897017688065)
    print(channel)
    print('The bot is logged in as {0.user}'.format(client))
    if loud:
        de = "Guess who's back."
        embed = discord.Embed(title=module.generator('phrases'), description=de, colour=0x1ed9c0)

        embed.set_footer(text="That's it nothing more " + current_time)
        await channel.send(embed=embed)
    serverStatus.start()  # starts the presence update loop


nukeLaunch = ['https://c.tenor.com/29eE-n-_4xYAAAAM/atomic-nuke.gif', 'https://c.tenor.com/Bupb0hg8c-EAAAAM/cat-launch.gif', 'https://c.tenor.com/xW6YocQ1DokAAAAM/nasa-rocket-launch.gif',
              'https://c.tenor.com/4O7uNcs8vHgAAAAM/rocket-launch.gif', 'https://c.tenor.com/1s8cZTvNNMsAAAAM/sup-dog.gif', 'https://c.tenor.com/uGwGAzGhP50AAAAM/shooting-missiles-zeo-zord-i.gif'
              'https://tenor.com/view/star-wars-death-star-laser-gif-9916316']
banned = []
explosions = ['https://c.tenor.com/BESeHXAH14IAAAAM/little-bit.gif', 'https://c.tenor.com/CWV41b03zPMAAAAM/jenmotzu.gif', 'https://c.tenor.com/9n0weQuYRQ8AAAAM/explosion-dragon-ball.gif',
              'https://c.tenor.com/2vTxvF4JV7UAAAAM/blue-planet.gif', 'https://c.tenor.com/_bbChuywxYsAAAAM/%D0%BF%D0%BB%D0%B0%D0%BD%D0%B5%D1%82%D0%B0-explosion.gif',
              'https://c.tenor.com/lMVdiUIZamcAAAAM/planet-collide-collision.gif', 'https://c.tenor.com/eM_H-IQfig8AAAAM/fedisbomb-explode.gif', 'https://c.tenor.com/LRPLtCBu1WYAAAAM/run-bombs.gif',
              'https://c.tenor.com/Rqe9gYz_WPcAAAAM/explosion-boom.gif', 'https://c.tenor.com/u8jwYAiT_DgAAAAM/boom-bomb.gif', 'https://c.tenor.com/f0zEg6sf1bsAAAAM/destory-eexplode.gif'
              'https://c.tenor.com/f0zEg6sf1bsAAAAM/destory-eexplode.gif', 'https://c.tenor.com/jkRrt2SrlMkAAAAM/pepe-nuke.gif', 'https://c.tenor.com/24gGug50GqQAAAAM/nuke-nuclear.gif']

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    # commands
    global cooldown
    if str(message.author) in banned:
        explosion = explosions[random.randint(0, len(explosions)-1)]
        launch = nukeLaunch[random.randint(0, len(nukeLaunch)-1)]
        if message.attachments or 'tenor' in message.content:
            await message.reply(launch)
            await asyncio.sleep(5)
            await message.reply(explosion)
            await asyncio.sleep(5)
            await message.delete()

    if message.content.startswith('--'):
        now = datetime.utcnow()
        current_time = now.strftime("%d/%m/%Y %H:%M:%S")
        print(str(message.author) + ' said ' + str(message.content) + ' at ' + current_time)
        # New Commands _________________________________________________________________________________________________
        if message.content.lower() == '--satellite now':
            await message.channel.send("Getting ISRO satellite images")
            embed = discord.Embed(title='INSAT-3D', colour=0x1ed9c0)
            date = now.strftime('%d%b')
            year = now.strftime('%Y')
            time = now.strftime('%H%M')
            a = await module.isro(date.upper(), year, time)
            if a[0] == 200:
                embed.set_image(url=a[1])
            else:
                embed.set_footer(text='Not Found')
            await message.channel.send(embed=embed)

        elif message.content.lower()[0:11] == '--satellite':
            await message.channel.send("Getting ISRO satellite images")
            embed = discord.Embed(title='INSAT-3D', colour=0x1ed9c0)
            dat = message.content[12:]
            date = dat[0:5]
            year = dat[5:9]
            time = dat[10:]
            if '' in (date, time, year):
                await message.channel.send('Request incomplete')
                return
            if len(date) == 5 and len(year) == 4 and len(time) == 4 and int(time) < 2400:
                a = await module.isro(date.upper(), year, time)
                if a[0] == 200:
                    embed.set_image(url=a[1])
                else:
                    embed.set_footer(text='Not Found')
                await message.channel.send(embed=embed)
            else:
                await message.channel.send("Please recheck your query")

        elif message.content.lower() == '--map':
            embed = discord.Embed(title='Overworld', color=0x1ed9c0)
            embed.set_image(url='https://cdn.discordapp.com/attachments/830074957954023427/842644631195353088/map-min_1.png')
            embed.set_footer(text="Original was 300 megapixels this one is 75")
            await message.channel.send(embed=embed)
        elif message.content.lower() == '--map riccardo':
            embed = discord.Embed(title='Riccardo\'s Domain', color=0x1ed9c0)
            embed.set_image(url='https://cdn.discordapp.com/attachments/830074957954023427/842668179460325440/riccardo.png')
            embed.set_footer(text="View original and zoom in")
            await message.channel.send(embed=embed)
        elif message.content.lower() == '--apod':
            APoD = await module.Nasa('APoD')
            embed = discord.Embed(title=APoD[2], description=APoD[0], colour=0x1ed9c0)
            embed.set_image(url=APoD[1])
            await message.channel.send(embed=embed)
        elif message.content.lower()[0:8] == '--target' and str(message.author) == 'clodman84#1215':
            banned.append(message.content[9:])
            await message.channel.send(f'{message.content.lower()[9:0]} successfully targeted chief')
        elif message.content.lower() == '--show targets' and str(message.author) == 'clodman84#1215':
            await message.channel.send(banned)
        elif message.content.lower()[0:6] == '--drop' and str(message.author) == 'clodman84#1215':
            banned.remove(message.content[7:])
            await message.channel.send(f'{message.content.lower()[7:]} was removed')
        elif message.content.lower()[0:6] == '--nuke':
            if len(banned) > 0 and int(message.content.lower()[7:]) > 0:
                for i in nukeLaunch:
                    await message.channel.send(i)
                async for message in message.channel.history(limit=int(message.content.lower()[7:])):
                    if str(message.author) in banned and ('tenor' in message.content or message.attachments):
                        await message.reply(explosions[random.randint(0, len(explosions)-1)])
                        await message.delete()
        elif message.content.lower()[0:8] == "--icao24":
            aircraft = await module.ind()
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
            for area in await module.iso(message.content.lower()[6:]):
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
                        await message.channel.send(f"**{Name}**\n\n```{table.draw()}```\n\nI can sense {Number} aircraft in this area.")

        # Global Aircraft Data
        elif message.content.lower() == '--global':
            zebra = await module.globe()
            embed = discord.Embed(title='World',
                                  description="I can sense " + str(len(zebra)) + ' aircrafts in this area',
                                  colour=0x1ed9c0)
            table = T.Texttable()
            table.set_deco(T.Texttable.VLINES | T.Texttable.HEADER | T.Texttable.BORDER)
            table.set_cols_width([3, 8, 6, 11, 8, 8, 13, 10])
            table.set_cols_align(['l', 'l', 'l', 'c', 'r', 'r', 'c', 'c'])
            data = [['No.', 'CallSign', 'Icao24', 'Coords', 'Altitude', 'Vertical', 'Origin', 'True Track']]
            a = 1
            for aircraft in zebra:
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
                    await message.channel.send(f"**World**``` {table.draw()} ```\nI can sense {len(zebra)} aircrafts in this area")

        # tells a single aircraft's history for one week
        elif message.content.lower()[0:9] == '--history':
            await message.channel.send('Searching ...')
            table = T.Texttable()
            table.set_cols_width([3, 8, 6, 20, 6])
            table.set_cols_align(['l', 'l', 'c', 'c', 'c'])
            table.set_deco(T.Texttable.VLINES | T.Texttable.HEADER | T.Texttable.BORDER)
            data = [['No.', 'Callsign', 'Depart', 'LastSeen', 'Arive']]
            a = 1
            for plan in await module.history(icao=message.content.lower()[10:]):
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
            zebra = await module.airport(type='arrivl', icao=message.content.lower()[10:])
            table = T.Texttable()
            table.set_cols_width([3, 6, 8, 20, 6, 20])
            table.set_cols_align(['l', 'c', 'l', 'c', 'c', 'c'])
            table.set_deco(T.Texttable.VLINES | T.Texttable.HEADER)
            data = [['No.', 'Icao24', 'CallSign', 'FirstSeen', 'Depart', 'LastSeen']]
            a = 1
            for plan in zebra:
                if a < 21:
                    data.append([a, plan['icao24'], plan['callsign'],
                                 datetime.fromtimestamp(plan['firstSeen']).strftime('%H:%M:%S  %d/%m/%y'),
                                 plan['estDepartureAirport'],
                                 datetime.fromtimestamp(plan['lastSeen']).strftime('%H:%M:%S  %d/%m/%y'), ])
                    a += 1
            else:
                if len(data) > 1:
                    table.add_rows(data)
                    await message.channel.send(f"``` {table.draw()}```\nI have tracked {len(zebra)} aircraft arriving at this airport in the last 7 days")
                else:
                    await message.channel.send('Airport not found')

        # departures in the last week
        elif message.content.lower()[0:11] == '--departure':
            await message.channel.send('Searching ...')
            zebra = await module.airport(type='departure', icao=message.content.lower()[12:])
            table = T.Texttable()
            table.set_cols_width([3, 6, 8, 20, 6, 20])
            table.set_cols_align(['l', 'c', 'l', 'c', 'c', 'c'])
            table.set_deco(T.Texttable.VLINES | T.Texttable.HEADER)
            data = [['No.', 'Icao24', 'CallSign', 'FirstSeen', 'Arrive', 'LastSeen']]
            a = 1
            for plan in zebra:
                if a < 21:
                    data.append([a, plan['icao24'], plan['callsign'],
                                 datetime.fromtimestamp(plan['firstSeen']).strftime('%H:%M:%S  %d/%m/%y'),
                                 plan['estArrivalAirport'],
                                 datetime.fromtimestamp(plan['lastSeen']).strftime('%H:%M:%S  %d/%m/%y'), ])
                    a += 1
            else:
                if len(data) > 1:
                    table.add_rows(data)
                    await message.channel.send(f"``` {table.draw()}```\nI have tracked {len(zebra)} aircraft departing from this airport in the last 7 days")
                else:
                    await message.channel.send('Airport not found')


        # OLD COMMANDS R.I.P ___________________________________________________________________________________________
        elif message.content.lower() == '--start':
            await message.channel.send("I don't do that anymore :-P\n" + module.generator('minecraft'))

        elif message.content.lower() == '--status':
            await message.channel.send("I have no idea bro. \nEnjoying porno : " + module.generator('phrases'))

        elif message.content.lower() == '--athar1':
            author = message.author
            if str(author) == 'AbsolA1#4589':
                await message.channel.send(f"{author.mention}, the "
                                           f" PussyBitch has been detected \n" + module.generator('sentences'))
                await message.channel.send("Ah I miss the good old days, alas I am no longer capable of providing "
                                           "that info. All of you have aternos accounts, check it on your own from "
                                           "your phone. But I will give you a cool porn site I found " + module.generator(
                    'site'))
            else:
                await message.channel.send(
                    "No idea bro, all of you have aternos account now check from phone, take this minecraft yellow "
                    "text instead. " + module.generator("minecraft"))

        elif message.content.lower() == '--stop':
            await message.channel.send(module.generator('minecraft'))

        elif message.content.lower() == '--wait':
            await message.channel.send("Time is an infinite void, aren't we all waiting for something that never "
                                       "comes closer yet feels like it is. Certified Billi Eyelash moment. " + module.generator(
                'phrases') + ' moment')


        # text based _____________________________________________________________________________________
        elif message.content.lower() == '--clear porn':
            await message.channel.send(module.clear('phrases'))
        elif message.content.lower() == '--clear sites':
            await message.channel.send(module.clear('sites'))
        elif message.content.lower() == '--clear minecraft':
            await message.channel.send(module.clear('minecraft'))
        elif message.content.lower() == '--clear monke':
            await message.channel.send(module.clear('sentences'))

        elif message.content.lower() == '--ammo':
            await message.channel.send(module.ammo())
        elif message.content.lower() == '--joke':
            await message.channel.send(await module.joke())
        elif message.content.lower() == '--ping':
            await message.channel.send(
                "pong! " + str(client.latency) + " seconds\n" + module.generator('minecraft'))
        elif message.content.lower() == '--counter':
            cursor.execute(f'select * from users where userID = "{str(message.author)}"')
            data = cursor.fetchall()[0]
            await message.channel.send(
                message.author.mention + f" you have spoken {data[1]} times today.")
        elif message.content.lower() == '--porn':
            await message.channel.send(module.generator('phrases'))
        elif message.content.lower() == '--people':
            await message.channel.send(await module.Nasa('people'))
        elif message.content.lower() == '--iss':
            await message.channel.send(await module.Nasa('iss'))
        elif message.content.lower() == '--monke':
            await message.channel.send(module.generator('sentences'))
        elif message.content.lower() == '--cooldown':
            await message.channel.send(cooldown)
        elif message.content.lower() == '--minecraft':
            await message.channel.send(module.generator('minecraft'))
        elif message.content.lower() == '--website':
            await message.channel.send(module.generator('sites'))
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
        Text = await module.translate(message.content, str(author))
        embed = discord.Embed(description="*" + Text[0] + "*", colour=0x1ed9c0)
        embed.set_footer(text="-" + Text[1])
        await message.channel.send(embed=embed)
        if Text[1][-4:] == 'CUNT':
            cooldown = 3600

@tasks.loop(seconds=5.0)
async def serverStatus():
    global cooldown
    if cooldown > 0:
        cooldown = cooldown - 5
    return

client.run("Nzk1OTYwMjQ0MzUzMzY4MTA0.X_Q9vg.gPgPZT4xIY81CQCfPiGYm3NYSPg")
