import discord
import mysql.connector as sql

mycon = sql.connect(host='localhost', user='bot', password='Questionsco1234', auth_plugin= 'mysql_native_password', database='aternos_reborn')
cursor = mycon.cursor(buffered=True)
client = discord.Client()


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    # commands

    if message.content.lower() == 'analyse':
        await message.channel.send("All right chief, creating user profiles")
        for message in await message.channel.history(limit=1000000000).flatten():
            author = str(message.author)
            cursor.execute(f'select * from users where userID = "{author}"')
            data = cursor.fetchall()
            if data == []:
                cursor.execute(f'insert into users values ("{author}", 0, 1)')
                mycon.commit()
            else:
                cursor.execute(f'update users set total = {data[0][2] + 1} where userID = "{author}"')
                mycon.commit()
        else:
            await message.channel.send("Analysis complete")
client.run("Nzk1OTYwMjQ0MzUzMzY4MTA0.X_Q9vg.gPgPZT4xIY81CQCfPiGYm3NYSPg")