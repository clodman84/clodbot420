import random
from datetime import datetime
import sqlite3 as sql
import asyncio
import discord
import texttable as T
from errors import DriverNotFoundError
from utils import is_future, make_table,rank_best_lap_times
from discord.ext import tasks
import module

# Initialising the F1 data ---------------------------------------------------------------------------------------------

# Words and phrases update _____________________________________________________________________________________________

mycon = sql.connect('data.db')
cursor = mycon.cursor()
reply_url = ['https://media1.tenor.com/images/5fc568729ede3645080391e871bce197/tenor.gif?itemid=20747133',
             'https://tenor.com/view/stop-it-stop-get-some-help-michael-jordan-gif-7964841',
             'https://tenor.com/view/its-time-to-stop-stop-clock-time-gif-5001372',
             'https://tenor.com/view/clapping-leonardo-dicaprio-leo-dicaprio-gif-10584134']

# ______________________________________________________________________________________________________________________

cooldown = 0
loud = False
islive = False
client = discord.Client()

TeamImage = {
'Red Bull Racing':'https://www.formula1.com/content/dam/fom-website/teams/2021/red-bull-racing.png.transform/4col/image.png',
'Mercedes':'https://www.formula1.com/content/dam/fom-website/teams/2021/mercedes.png.transform/4col/image.png',
'McLaren':'https://www.formula1.com/content/dam/fom-website/teams/2021/mclaren.png.transform/4col/image.png',
'AlphaTauri':'https://www.formula1.com/content/dam/fom-website/teams/2021/alphatauri.png.transform/4col/image.png',
'Alpine':'https://www.formula1.com/content/dam/fom-website/teams/2021/alpine.png.transform/4col/image.png',
'Aston Martin':'https://www.formula1.com/content/dam/fom-website/teams/2021/aston-martin.png.transform/4col/image.png',
'Ferrari':'https://www.formula1.com/content/dam/fom-website/teams/2021/ferrari.png.transform/4col/image.png',
'Alfa Romeo Racing':'https://www.formula1.com/content/dam/fom-website/teams/2021/alfa-romeo-racing.png.transform/4col/image.png',
'Williams': 'https://www.formula1.com/content/dam/fom-website/teams/2021/williams.png.transform/4col/image.png',
'Haas F1 Team':'https://www.formula1.com/content/dam/fom-website/teams/2021/haas-f1-team.png.transform/4col/image.png'
}
# ______________________________________________________________________________________________________________________
Update_messages = {'Timing': [],'Chart':None, 'weather': None}
@client.event
async def on_ready():
    now = datetime.utcnow()
    current_time = now.strftime("%d/%m/%Y %H:%M:%S")  # starts server
    channel = client.get_channel(799957897017688065)
    print(channel)
    print('The bot is logged in as {0.user}'.format(client))  # these variables are going to be used again
    global numberRelations
    global colours

    session = await module.get_session_info()
    path = session['path']
    live = await module.get_live(path)
    numberRelations = module.numberRelations(live)
    colours = module.get_colours(live)
    if loud:
        de = "Guess who's back."
        embed = discord.Embed(title=module.generator('phrases'), description=de, colour=0x1ed9c0)

        embed.set_footer(text="That's it nothing more " + current_time)
        await channel.send(embed=embed)
    serverStatus.start()  # starts the presence update loop


async def check_season(ctx, season):
    """Raise error if the given season is in the future."""
    if is_future(season):
        await ctx.send(f"Can't predict future :thinking:")


nukeLaunch = ['https://c.tenor.com/29eE-n-_4xYAAAAM/atomic-nuke.gif',
              'https://c.tenor.com/Bupb0hg8c-EAAAAM/cat-launch.gif',
              'https://c.tenor.com/xW6YocQ1DokAAAAM/nasa-rocket-launch.gif',
              'https://c.tenor.com/4O7uNcs8vHgAAAAM/rocket-launch.gif',
              'https://c.tenor.com/1s8cZTvNNMsAAAAM/sup-dog.gif',
              'https://c.tenor.com/uGwGAzGhP50AAAAM/shooting-missiles-zeo-zord-i.gif'
              'https://tenor.com/view/star-wars-death-star-laser-gif-9916316']
banned = []
explosions = ['https://c.tenor.com/BESeHXAH14IAAAAM/little-bit.gif',
              'https://c.tenor.com/CWV41b03zPMAAAAM/jenmotzu.gif',
              'https://c.tenor.com/9n0weQuYRQ8AAAAM/explosion-dragon-ball.gif',
              'https://c.tenor.com/2vTxvF4JV7UAAAAM/blue-planet.gif',
              'https://c.tenor.com/_bbChuywxYsAAAAM/%D0%BF%D0%BB%D0%B0%D0%BD%D0%B5%D1%82%D0%B0-explosion.gif',
              'https://c.tenor.com/lMVdiUIZamcAAAAM/planet-collide-collision.gif',
              'https://c.tenor.com/eM_H-IQfig8AAAAM/fedisbomb-explode.gif',
              'https://c.tenor.com/LRPLtCBu1WYAAAAM/run-bombs.gif',
              'https://c.tenor.com/Rqe9gYz_WPcAAAAM/explosion-boom.gif',
              'https://c.tenor.com/u8jwYAiT_DgAAAAM/boom-bomb.gif',
              'https://c.tenor.com/f0zEg6sf1bsAAAAM/destory-eexplode.gif'
              'https://c.tenor.com/f0zEg6sf1bsAAAAM/destory-eexplode.gif',
              'https://c.tenor.com/jkRrt2SrlMkAAAAM/pepe-nuke.gif',
              'https://c.tenor.com/24gGug50GqQAAAAM/nuke-nuclear.gif']
satList = ['isrocast', '3dimager', '3drimager']
puppeteer = [False, None]
live = False


@client.event
async def on_message(message):
    if message.author == client.user or message.author.bot:
        return
    # commands
    global cooldown
    global puppeteer
    global Update_messages  # these variables are going to be used again
    global numberRelations
    global colours
    global islive
    if str(message.author) in banned:
        explosion = explosions[random.randint(0, len(explosions) - 1)]
        launch = nukeLaunch[random.randint(0, len(nukeLaunch) - 1)]
        if message.attachments or 'tenor' in message.content:
            await message.reply(launch)
            await asyncio.sleep(5)
            await message.reply(explosion)
            await asyncio.sleep(5)
            await message.delete()
    if message.channel.id == 842796682114498570 and puppeteer[0] and message.content[0:2] != '--':
        channel = client.get_channel(int(puppeteer[1]))
        await channel.send(str(message.content))

    if message.content.startswith('--'):
        now = datetime.utcnow()
        current_time = now.strftime("%d/%m/%Y %H:%M:%S")
        print(str(message.author) + ' said ' + str(message.content) + ' at ' + current_time)
        # formula1 commands --------------------------------------------------------------------------------------------
        if message.content.lower() == '--startlive':
            session = await module.get_session_info()
            path = session['path']
            live = await module.get_live(path)
            # Big Message showing the name of the Grand Prix
            result = await module.nextRace()
            track_url = result['url'].replace(f"{result['season']}_", '')
            track_url_img = await module.get_wiki_thumbnail(track_url)
            embed = discord.Embed(
                title=f"**{session['name']}**",
                description=f"{session['circuit']}\n{session['location']}",
                colour=0x1ed9c0,
                url=track_url
            )
            embed.set_thumbnail(url='https://i.imgur.com/kvZYOue.png')
            temps = module.weather(live)
            embed.add_field(name='Track Temperature', value=temps['trackTemp'])
            embed.add_field(name='Air Temperature', value=temps['airTemp'])
            embed.add_field(name='Rain', value=temps['Rain'])
            embed.add_field(name='Wind Speed', value=temps['windSpeed'])
            embed.add_field(name='Wind Direction', value=temps['windDir'])
            embed.add_field(name='Humidity', value=temps['humidity'])
            embed.add_field(name='Pressure', value=temps['pressure'])
            embed.set_thumbnail(url='https://i.imgur.com/kvZYOue.png')
            embed.set_image(url=track_url_img)
            Update_messages['weather'] = await message.channel.send(embed=embed)

            # ranking messages lessgoo
            timeData = await module.extracTimeData(path)
            table = T.Texttable()
            table.set_deco(T.Texttable.VLINES | T.Texttable.HEADER | T.Texttable.BORDER)
            data = [['NO','DRI', 'LEADER', '+AHEAD', 'LAPTIME', 'BESTLAP', 'REMARK']]
            for index in range(len(timeData)):
                i = timeData[index]
                driver = numberRelations[i["RacingNumber"]][0]
                if index <= 3:
                    colour = int(colours[driver], 16)
                    descrption = f'Last Lap : {i["LastLapTime"]["Value"]}\n'
                    if i['LastLapTime']['OverallFastest']:
                        descrption += f'**FASTEST LAP SET**\n'
                    elif i['LastLapTime']['PersonalFastest']:
                        descrption += f"**Personal Fastest Lap**\n"
                    else:
                        descrption += f"Best : **{i['BestLapTime']['Value']}** Lap *{i['BestLapTime']['Lap']}*\n"
                    if i['IntervalToPositionAhead']['Catching']:
                        descrption += f"**{i['IntervalToPositionAhead']['Value']}** to driver ahead *Closing in* \n"
                    if i['InPit']:
                        descrption += f'**In Pit** {i["NumberOfPitStops"]} stops so far\n'
                    if i['PitOut']:
                        descrption += f'**PitOut** {i["NumberOfPitStops"]} stops so far\n'
                    if i['Retired']:
                        descrption += f'**RETIRED**\n'
                    if i['Stopped']:
                        descrption += '**STOPPED**\n'
                    for j in range(len(i['Sectors'])):
                        sectorData = i['Sectors'][j]
                        if sectorData['OverallFastest']:
                            descrption += f'*Sector {j + 1} Time: {sectorData["Value"]}* **Overall Fastest** \n'
                        elif sectorData['PersonalFastest']:
                            descrption += f'*Sector {j + 1} Time:{sectorData["Value"]}* **Personal Fastest**\n'

                    embed = discord.Embed(
                        title=f'**{driver}** {i["GapToLeader"]}',
                        colour=colour,
                        description=descrption
                    )
                    embed.set_image(url=TeamImage[numberRelations[i["RacingNumber"]][1]])
                    Update_messages['Timing'].append(await message.channel.send(embed=embed))
                else:
                    des = ''
                    if i['LastLapTime']['OverallFastest']:
                        des += 'Fastest Lap '
                    for j in range(len(i['Sectors'])):
                        sectorData = i['Sectors'][j]
                        if sectorData['OverallFastest']:
                            des += f'Sector {j+1} Fastest'
                    if i['InPit']:
                        des = f'IN PITS'
                    if i['PitOut']:
                        des = f'PITOUT'
                    if i['Retired']:
                        des = f'RETIRED'
                    if i['Stopped']:
                        des = 'STOPPED'
                    if i['IntervalToPositionAhead']['Catching']:
                        des += 'Closing Gap'
                    driverData = [index+1,driver, i["GapToLeader"], i['IntervalToPositionAhead']['Value'],i["LastLapTime"]["Value"],i['BestLapTime']['Value'], des]
                    data.append(driverData)

            table.add_rows(data)
            Update_messages['Chart'] = await message.channel.send(f'```{table.draw()}```')

            islive = True
            cooldown = 72000
        elif message.content.lower() == '--stoplive':
            islive = False
            Update_messages = {'Timing': [],'Chart':None, 'weather': None}
            await message.channel.send('Live F1 over')

        elif message.content.lower() == '--plotpos':
            sessionInfo = await module.get_session_info()
            path = sessionInfo['path']
            live = await module.get_live(path)
            await module.plotPos(live, colours)
            f = discord.File("position-plot.png", filename='position-plot.png')
            await message.channel.send(file=f)
        # Need to make fancy plotting commands__________________________________________________________________________
        elif message.content.lower() == '--plotperf':
            return
        #_______________________________________________________________________________________________________________
        elif message.content.lower()[0:5] == '--wdc':
            season = message.content.lower()

            if len(season) == 5:
                season = 'current'
            else:
                season = season[6:]
            await check_season(message.channel, season)
            result = await module.get_driver_standings(season)
            table = make_table(result['data'], fmt='simple')
            await message.channel.send(
                f"**World Driver Championship**\n" +
                f"Season: {result['season']} Round: {result['round']}\n"
            )
            await message.channel.send(f"```\n{table}\n```")
        elif message.content.lower()[0:5] == '--wcc':
            season = message.content.lower()

            if len(season) == 5:
                season = 'current'
            else:
                season = season[6:]
            await check_season(message.channel, season)
            result = await module.get_team_standings(season)
            table = make_table(result['data'])
            target = message.channel
            await target.send(
                f"**World Constructor Championship**\n" +
                f"Season: {result['season']} Round: {result['round']}\n"
            )
            await target.send(f"```\n{table}\n```")

        elif message.content.lower()[0:9] == '--results':
            command = message.content.lower()
            season = 'current'
            rnd = 'last'
            if len(command) > 9:
                subcommand = command.split(' ')
                if len(subcommand) == 2:
                    season = subcommand[1]
                else:
                    season, rnd = subcommand[1:]
            await check_season(message.channel, season)

            result = await module.get_race_results(rnd, season)
            try:
                table = [make_table(result['data'], fmt='simple')]
            except:
                data = result['data']
                middle = int(len(data) / 2)
                table = (make_table(data[0:middle]), make_table(data[middle:]))
            target = message.channel
            await target.send(f"**Race Results - {result['race']} ({result['season']})**")
            for i in table:
                await target.send(f"```\n{i}\n```")


        elif message.content.lower()[0:8] == '--driver':
            command = message.content
            if len(command) > 8:
                driver_id = command.split(' ')[1]
            else:
                await message.channel.send('You need to specify a driver, example vettel, VET or 55')
                return
            """Career stats for the `driver_id`.
                Includes total poles, wins, points, seasons, teams, fastest laps, and DNFs.
                Parameters:
                -----------
                `driver_id`
                    Supported Ergast API ID, e.g. 'alonso', 'michael_schumacher', 'vettel', 'di_resta'.
                Usage:
                --------
                    !f1 career vettel | VET | 55   Get career stats for Sebastian Vettel.
                """
            target = message.channel
            await target.send("*Gathering driver data, this may take a few moments...*")
            try:
                driver = module.get_driver_info(driver_id)
            except DriverNotFoundError:
                await target.send('Driver not found')
            result = await module.get_driver_career(driver)
            thumb_url_task = asyncio.create_task(module.get_wiki_thumbnail(driver['url']))
            season_list = result['data']['Seasons']['years']
            champs_list = result['data']['Championships']['years']
            embed = discord.Embed(
                title=f"**{result['driver']['firstname']} {result['driver']['surname']} Career**",
                url=result['driver']['url'],
                colour=0x1ed9c0,
            )
            embed.set_thumbnail(url=await thumb_url_task)
            embed.add_field(name='Number', value=result['driver']['number'], inline=True)
            embed.add_field(name='Nationality', value=result['driver']['nationality'], inline=True)
            embed.add_field(name='Age', value=result['driver']['age'], inline=True)
            embed.add_field(
                name='Seasons',
                # Total and start to latest season
                value=f"{result['data']['Seasons']['total']} ({season_list[0]}-{season_list[len(season_list) - 1]})",
                inline=True
            )
            embed.add_field(name='Wins', value=result['data']['Wins'], inline=True)
            embed.add_field(name='Poles', value=result['data']['Poles'], inline=True)
            embed.add_field(
                name='Championships',
                # Total and list of seasons
                value=(
                        f"{result['data']['Championships']['total']} " + "\n"
                        + ", ".join(y for y in champs_list if champs_list)
                ),
                inline=False
            )
            embed.add_field(
                name='Teams',
                # Total and list of teams
                value=(
                        f"{result['data']['Teams']['total']} " + "\n"
                        + ", ".join(t for t in result['data']['Teams']['names'])
                ),
                inline=False
            )
            await target.send(embed=embed)

        elif message.content.lower()[0:7] == '--quali':
            command = message.content.lower()
            season = 'current'
            rnd = 'last'
            if len(command) > 7:
                subcommand = command.split(' ')
                if len(subcommand) == 2:
                    season = subcommand[1]
                    if int(season) < 2003:
                        await message.channel.send("Qualifying data is available only from 2003 onwards")
                        return
                else:
                    season, rnd = subcommand[1:]
            await check_season(message.channel, season)

            result = await module.get_qualifying_results(rnd, season)
            try:
                table = [make_table(result['data'])]
            except:
                data = result['data']
                middle = int(len(data) / 2)
                table = (make_table(data[0:middle]), make_table(data[middle:]))
            target = message.channel
            await target.send(f"**Qualifying Results - {result['race']} ({result['season']})**")
            for i in table:
                await target.send(f"```\n{i}\n```")

        elif message.content.lower()[0:6] == '--wins':
            command = message.content
            if len(command) > 6:
                driver_id = command.split(' ')[1]
            else:
                await message.channel.send('You need to specify a driver, example vettel, VET or 55')
                return
            target = message.channel
            await target.send("*Gathering driver data, this may take a few moments...*")
            driver = module.get_driver_info(driver_id)
            await target.send(f"**{driver['firstname']} {driver['surname']}** Age:{driver['age']}")
            wins = await module.get_driver_wins(driver['id'])
            try:
                table = [make_table(wins['data'], fmt='simple')]
            except:
                data = wins['data']
                middle = int(len(data) / 4)
                table = (make_table(data[0:middle]), make_table(data[middle:2 * middle]),
                         make_table(data[2 * middle:3 * middle]), make_table(data[3 * middle:]))
            for i in table:
                await target.send(f"```\n{i}\n```")

        elif message.content.lower()[0:6] == '--pole':
            command = message.content
            if len(command) > 6:
                driver_id = command.split(' ')[1]
            else:
                await message.channel.send('You need to specify a driver, example vettel, VET or 55')
                return

            target = message.channel
            await target.send("*Gathering driver data, this may take a few moments...*")
            driver = module.get_driver_info(driver_id)
            await target.send(f"**{driver['firstname']} {driver['surname']} ** Age:{driver['age']}")
            poles = await module.get_driver_poles(driver['id'])
            try:
                table = [make_table(poles['data'], fmt='simple')]
            except:
                data = poles['data']
                middle = int(len(data) / 4)
                table = (make_table(data[0:middle]), make_table(data[middle:2 * middle]),
                         make_table(data[2 * middle:3 * middle]), make_table(data[3 * middle:]))
            for i in table:
                await target.send(f"```\n{i}\n```")

        elif message.content.lower()[0:6] == '--best':
            command = message.content
            season = 'current'
            rnd = 'last'
            if len(command) > 9:
                subcommand = command.split(' ')
                if len(subcommand) == 2:
                    season = subcommand[1]
                else:
                    season, rnd = subcommand[1:]
            best = await module.get_best_laps(rnd, season)
            await message.channel.send(f"**{best['race']} {best['season']}** ")
            try:
                table = [make_table(rank_best_lap_times(best), fmt='simple')]
            except:
                data = rank_best_lap_times(best)
                middle = int(len(data) / 2)
                table = (make_table(data[0:middle]), make_table(data[middle:]))
            for i in table:
                await message.channel.send(f"```\n{i}\n```")

        elif message.content.lower() == '--next':
            result = await module.nextRace()
            track_url = result['url'].replace(f"{result['season']}_", '')
            track_url_img = asyncio.create_task(module.get_wiki_thumbnail(track_url))
            embed = discord.Embed(
                title=f"**{result['data']['Name']}**",
                description=f"{result['countdown']} left",
                url=track_url,
                colour=0x1ed9c0,
            )
            embed.set_thumbnail(url='https://i.imgur.com/kvZYOue.png')
            embed.add_field(name='Circuit', value=f"[{result['data']['Circuit']}]({result['data']['url']})",
                            inline=False)
            embed.add_field(name='Round', value=result['data']['Round'], inline=True)
            embed.add_field(name='Location', value=result['data']['Country'], inline=True)
            embed.add_field(name='Date', value=result['data']['Date'], inline=True)
            embed.add_field(name='Time', value=result['data']['Time'], inline=True)
            embed.set_image(url=await track_url_img)
            embed.set_footer(text=f'SearchID = {result["data"]["id"]}')
            await message.channel.send(embed=embed)


        elif message.content.lower()[0:10] == '--schedule':
            if len(message.content) == 10:
                schedule = await module.schedule()
                if schedule[0] == 200:
                    table = T.Texttable()
                    table.set_deco(T.Texttable.VLINES | T.Texttable.HEADER | T.Texttable.BORDER)
                    data = [['Country', 'Search ID', 'Date']]
                    for i in schedule[1]:
                        country = i["Circuit"]['Location']['country']
                        searchID = i["Circuit"]['circuitId']
                        date = i["date"]
                        data.append([country, searchID, date])
                    else:
                        table.add_rows(data)
                        await message.channel.send(
                            f"```{table.draw()}```")

                else:
                    await message.channel.send(f"Error {schedule[0]}")
            else:
                print(message.content[10:])
                schedule = module.schedule(int(message.content[10:]))

                if schedule[0] == 200:
                    table = T.Texttable()
                    table.set_deco(T.Texttable.VLINES | T.Texttable.HEADER | T.Texttable.BORDER)
                    data = [['Country', 'Search ID', 'Date']]
                    for i in schedule[1]:
                        country = i["Circuit"]['Location']['country']
                        searchID = i["Circuit"]['circuitId']
                        date = i["date"]
                        data.append([country, searchID, date])
                    else:
                        table.add_rows(data)
                        await message.channel.send(
                            f"```{table.draw()}```")

                else:
                    await message.channel.send(f"Error {schedule[0]}")
        # Older Commands _________________________________________________________________________________________________
        elif message.content.lower() == '--bimg now':
            await message.channel.send("Getting ISRO satellite images")
            embed = discord.Embed(title='INSAT-3D Blended Image', colour=0x1ed9c0)
            date = now.strftime('%d%b')
            year = now.strftime('%Y')
            time = now.strftime('%H%M')
            a = await module.isro_BIMG(date.upper(), year, time)
            if a[0] == 200:
                embed.set_image(url=a[1])
            else:
                embed.set_footer(text='Not Found')
            await message.channel.send(embed=embed)

        elif message.content.lower()[0:8] == '--puppet' and str(message.author) == 'clodman84#1215':
            if puppeteer[0]:
                puppeteer[0] = False
                await message.channel.send("I am now free")
            else:
                puppeteer = [True, message.content.lower()[9:]]
                await message.channel.send(f"I am now being controlled in channel, {message.content.lower()}")

        elif message.content.lower()[0:6] == '--feed':
            author = message
            if message.content.lower()[7:] in satList:
                contents = await module.feed(message.content.lower()[7:])
                cur_page = 1
                pages = len(contents)
                embed = discord.Embed(title=contents[cur_page - 1][0], description=contents[cur_page - 1][2],
                                      color=0x1ed9c0)
                embed.set_image(url=contents[cur_page - 1][1])
                embed.set_footer(text=f"PubDate = {contents[cur_page - 1][3]} page {cur_page}/{pages}")
                message = await message.channel.send(embed=embed)
                # getting the message object for editing and reacting
                await message.add_reaction("◀️")
                await message.add_reaction("▶️")

                while True:
                    try:
                        reaction, user = await client.wait_for("reaction_add", timeout=120)
                        # waiting for a reaction to be added - times out after x seconds, 60 in this
                        # example
                        print(reaction, user, author.author)

                        if user == client.user:
                            None
                        elif str(reaction.emoji) == "▶️" and cur_page != pages and user == author.author:
                            cur_page += 1
                            embed = discord.Embed(title=contents[cur_page - 1][0],
                                                  description=contents[cur_page - 1][2], color=0x1ed9c0)
                            embed.set_image(url=contents[cur_page - 1][1])
                            embed.set_footer(text=f"PubDate = {contents[cur_page - 1][3]} page {cur_page} / {pages}")
                            await message.edit(embed=embed)
                            try:
                                await message.remove_reaction(reaction, user)
                            except:
                                None

                        elif str(reaction.emoji) == "◀️" and cur_page > 1 and user == author.author:
                            cur_page -= 1
                            embed = discord.Embed(title=contents[cur_page - 1][0],
                                                  description=contents[cur_page - 1][2], color=0x1ed9c0)
                            embed.set_image(url=contents[cur_page - 1][1])
                            embed.set_footer(text=f"PubDate = {contents[cur_page - 1][3]} page {cur_page} / {pages}")
                            await message.edit(embed=embed)
                            try:
                                await message.remove_reaction(reaction, user)
                            except:
                                None
                        else:
                            try:
                                await message.remove_reaction(reaction, user)
                            except:
                                None
                            # removes reactions if the user tries to go forward on the last page or
                            # backwards on the first page
                    except asyncio.TimeoutError:
                        await message.channel.send(f"Time is up {author.author.mention}")
                        break
                        # ending the loop if user doesn't react after x seconds


        elif message.content.lower() == '--satlist':
            await message.channel.send(satList)
        elif message.content.lower()[0:6] == '--bimg':
            await message.channel.send("Getting ISRO satellite images")
            embed = discord.Embed(title='INSAT-3D Blended Image', colour=0x1ed9c0)
            dat = message.content[7:]
            date = dat[0:5]
            year = dat[5:9]
            time = dat[10:]
            if '' in (date, time, year):
                await message.channel.send('Request incomplete')
                return
            if len(date) == 5 and len(year) == 4 and len(time) == 4 and int(time) <= 2400:
                a = await module.isro_BIMG(date.upper(), year, time)
                if a[0] == 200:
                    embed.set_image(url=a[1])
                else:
                    embed.set_footer(text='Not Found')
                await message.channel.send(embed=embed)
            else:
                await message.channel.send("Please recheck your query")

        elif message.content.lower() == '--map':
            embed = discord.Embed(title='Overworld', color=0x1ed9c0)
            embed.set_image(
                url='https://cdn.discordapp.com/attachments/830074957954023427/842644631195353088/map-min_1.png')
            embed.set_footer(text="Original was 300 megapixels this one is 75")
            await message.channel.send(embed=embed)
        elif message.content.lower() == '--map riccardo':
            embed = discord.Embed(title='Riccardo\'s Domain', color=0x1ed9c0)
            embed.set_image(
                url='https://cdn.discordapp.com/attachments/830074957954023427/842668179460325440/riccardo.png')
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
                        await message.reply(explosions[random.randint(0, len(explosions) - 1)])
                        await message.delete()
        elif message.content.lower()[0:8] == "--icao24":
            await message.channel.send('Searching ...')
            aircraft = await module.ind(message.content.lower()[9:])

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
            result = await module.iso(message.content.lower()[6:])
            if result == None:
                await message.channel.send('The ISO code you sent does not exist')
                return
            for area in result:
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
                        await message.channel.send(
                            f"**{Name}**\n```{table.draw()}```I can sense {Number} aircraft in this area.\n\n{'-' * 10}")

        # Global Aircraft Data
        elif message.content.lower() == '--global':
            zebra = await module.globe()
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
                    await message.channel.send(
                        f"**World**``` {table.draw()} ```\nI can sense {len(zebra)} aircrafts in this area")

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
            zebra = await module.airport(type='arrival', icao=message.content.lower()[10:])
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
                    await message.channel.send(
                        f"``` {table.draw()}```\nI have tracked {len(zebra)} aircraft arriving at this airport in the last 7 days")
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
                    await message.channel.send(
                        f"``` {table.draw()}```\nI have tracked {len(zebra)} aircraft departing from this airport in the last 7 days")
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

    if message.attachments or any(
            ele in content for ele in ['/', '%', 'https', ':', 'http', '--']) or message.reference:
        return
    elif (data[0][1] + 1) % 50 == 0 and cooldown == 0 and len(content) <= 2048:
        Text = await module.translate(message.content, str(author))
        embed = discord.Embed(description="*" + Text[0] + "*", colour=0x1ed9c0)
        embed.set_footer(text="-" + Text[1])
        if Text[2] == 200:
            await message.channel.send(embed=embed)
            await message.delete()
        if Text[1][-4:] == 'CUNT':
            cooldown = 3600

@tasks.loop(seconds=5.0)
async def serverStatus():
    global cooldown
    if cooldown > 0:
        cooldown = cooldown - 5.0
    if islive:
        session = await module.get_session_info()
        path = session['path']
        live = await module.get_live(path)
        result = await module.nextRace()
        track_url = result['url'].replace(f"{result['season']}_", '')
        track_url_img = await module.get_wiki_thumbnail(track_url)
        embed = discord.Embed(
            title=f"**{session['name']}**",
            description=f"{session['circuit']}\n{session['location']}",
            colour=0x1ed9c0,
            url=track_url
        )
        embed.set_thumbnail(url='https://i.imgur.com/kvZYOue.png')
        temps = module.weather(live)
        embed.add_field(name='Track Temperature', value=temps['trackTemp'])
        embed.add_field(name='Air Temperature', value=temps['airTemp'])
        embed.add_field(name='Rain', value=temps['Rain'])
        embed.add_field(name='Wind Speed', value=temps['windSpeed'])
        embed.add_field(name='Wind Direction', value=temps['windDir'])
        embed.add_field(name='Humidity', value=temps['humidity'])
        embed.add_field(name='Pressure', value=temps['pressure'])
        embed.set_image(url=track_url_img)
        embed.set_thumbnail(url='https://i.imgur.com/kvZYOue.png')
        await Update_messages['weather'].edit(embed=embed)

        # ranking messages lessgoo
        timeData = await module.extracTimeData(path)
        table = T.Texttable()
        table.set_deco(T.Texttable.VLINES | T.Texttable.HEADER | T.Texttable.BORDER)
        data = [['NO','DRI', 'LEADER', '+AHEAD', 'LAPTIME', 'BESTLAP', 'REMARK']]
        for index in range(len(timeData)):
            i = timeData[index]
            driver = numberRelations[i["RacingNumber"]][0]
            if index <= 3:
                colour = int(colours[driver], 16)
                descrption = f'Last Lap : {i["LastLapTime"]["Value"]}\n'
                if i['LastLapTime']['OverallFastest']:
                    descrption += f'**FASTEST LAP SET**\n'
                elif i['LastLapTime']['PersonalFastest']:
                    descrption += f"**Personal Fastest Lap**\n"
                else:
                    descrption += f"Best : **{i['BestLapTime']['Value']}** Lap *{i['BestLapTime']['Lap']}*\n"
                if i['IntervalToPositionAhead']['Catching']:
                    descrption += f"**{i['IntervalToPositionAhead']['Value']}** to driver ahead *Closing in* \n"
                if i['InPit']:
                    descrption += f'**In Pit** {i["NumberOfPitStops"]} stops so far\n'
                if i['PitOut']:
                    descrption += f'**PitOut** {i["NumberOfPitStops"]} stops so far\n'
                if i['Retired']:
                    descrption += f'**RETIRED**\n'
                if i['Stopped']:
                    descrption += '**STOPPED**\n'
                for j in range(len(i['Sectors'])):
                    sectorData = i['Sectors'][j]
                    if sectorData['OverallFastest']:
                        descrption += f'*Sector {j + 1} Time: {sectorData["Value"]}* **Overall Fastest** \n'
                    elif sectorData['PersonalFastest']:
                        descrption += f'*Sector {j + 1} Time:{sectorData["Value"]}* **Personal Fastest**\n'

                embed = discord.Embed(
                    title=f'**{driver}** {i["GapToLeader"]}',
                    colour=colour,
                    description=descrption
                )
                embed.set_image(url=TeamImage[numberRelations[i["RacingNumber"]][1]])
                await Update_messages['Timing'][index].edit(embed=embed)
            else:
                des = ''
                if i['LastLapTime']['OverallFastest']:
                    des += 'Fastest Lap '
                for j in range(len(i['Sectors'])):
                    sectorData = i['Sectors'][j]
                    if sectorData['OverallFastest']:
                        des += f'SCTR {j + 1} Fastest'
                if i['InPit']:
                    des = 'IN PITS'
                if i['PitOut']:
                    des = 'PITOUT'
                if i['Retired']:
                    des = 'RETIRED'
                if i['Stopped']:
                    des = 'STOPPED'
                if i['IntervalToPositionAhead']['Catching']:
                    des += 'Closing Gap'
                driverData = [index + 1, driver, f' {i["GapToLeader"]}', f" {i['IntervalToPositionAhead']['Value']}",
                              i["LastLapTime"]["Value"], i['BestLapTime']['Value'], des]
                data.append(driverData)
        table.add_rows(data)
        await Update_messages['Chart'].edit(content=f'```{table.draw()}```')
    return


client.run("Nzk1OTYwMjQ0MzUzMzY4MTA0.X_Q9vg.kXnNCNVT7NZfhC92jVTqbJa9LIY")
