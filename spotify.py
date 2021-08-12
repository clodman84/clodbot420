from tekore import Spotify, refresh_user_token

client_id = '6612697d6d7a4df2aef70111f85cb552'
client_secret = 'b49c76721f8b42edaf42fbf9035fb62d'
refresh_token = 'AQCwE9baWQCICNuY2-bbHwwjrP0HA84MTWtoQPjV33a0c630zQK_akyepWttZbsH2nAJvcvt0' \
                '--eicFvxqaVZ-6C_05GQJSkxv_xZOcynx4vSGU8DFyZQjQ6c5zUN4S3PBo'
app_token = refresh_user_token(client_id, client_secret, refresh_token)


def bubbleSort(list, pop, sorter='g'):  # soapy
    n = len(list)
    if sorter == 'g':
        for i in range(0, n - 1):
            for j in range(0, n - 1 - i):
                if abs(list[j].popularity - pop) > abs(list[j + 1].popularity - pop):
                    list[j], list[j + 1] = list[j + 1], list[j]
        return list
    elif sorter == 'd':
        for i in range(0, n - 1):
            for j in range(0, n - 1 - i):
                if list[j].popularity < list[j + 1].popularity:
                    list[j], list[j + 1] = list[j + 1], list[j]
        return list


# aternos algorithm for making a banger playlist
async def search(query):
    spotify = Spotify(app_token, asynchronous=True)
    tracks, = await spotify.search(query, limit=1)
    for t in tracks.items:
        related_artists = await spotify.artist_related_artists(t.artists[0].id)
        top_tracks = []
        for artist in related_artists:
            top_tracks.extend(await spotify.artist_top_tracks(artist.id, 'IN'))
        else:
            mixtape = bubbleSort(top_tracks, t.popularity)[0:10]  # 10 songs with the closest popularity
            # now we select the remaining thirty songs with the some randomness and other metrics
            ids = [song.id for song in mixtape]
            recomendations = await spotify.recommendations(track_ids=[t.id], limit=15)
            for track in recomendations.tracks:
                if track.id not in ids:
                    mixtape.append(track)
            ids = [song.id for song in mixtape]
            for track in bubbleSort(top_tracks, None, 'd')[0:5]:  # 10 most popular songs with from related artists
                if track.id not in ids:
                    mixtape.append(track)
            bubbleSort(mixtape, None, 'd')
    await spotify.close()

    return [track.uri for track in mixtape]


async def playlist(tracks):
    spotify = Spotify(app_token, asynchronous=True)
    await spotify.playlist_clear('3uHFXfzb2LeHMMbSCZIShT')
    await spotify.playlist_add('3uHFXfzb2LeHMMbSCZIShT', tracks)
    await spotify.close()


