import sqlite3 as sql
import discord
mycon = sql.connect('data.db')
cursor = mycon.cursor()
client = discord.Client()

channels = [797800736599441490, 797800736599441491, 799957897017688065, 815089209751633950, 816167327275548693]
user_dict = {'clodman84#1215': {'la-comédie': 0, 'aternos_cunt': 0, 'hardcore-minecraft': 0, 'riccardo': 0, 'neko': 0}, 'AbsolA1#4589': {'la-comédie': 0, 'aternos_cunt': 0, 'hardcore-minecraft': 0, 'riccardo': 0, 'neko': 0}, 'The Dark Knight#3439': {'la-comédie': 0, 'aternos_cunt': 0, 'hardcore-minecraft': 0, 'riccardo': 0, 'neko': 0}, 'Aternos_CUNT#4899': {'la-comédie': 0, 'aternos_cunt': 0, 'hardcore-minecraft': 0, 'riccardo': 0, 'neko': 0}, 'HaikuBot#6950': {'la-comédie': 0, 'aternos_cunt': 0, 'hardcore-minecraft': 0, 'riccardo': 0, 'neko': 0}, 'Dyno#3861': {'la-comédie': 0, 'aternos_cunt': 0, 'hardcore-minecraft': 0, 'riccardo': 0, 'neko': 0}, 'AIRHORN SOLUTIONS#0001': {'la-comédie': 0, 'aternos_cunt': 0, 'hardcore-minecraft': 0, 'riccardo': 0, 'neko': 0}, 'Snapman#9033': {'la-comédie': 0, 'aternos_cunt': 0, 'hardcore-minecraft': 0, 'riccardo': 0, 'neko': 0}, 'Message Counter#8013': {'la-comédie': 0, 'aternos_cunt': 0, 'hardcore-minecraft': 0, 'riccardo': 0, 'neko': 0}, 'Message Count +#7918': {'la-comédie': 0, 'aternos_cunt': 0, 'hardcore-minecraft': 0, 'riccardo': 0, 'neko': 0}, 'Soul Massive#5757': {'la-comédie': 0, 'aternos_cunt': 0, 'hardcore-minecraft': 0, 'riccardo': 0, 'neko': 0}, 'Groovy#7254': {'la-comédie': 0, 'aternos_cunt': 0, 'hardcore-minecraft': 0, 'riccardo': 0, 'neko': 0}, 'Deleted User#0000': {'la-comédie': 0, 'aternos_cunt': 0, 'hardcore-minecraft': 0, 'riccardo': 0, 'neko': 0}, 'Naila#1361': {'la-comédie': 0, 'aternos_cunt': 0, 'hardcore-minecraft': 0, 'riccardo': 0, 'neko': 0}, 'Sirona#3754': {'la-comédie': 0, 'aternos_cunt': 0, 'hardcore-minecraft': 0, 'riccardo': 0, 'neko': 0}, 'wiki_CUNT#8287': {'la-comédie': 0, 'aternos_cunt': 0, 'hardcore-minecraft': 0, 'riccardo': 0, 'neko': 0}, 'Wikipedia#0936': {'la-comédie': 0, 'aternos_cunt': 0, 'hardcore-minecraft': 0, 'riccardo': 0, 'neko': 0}, 'Google Assistant#5197': {'la-comédie': 0, 'aternos_cunt': 0, 'hardcore-minecraft': 0, 'riccardo': 0, 'neko': 0}, 'Music_CUNT#5451': {'la-comédie': 0, 'aternos_cunt': 0, 'hardcore-minecraft': 0, 'riccardo': 0, 'neko': 0}, 'GoogleBot#0847': {'la-comédie': 0, 'aternos_cunt': 0, 'hardcore-minecraft': 0, 'riccardo': 0, 'neko': 0}}
{'clodman84#1215': {'la-comédie': 1233, 'aternos_cunt': 8677, 'hardcore-minecraft': 2651, 'riccardo': 446, 'neko': 130}, 'AbsolA1#4589': {'la-comédie': 1214, 'aternos_cunt': 5150, 'hardcore-minecraft': 1522, 'riccardo': 97, 'neko': 158}, 'The Dark Knight#3439': {'la-comédie': 1249, 'aternos_cunt': 7926, 'hardcore-minecraft': 2132, 'riccardo': 177, 'neko': 149}, 'Aternos_CUNT#4899': {'la-comédie': 298, 'aternos_cunt': 11591, 'hardcore-minecraft': 93, 'riccardo': 171, 'neko': 10}, 'HaikuBot#6950': {'la-comédie': 24, 'aternos_cunt': 64, 'hardcore-minecraft': 27, 'riccardo': 1, 'neko': 0}, 'Dyno#3861': {'la-comédie': 19, 'aternos_cunt': 154, 'hardcore-minecraft': 23, 'riccardo': 0, 'neko': 0}, 'AIRHORN SOLUTIONS#0001': {'la-comédie': 1, 'aternos_cunt': 0, 'hardcore-minecraft': 0, 'riccardo': 0, 'neko': 0}, 'Snapman#9033': {'la-comédie': 697, 'aternos_cunt': 2810, 'hardcore-minecraft': 851, 'riccardo': 50, 'neko': 130}, 'Message Counter#8013': {'la-comédie': 1, 'aternos_cunt': 0, 'hardcore-minecraft': 0, 'riccardo': 0, 'neko': 0}, 'Message Count +#7918': {'la-comédie': 1, 'aternos_cunt': 0, 'hardcore-minecraft': 0, 'riccardo': 0, 'neko': 0}, 'Soul Massive#5757': {'la-comédie': 56, 'aternos_cunt': 398, 'hardcore-minecraft': 3, 'riccardo': 2, 'neko': 0}, 'Groovy#7254': {'la-comédie': 31, 'aternos_cunt': 309, 'hardcore-minecraft': 45, 'riccardo': 1, 'neko': 43}, 'Deleted User#0000': {'la-comédie': 1, 'aternos_cunt': 0, 'hardcore-minecraft': 0, 'riccardo': 0, 'neko': 0}, 'Naila#1361': {'la-comédie': 2, 'aternos_cunt': 3, 'hardcore-minecraft': 0, 'riccardo': 0, 'neko': 0}, 'Sirona#3754': {'la-comédie': 19, 'aternos_cunt': 0, 'hardcore-minecraft': 0, 'riccardo': 0, 'neko': 0}, 'wiki_CUNT#8287': {'la-comédie': 1, 'aternos_cunt': 96, 'hardcore-minecraft': 0, 'riccardo': 0, 'neko': 0}, 'Wikipedia#0936': {'la-comédie': 1, 'aternos_cunt': 26, 'hardcore-minecraft': 0, 'riccardo': 0, 'neko': 0}, 'Google Assistant#5197': {'la-comédie': 12, 'aternos_cunt': 69, 'hardcore-minecraft': 0, 'riccardo': 0, 'neko': 0}, 'Music_CUNT#5451': {'la-comédie': 18, 'aternos_cunt': 192, 'hardcore-minecraft': 22, 'riccardo': 0, 'neko': 0}, 'GoogleBot#0847': {'la-comédie': 3, 'aternos_cunt': 0, 'hardcore-minecraft': 0, 'riccardo': 0, 'neko': 0}}


#@client.event
'''
 async def on_ready():
    for cha in channels:
        channel = client.get_channel(cha)
        print(channel)
        async for message in channel.history(limit=None):
           user_dict[str(message.author)][str(channel)] += 1
    else:
        print(user_dict)
        for user in user_dict.keys():
            total = 0
            for t in user_dict[user].values():
                total += t
            else:
                cursor.execute(f"update users set total = {total} where userID = '{user}'")
        else:
            for i in cursor.execute("select * from users"):
                print(i)
'''

cursor.execute(f"update users set userID = 'The Dark Knight#3439' where userID = 'Divyansh#3439'")
cursor.execute(f"update users set total = 9179 where userID = 'The Dark Knight#3439'")
mycon.commit()
for i in cursor.execute("select * from users"):
                print(i)
client.run("Nzk1OTYwMjQ0MzUzMzY4MTA0.X_Q9vg.gPgPZT4xIY81CQCfPiGYm3NYSPg")