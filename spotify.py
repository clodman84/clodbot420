from tekore import Spotify, refresh_user_token
import config

client_id = config.SP_CLIENT_ID
client_secret = config.SP_CLIENT_SECRET
refresh_token = config.SP_REFRESH_TOKEN
app_token = refresh_user_token(client_id, client_secret, refresh_token)


def bubbleSort(list, pop, sorter="g"):  # soapy
    n = len(list)
    if sorter == "g":
        for i in range(0, n - 1):
            for j in range(0, n - 1 - i):
                if abs(list[j].popularity - pop) > abs(list[j + 1].popularity - pop):
                    list[j], list[j + 1] = list[j + 1], list[j]
        return list
    elif sorter == "d":
        for i in range(0, n - 1):
            for j in range(0, n - 1 - i):
                if list[j].popularity < list[j + 1].popularity:
                    list[j], list[j + 1] = list[j + 1], list[j]
        return list


async def search(query):
    spotify = Spotify(app_token, asynchronous=True)
    (search,) = await spotify.search(query, limit=8)
    await spotify.close()
    return search.items, [[track.name, track.artists[0].name] for track in search.items]


# aternos algorithm for making a banger playlist
async def generate(t):
    spotify = Spotify(app_token, asynchronous=True)
    related_artists = await spotify.artist_related_artists(t.artists[0].id)
    top_tracks = []
    for artist in related_artists:
        top_tracks.extend(await spotify.artist_top_tracks(artist.id, "IN"))
    else:
        artists_top = await spotify.artist_top_tracks(t.artists[0].id, "IN")
        # starts with the top 5 from that artist
        mixtape = artists_top[0:5]
        # Checking the ids to make sure the same song does not enter twice

        ids = [song.id for song in mixtape]
        # 15 songs spotify thinks we will like
        recomendations = await spotify.recommendations(track_ids=[t.id], limit=15)
        for track in recomendations.tracks:
            if track.id not in ids:
                mixtape.append(track)

        ids = [song.id for song in mixtape]
        # 10 songs with the closest popularity
        for track in bubbleSort(top_tracks, t.popularity)[0:10]:
            if track.id not in ids:
                mixtape.append(track)

    await spotify.close()
    return [track.uri for track in mixtape], [
        [track.name, track.artists[0].name] for track in mixtape
    ]


async def playlist(tracks):
    spotify = Spotify(app_token, asynchronous=True)
    await spotify.playlist_clear("3uHFXfzb2LeHMMbSCZIShT")
    await spotify.playlist_add("3uHFXfzb2LeHMMbSCZIShT", tracks)
    await spotify.close()


def listSongs(songs):
    if len(songs) == 0:
        return None
    string = "```css\n"
    for song in range(len(songs)):
        if song >= 9:
            item = f"{song + 1}. "
        else:
            item = f"{song + 1}.  "

        if len(songs[song][0]) > 30:
            item += songs[song][0][0:30] + "...   "
        else:
            item += songs[song][0] + " " * (36 - len(songs[song][0]))

        if len(songs[song][1]) > 18:
            item += songs[song][1][0:18] + "...  "
        else:
            item += songs[song][1] + " " * (23 - len(songs[song][1])) + "\n"
        string += item
    else:
        string += "```"
    return string
