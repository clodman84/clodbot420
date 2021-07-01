from discord import File
from discord.embeds import Embed
from discord.ext import commands
from datetime import datetime
import utils
import formula1
import liveFormula
import asyncio
import space
from errors import DriverNotFoundError
from pygicord import Paginator
import airplanes
import texttable as T


LOUD = False

help = commands.DefaultHelpCommand(
    no_category=''
)

bot = commands.Bot(
    command_prefix='--',
    help_command=help,
    case_insensitive=True
)

live = asyncio.run(liveFormula.get_live('2021/2021-06-20_French_Grand_Prix/2021-06-20_Race/'))
numberRelations = liveFormula.numberRelations(live)
colours = liveFormula.get_colours(live)


async def check_season(ctx, season):
    """Raise error if the given season is in the future."""
    if utils.is_future(season):
        await ctx.send(f"Can't predict future :thinking:")
        raise commands.BadArgument('Given season is in the future.')


@bot.event
async def on_command(ctx):
    channel = ctx.message.channel
    user = ctx.message.author
    print(f'Command: {ctx.prefix}{ctx.command} in {channel} by {user}')


@bot.command(aliases=['drivers', 'championship'])
async def wdc(ctx, season='current'):
    """Displays drivers standings
    Usage:
    -----
    --wdc      -> Current standings.
    --wdc 2008 -> Standings in 2008.
    """
    await check_season(ctx, season)
    result = await formula1.get_driver_standings(season)
    table = utils.make_table(result['data'], fmt='simple')
    await ctx.send(
        f"**World Driver Championship**\n" +
        f"Season: {result['season']} Round: {result['round']}\n"
    )
    await ctx.send(f"```\n{table}\n```")


@bot.command(aliases=['teams', 'constructors'])
async def wcc(ctx, season='current'):
    """Display Constructor Championship standings
    Usage:
    ------
    --wcc       -> Current WCC standings as of the last race.
    --wcc 2008  -> WCC standings from 2008.
    """
    await check_season(ctx, season)
    result = await formula1.get_team_standings(season)
    table = utils.make_table(result['data'])
    await ctx.send(
        f"**World Constructor Championship**\n" +
        f"Season: {result['season']} Round: {result['round']}\n"
    )
    await ctx.send(f"```\n{table}\n```")


@bot.command()
async def schedule(ctx, season='current'):
    await check_season(ctx, season)
    schedule = await formula1.schedule(season)
    if schedule[0] == 200:
        data = {'Country': [], 'Search ID': [], 'Date': []}
        for i in schedule[1]:
            data['Country'].append(i["Circuit"]['Location']['country'])
            data['Search ID'].append(i["Circuit"]['circuitId'])
            data['Date'].append(i["date"])
        else:
            await ctx.send(
                f"```{utils.make_table(data)}```")

    else:
        await ctx.send(f"Error {schedule[0]}")


@bot.command()
async def results(ctx, season='current', rnd='last'):
    await check_season(ctx, season)
    result = await formula1.get_race_results(rnd, season)
    try:
        table = [utils.make_table(result['data'], fmt='simple')]
    except:
        data = result['data']
        middle = int(len(data) / 2)
        table = (utils.make_table(data[0:middle]), utils.make_table(data[middle:]))
    await ctx.send(f"**Race Results - {result['race']} ({result['season']})**")
    for i in table:
        await ctx.send(f"```\n{i}\n```")


@bot.command()
async def quali(ctx, season='current', rnd='last'):
    await check_season(ctx, season)
    if int(season) < 2003:
        await ctx.send("Qualifying data is available only from 2003 onwards")
        return
    result = await formula1.get_qualifying_results(rnd, season)
    try:
        table = [utils.make_table(result['data'])]
    except:
        data = result['data']
        middle = int(len(data) / 2)
        table = (utils.make_table(data[0:middle]), utils.make_table(data[middle:]))
    await ctx.send(f"**Qualifying Results - {result['race']} ({result['season']})**")
    for i in table:
        await ctx.send(f"```\n{i}\n```")


@bot.command()
async def driverData(ctx, driver_id):
    await ctx.send("*Gathering driver data, this may take a few moments...*")
    try:
        driver = await formula1.get_driver_info(driver_id)
    except DriverNotFoundError:
        await ctx.send('Driver not found')
    result = await formula1.get_driver_career(driver)
    thumb_url_task = asyncio.create_task(formula1.get_wiki_thumbnail(driver['url']))
    season_list = result['data']['Seasons']['years']
    champs_list = result['data']['Championships']['years']
    embed = Embed(
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
    await ctx.send(embed=embed)


@bot.command()
async def wins(ctx, driver_id):
    driver = formula1.get_driver_info(driver_id)
    await ctx.send(f"**{driver['firstname']} {driver['surname']}** Age:{driver['age']}")
    wins = await formula1.get_driver_wins(driver['id'])
    try:
        table = [utils.make_table(wins['data'], fmt='simple')]
    except:
        data = wins['data']
        middle = int(len(data) / 4)
        table = (utils.make_table(data[0:middle]), utils.make_table(data[middle:2 * middle]),
                 utils.make_table(data[2 * middle:3 * middle]), utils.make_table(data[3 * middle:]))
    for i in table:
        await ctx.send(f"```\n{i}\n```")


@bot.command()
async def poles(ctx, driver_id):
    driver = formula1.get_driver_info(driver_id)
    await ctx.send(f"**{driver['firstname']} {driver['surname']} ** Age:{driver['age']}")
    poles = await ctx.get_driver_poles(driver['id'])
    try:
        table = [utils.make_table(poles['data'], fmt='simple')]
    except:
        data = poles['data']
        middle = int(len(data) / 4)
        table = (utils.make_table(data[0:middle]), utils.make_table(data[middle:2 * middle]),
                 utils.make_table(data[2 * middle:3 * middle]), utils.make_table(data[3 * middle:]))
    for i in table:
        await ctx.send(f"```\n{i}\n```")


@bot.command()
async def lastSession(ctx):
    session = await liveFormula.get_session_info()
    path = session['path']
    live = await liveFormula.get_live(path)
    if live == 404:
        await ctx.send('Alas moment, 404')
        return
    # Big Message showing the name of the Grand Prix
    result = await formula1.nextRace()
    track_url = result['url'].replace(f"{result['season']}_", '')
    track_url_img = await formula1.get_wiki_thumbnail(track_url)
    embed = Embed(
        title=f"**{session['name']}**",
        description=f"{session['circuit']}\n{session['location']}",
        colour=0x1ed9c0,
        url=track_url
    )
    embed.set_thumbnail(url='https://i.imgur.com/kvZYOue.png')
    temps = liveFormula.weather(live)
    embed.add_field(name='Track Temperature', value=temps['trackTemp'])
    embed.add_field(name='Air Temperature', value=temps['airTemp'])
    embed.add_field(name='Rain', value=temps['Rain'])
    embed.add_field(name='Wind Speed', value=temps['windSpeed'])
    embed.add_field(name='Wind Direction', value=temps['windDir'])
    embed.add_field(name='Humidity', value=temps['humidity'])
    embed.add_field(name='Pressure', value=temps['pressure'])
    embed.set_thumbnail(url='https://i.imgur.com/kvZYOue.png')
    embed.set_image(url=track_url_img)
    await ctx.send(embed=embed)

    # ranking messages lessgoo
    timeData = await liveFormula.extracTimeData(path)
    for index in range(len(timeData)):
        i = timeData[index]
        driver = numberRelations[i["RacingNumber"]][0]
        colour = int(colours[driver], 16)
        descrption = f'Last Lap : {i["LastLapTime"]["Value"]}\n'
        if i['LastLapTime']['Value'] == '':
            descrption += 'F moment happened'
            embed = Embed(
                title=f'**{driver}**',
                colour=colour,
                description=descrption
            )
            embed.set_image(url=liveFormula.TeamImage[numberRelations[i["RacingNumber"]][1]][0])
            await ctx.send(embed=embed)
            continue
        if i['LastLapTime']['OverallFastest']:
            descrption += f'**FASTEST LAP SET**\n'
        elif i['LastLapTime']['PersonalFastest']:
            descrption += f"**Personal Fastest Lap**\n"
        else:
            descrption += f"Best : **{i['BestLapTime']['Value']}** Lap *{i['BestLapTime']['Lap']}*\n"
        try:
            if i['IntervalToPositionAhead']['Catching']:
                descrption += f"**{i['IntervalToPositionAhead']['Value']}** to driver ahead *Closing in* \n"
            else:
                descrption += f"**{i['IntervalToPositionAhead']['Value']}** to driver ahead\n"
        except KeyError:
            descrption += f"**{i['TimeDiffToPositionAhead']}** to driver ahead\n"
        if i['InPit']:
            descrption += f'**In Pit** {i["NumberOfPitStops"]} stops\n'
        if i['PitOut']:
            descrption += f'**PitOut** {i["NumberOfPitStops"]} stops\n'
        if i['Retired']:
            descrption += f'**RETIRED**\n'
        if i['Stopped']:
            descrption += '**STOPPED**\n'
        for j in range(len(i['Sectors'])):
            sectorData = i['Sectors'][j]
            if sectorData['OverallFastest']:
                descrption += f'*Sector {j + 1} Time : {sectorData["Value"]}* **Overall Fastest** \n'
            elif sectorData['PersonalFastest']:
                descrption += f'*Sector {j + 1} Time : {sectorData["Value"]}* **Personal Fastest**\n'
        try:
            gap = i['GapToLeader']
        except KeyError:
            gap = i['TimeDiffToFastest']
        embed = Embed(
            title=f'**{driver}** {gap}',
            colour=colour,
            description=descrption
        )
        embed.set_image(url=liveFormula.TeamImage[numberRelations[i["RacingNumber"]][1]][0])
        await ctx.send(embed=embed)


@bot.command()
async def plotpos(ctx):
    sessionInfo = await liveFormula.get_session_info()
    path = sessionInfo['path']
    live = await liveFormula.get_live(path)
    await liveFormula.plotPos(live, colours)
    f = File("position-plot.png", filename='position-plot.png')
    await ctx.send(file=f)


@bot.command()
async def best(ctx, season='current', rnd='last'):
    best = await formula1.get_best_laps(rnd, season)
    await ctx.send(f"**{best['race']} {best['season']}** ")
    try:
        table = [utils.make_table(utils.rank_best_lap_times(best), fmt='simple')]
    except:
        data = utils.rank_best_lap_times(best)
        middle = int(len(data) / 2)
        table = (utils.make_table(data[0:middle]), utils.make_table(data[middle:]))
    for i in table:
        await ctx.send(f"```\n{i}\n```")


@bot.command()
async def nextRace(ctx):
    result = await formula1.nextRace()
    track_url = result['url'].replace(f"{result['season']}_", '')
    track_url_img = asyncio.create_task(formula1.get_wiki_thumbnail(track_url))
    embed = Embed(
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
    await ctx.send(embed=embed)


@bot.command()
async def bimgNow(ctx):
    await ctx.send("Getting ISRO satellite images")
    embed = Embed(title='INSAT-3D Blended Image', colour=0x1ed9c0)
    now = datetime.now()
    date = now.strftime('%d%b')
    year = now.strftime('%Y')
    time = now.strftime('%H%M')
    a = await space.isro_BIMG(date.upper(), year, time)
    if a[0] == 200:
        embed.set_image(url=a[1])
    else:
        embed.set_footer(text='Not Found')
    await ctx.send(embed=embed)


@bot.command()
async def bimg(ctx, date, year, time):
    if len(date) == 5 and len(year) == 4 and len(time) == 4 and int(time) <= 2400:
        embed = Embed(title='INSAT-3D Blended Image', colour=0x1ed9c0)
        a = await space.isro_BIMG(date.upper(), year, time)
        if a[0] == 200:
            embed.set_image(url=a[1])
        else:
            embed.set_footer(text='Not Found')
        await ctx.send(embed=embed)
    else:
        await ctx.send("Please recheck your query")


@bot.command()
async def feed(ctx, sat='3drimager'):
    feed = await space.feed(sat)
    pages = []
    for i in feed:
        embed = Embed(title=i[0], description=i[2], color=0x1ed9c0)
        embed.set_image(url=i[1])
        pages.append(embed)

    paginator = Paginator(pages=pages)
    await paginator.start(ctx)

@bot.command()
async def satlist(ctx):
    satList = ['isrocast', '3dimager', '3drimager']
    await ctx.send(satList)


@bot.command()
async def apod(ctx):
    APoD = await space.apod()
    embed = Embed(title=APoD[2], description=APoD[0], colour=0x1ed9c0)
    embed.set_image(url=APoD[1])
    await ctx.send(embed=embed)


@bot.command()
async def icao24(ctx, icao):
    await ctx.send('Searching ...')
    aircraft = await airplanes.ind(icao)

    if aircraft != None:
        embed = Embed(title=aircraft[1])
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
        await ctx.send(embed=embed)
    else:
        await ctx.send("Can't spot it chief, try another aircraft or try again later.")


@bot.command()
async def iso(ctx, iso):

    await ctx.send('Searching ...')
    result = await airplanes.iso(iso)
    if result == None:
        await ctx.send('The ISO code you sent does not exist')
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
                await ctx.send(
                    f"**{Name}**\n```{table.draw()}```I can sense {Number} aircraft in this area.\n\n{'-' * 10}")


@bot.command()
async def world(ctx):
    zebra = await airplanes.globe()
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
            await ctx.send(f"**World**``` {table.draw()} ```\nI can sense {len(zebra)} aircrafts in this area")

@bot.command()
async def history(ctx, icao):
    await ctx.send('Searching ...')
    table = T.Texttable()
    table.set_cols_width([3, 8, 6, 20, 6])
    table.set_cols_align(['l', 'l', 'c', 'c', 'c'])
    table.set_deco(T.Texttable.VLINES | T.Texttable.HEADER | T.Texttable.BORDER)
    data = [['No.', 'Callsign', 'Depart', 'LastSeen', 'Arive']]
    a = 1
    for plan in await airplanes.history(icao=icao):
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
            await ctx.send('```' + table.draw() + '```')
        else:
            await ctx.send('Aircraft not found')


@bot.command()
async def arrival(ctx, icao):
    await ctx.send('Searching ...')
    zebra = await airplanes.airport(type='arrival', icao=icao)
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
            await ctx.send(
                f"``` {table.draw()}```\nI have tracked {len(zebra)} aircraft arriving at this airport in the last 7 days")
        else:
            await ctx.send('Airport not found')


@bot.command()
async def departure(ctx, icao):
    await ctx.send('Searching ...')
    zebra = await airplanes.airport(type='departure', icao=icao)
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
            await ctx.send(
                f"```{table.draw()}```\nI have tracked {len(zebra)} aircraft departing from this airport in the last 7 days")
        else:
            await ctx.send('Airport not found')