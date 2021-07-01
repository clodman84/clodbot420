import random
from datetime import datetime
import sqlite3 as sql
import asyncio
from discord import Embed
from discord.ext import tasks
import module
import commands
import space

# Words and phrases update _____________________________________________________________________________________________

mycon = sql.connect('data.db')
cursor = mycon.cursor()

# ______________________________________________________________________________________________________________________

cooldown = 0
LOUD = True
bot = commands.bot


# ______________________________________________________________________________________________________________________
@bot.event
async def on_ready():
        now = datetime.utcnow()
        current_time = now.strftime("%d/%m/%Y %H:%M:%S")  # starts server
        channel = bot.get_channel(799957897017688065)
        print(channel)
        print('The bot is logged in as {0.user}'.format(bot))  # these variables are going to be used again
        if LOUD:
            de = "Guess who's back."
            embed = Embed(title=module.generator('phrases'), description=de, colour=0x1ed9c0)

            embed.set_footer(text="That's it nothing more " + current_time)
            await channel.send(embed=embed)
        print('All tasks complete!')
        serverStatus.start()


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

puppeteer = [False, None]
live = False


@bot.event
async def on_message(message):
    if message.author == bot.user or message.author.bot:
        return
    # commands
    global cooldown
    global puppeteer  # these variables are going to be used again

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
        channel = bot.get_channel(int(puppeteer[1]))
        await channel.send(str(message.content))

    if message.content.startswith('--'):

        # formula1 commands --------------------------------------------------------------------------------------------
        if message.content.lower() == '--show targets' and str(message.author) == 'clodman84#1215':
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

        # OLD COMMANDS R.I.P
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
                "pong! " + str(bot.latency) + " seconds\n" + module.generator('minecraft'))
        elif message.content.lower() == '--counter':
            cursor.execute(f'select * from users where userID = "{str(message.author)}"')
            data = cursor.fetchall()[0]
            await message.channel.send(
                message.author.mention + f" you have spoken {data[1]} times today.")
        elif message.content.lower() == '--porn':
            await message.channel.send(module.generator('phrases'))
        elif message.content.lower() == '--people':
            await message.channel.send(await space('people'))
        elif message.content.lower() == '--iss':
            await message.channel.send(await space('iss'))
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

    if message.channel.id == 858700343113416704:
        if any(ele in content.lower() for ele in ['sus', 's u s']):
            None
        else:
            embed = Embed(
                description=f"**<@{message.author.id}> You sussy bitch, breaking the sus rule, no sus in your sentence:**\n\n{content}",
                colour=0x1ed9c0)
            embed.set_footer(text=module.generator('sites'))
            await message.channel.send(embed=embed)
            await message.delete()

    if message.attachments or any(
            ele in content for ele in ['/', '%', 'https', ':', 'http', '--']) or message.reference:
        return
    elif (data[0][1] + 1) % 50 == 0 and cooldown == 0 and len(content) <= 2048:
        Text = await module.translate(message.content, str(author))
        embed = Embed(description="*" + Text[0] + "*", colour=0x1ed9c0)
        embed.set_footer(text="-" + Text[1])
        if Text[2] == 200:
            await message.channel.send(embed=embed)
            await message.delete()
        if Text[1][-4:] == 'CUNT':
            cooldown = 3600


@bot.command()
async def puppet(ctx, target):
    global puppeteer
    if ctx.author.id == 793451663339290644:
        if puppeteer[0]:
            puppeteer[0] = False
            await ctx.send("I am now free")
        else:
            puppeteer = [True, target]
            await ctx.send(f"I am now being controlled in channel, {bot.get_channel(int(target))}")


@bot.command()
async def target(ctx, target):
    banned.append(target)
    await ctx.send(f'<@{target}> successfully targeted chief')

@tasks.loop(seconds=5.0)
async def serverStatus():
    global cooldown
    if cooldown > 0:
        cooldown = cooldown - 5.0
    return

bot.run('Nzk1OTYwMjQ0MzUzMzY4MTA0.X_Q9vg.jXalYoWmE-JrquPA84NbL1dVowU')