from utils import get
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from operator import itemgetter

TeamImage = {
    'Red Bull Racing': [
        'https://www.formula1.com/content/dam/fom-website/teams/2021/red-bull-racing.png.transform/4col/image.png',
        'https://www.formula1.com/content/dam/fom-website/teams/2021/red-bull-racing-logo.png.transform/2col/image.png'],
    'Mercedes': ['https://www.formula1.com/content/dam/fom-website/teams/2021/mercedes.png.transform/4col/image.png',
                 'https://www.formula1.com/content/dam/fom-website/teams/2021/mercedes-logo.png.transform/2col/image'
                 '.png'],
    'McLaren': ['https://www.formula1.com/content/dam/fom-website/teams/2021/mclaren.png.transform/4col/image.png',
                'https://www.formula1.com/content/dam/fom-website/teams/2021/mclaren-logo.png.transform/2col/image.png'],
    'AlphaTauri': [
        'https://www.formula1.com/content/dam/fom-website/teams/2021/alphatauri.png.transform/4col/image.png',
        'https://www.formula1.com/content/dam/fom-website/teams/2021/alphatauri-logo.png.transform/2col/image.png'],
    'Alpine': ['https://www.formula1.com/content/dam/fom-website/teams/2021/alpine.png.transform/4col/image.png',
               'https://www.formula1.com/content/dam/fom-website/teams/2021/alpine-logo.png.transform/2col/image.png'],
    'Aston Martin': [
        'https://www.formula1.com/content/dam/fom-website/teams/2021/aston-martin.png.transform/4col/image.png',
        'https://www.formula1.com/content/dam/fom-website/teams/2021/aston-martin-logo.png.transform/2col/image.png'],
    'Ferrari': ['https://www.formula1.com/content/dam/fom-website/teams/2021/ferrari.png.transform/4col/image.png',
                'https://www.formula1.com/content/dam/fom-website/teams/2021/ferrari-logo.png.transform/2col/image.png'],
    'Alfa Romeo Racing': [
        'https://www.formula1.com/content/dam/fom-website/teams/2021/alfa-romeo-racing.png.transform/4col/image.png',
        'https://www.formula1.com/content/dam/fom-website/teams/2021/alfa-romeo-racing-logo.png.transform/2col/image'
        '.png'],
    'Williams': ['https://www.formula1.com/content/dam/fom-website/teams/2021/williams.png.transform/4col/image.png',
                 'https://www.formula1.com/content/dam/fom-website/teams/2021/williams-logo.png.transform/2col/image'
                 '.png'],
    'Haas F1 Team': [
        'https://www.formula1.com/content/dam/fom-website/teams/2021/haas-f1-team.png.transform/4col/image.png',
        'https://www.formula1.com/content/dam/fom-website/teams/2021/haas-f1-team-logo.png.transform/2col/image.png']
}


async def get_status():
    status = await get('https://livetiming.formula1.com/static/StreamingStatus.json')

    if status.status_code == 200:
        status.encoding = 'utf-8-sig'
        if status.json()['Status'] == 'Offline':
            return False
        else:
            return True
    else:
        return False


async def get_session_info():
    info = await get('https://livetiming.formula1.com/static/SessionInfo.json')
    info.encoding = 'utf-8-sig'
    info = info.json()
    resDICT = {
        'name': info['Meeting']['Name'],
        'location': f"{info['Meeting']['Location']}, {info['Meeting']['Country']['Name']}",
        'circuit': info['Meeting']['Circuit']['ShortName'],
        'path': info['Path']
    }
    return resDICT


async def get_live(path):
    live = await get(f'https://livetiming.formula1.com/static/{path}SPFeed.json')
    code = live.status_code
    if code == 200:
        live.encoding = 'utf-8-sig'
        live = live.json()
        return live
    else:
        return 404


def weather(live):
    data = live['Weather']['graph']['data']
    temps = {
        'trackTemp': data['pTrack'][-1],
        'airTemp': data['pAir'][-1],
        'Rain': data['pRaining'][-1],
        'windSpeed': data['pWind Speed'][-1],
        'humidity': data['pHumidity'][-1],
        'pressure': data['pPressure'][-1],
        'windDir': data['pWind Dir'][-1]
    }
    return temps


def scores(live):
    res = {}
    for metric in live['Scores']['graph'].keys():
        data = live['Scores']['graph'][metric]

        if metric == 'TrackStatus':
            break

        res.setdefault(str(metric), [])
        if metric == 'Performance':
            searchIndex = -1
        else:
            searchIndex = 1
        for i in data.keys():
            dic = {'Driver': i[1:], 'Value': data[i][searchIndex]}
            res[str(metric)].append(dic)
    return res


def save_figure(fig, name='plot.png'):
    """Save the figure as a file."""
    fig.savefig(name, bbox_inches='tight')
    print(f"Figure saved as {name}")


def get_colours(live):
    data = live['init']['data']['Drivers']
    res = {}
    for i in data:
        res.setdefault(i['Initials'], i['Color'])
    return res


def pos(live):
    data = live['LapPos']['graph']['data']
    res = {}
    for i in data.keys():
        res.setdefault(i[1:], {'laps': [], 'position': []})
        for x in range(len(data[i])):
            if x % 2 == 0:
                res[i[1:]]['laps'].append(data[i][x])
            else:
                res[i[1:]]['position'].append(data[i][x])
    return res


async def plotPos(live, colours):
    """Plots the position over lap time"""
    data = pos(live)
    plt.style.use('dark_background')
    fig, ax = plt.subplots()
    fig.set_size_inches(12, 6)
    lastpos = []
    laps = 0
    for driver in data.keys():
        driverData = data[driver]
        try:
            colour=f"#{colours[driver]}"
        except KeyError:
            colour='#19f723'
        plt.plot(driverData['laps'], driverData['position'], figure=fig, color=colour, label=driver)
        lastpos.append(driverData['position'][-1])
        if driverData['laps'][-1] > laps:
            laps = driverData['laps'][-1]
    else:
        plt.xlabel('Lap')
        plt.ylabel('Position')
        plt.gca().invert_yaxis()
        plt.yticks(lastpos, data.keys())
        plt.gca().tick_params(axis='y', right=True, left=True, labelleft=False, labelright=True)
        ax.xaxis.set_minor_locator(MultipleLocator(1))
        save_figure(fig, name='position-plot.png')
    return


def numberRelations(live):
    """Tells what the driver's name and team is from its number"""
    res = {}
    for i in live['init']['data']['Drivers']:
        res.setdefault(i['Num'], [i['Initials'], i['Team']])
    return res


async def extracTimeData(path):
    res = []
    timeData = await get(f'https://livetiming.formula1.com/static/{path}TimingData.json')
    timeData.encoding = 'utf-8-sig'
    timeData = timeData.json()
    for i in timeData['Lines'].keys():
        data = timeData['Lines'][i]
        data['Position'] = int(data['Position'])
        for j in data['Sectors']:
            del j['Segments']
        res.append(data)
    sorted_Position = sorted(res, key=itemgetter('Position'))
    return sorted_Position


async def plotScores(colours, score):
    filename = []
    for i in score.keys():
        sorted_metric = sorted(score[i], key=itemgetter('Value'))
        drivers = []
        values = []
        colour = []
        for j in sorted_metric:
            drivers.append(j['Driver'])
            colour.append(f"#{colours[j['Driver']]}")
            values.append(j['Value'])
        plt.style.use('dark_background')
        fig = plt.figure(figsize=(12, 6))
        plt.title(i)
        plt.grid(axis='y')
        plt.bar(drivers, values, color=colour)
        save_figure(fig, name=f'{i}.png')
        filename.append(f"{i}.png")
    return filename
