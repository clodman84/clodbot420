import random
from datetime import datetime, timedelta
import asyncio
from discord import Embed, FFmpegPCMAudio
from discord.ext import tasks
from discord.errors import Forbidden
from discord.ext.commands.errors import BadArgument
import module
import commands
import utils
from space import apod
import reddit
import config

# ______________________________________________________________________________________________________________________

LOUD = True
COOLDOWN = 3600

nukeLaunch  = ['https://c.tenor.com/29eE-n-_4xYAAAAM/atomic-nuke.gif',
              'https://c.tenor.com/Bupb0hg8c-EAAAAM/cat-launch.gif',
              'https://c.tenor.com/xW6YocQ1DokAAAAM/nasa-rocket-launch.gif',
              'https://c.tenor.com/4O7uNcs8vHgAAAAM/rocket-launch.gif',
              'https://c.tenor.com/1s8cZTvNNMsAAAAM/sup-dog.gif',
              'https://c.tenor.com/uGwGAzGhP50AAAAM/shooting-missiles-zeo-zord-i.gif'
              'https://tenor.com/view/star-wars-death-star-laser-gif-9916316']
banned     = []
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
doom = ['https://tenor.com/view/crucible-doom-eternal-slayer-video-game-gif-16830152',
        'https://tenor.com/view/doom-logo-doom-video-game-logo-gif-14624225',
        'https://tenor.com/view/doom-eternal-gif-18822003',
        'https://tenor.com/view/doomslayer-doomguy-doom-eternal-seraphimsaber-gif-21010574',
        'https://tenor.com/view/sword-doom-doom-sword-gif-21163712',
        'https://tenor.com/view/destory-eexplode-nuke-gif-6073338']

PUPPET = [False, None]
bot = commands.bot
COUNTER = {}


# ______________________________________________________________________________________________________________________
@bot.event
async def on_ready():
    now = datetime.utcnow()
    current_time = now.strftime("%d/%m/%Y %H:%M:%S")  # starts server
    channel = bot.get_channel(799957897017688065)
    print(channel)
    print('The bot is logged in as {0.user}'.format(bot))  # these variables are going to be used again
    if LOUD:
        APoD = await apod()
        embed = Embed(title=APoD[2], description=APoD[0], colour=0x1ed9c0)
        embed.set_image(url=APoD[1])
        embed.set_footer(text="That's it nothing more " + current_time)
        await channel.send(embed=embed)
        cd = utils.countdown(datetime.strptime(f'2022-01-01 05:30:00', '%Y-%m-%d %H:%M:%S'))
        description = f'**__January 1st 2022__ is __{cd[0]}__ or __{cd[2]} seconds__ or __{cd[1][0] / 30} months__ or __{cd[1][0] / 7}__ weeks away**'
        embed = Embed(description=description, colour=0x1ed9c0)
        embed.set_image(url='https://cdn.discordapp.com/attachments/842796682114498570/876530474472857671/MrM.png')
        await channel.send(embed=embed)
    serverStatus.start()


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    # commands
    global COOLDOWN
    global PUPPET
    global COUNTER
    await bot.process_commands(message)
    if str(message.author.id) in banned:
        explosion = explosions[random.randint(0, len(explosions) - 1)]
        launch = nukeLaunch[random.randint(0, len(nukeLaunch) - 1)]
        if message.attachments or 'tenor' in message.content:
            await message.reply(launch)
            await asyncio.sleep(5)
            await message.reply(explosion)
            await asyncio.sleep(5)
            await message.delete()

    if len(message.content.split()) == 1 and 'https://www.reddit.com/r/' in message.content:
        data = await reddit.get_image(message.content)
        if data is not None:
            embed = Embed(title=data['title'], url=data['permalink'], colour=0x1ed9c0)
            embed.set_image(url=data['url'])
            embed.set_author(name=message.author.name)
            embed.set_footer(text=f'{data["upvotes"]} upvotes in {data["subreddit"]}. {data["ratio"]}% upvote rate.')
            await message.channel.send(embed=embed)
            await message.delete()

    if any(ele in message.content.lower() for ele in ['who-asked', 'who asked']):
        await message.channel.send('**IT WAS ME! I WAS THE ONE WHO ASKED**')
        dom = doom[random.randint(0, len(doom) - 1)]
        await message.channel.send(dom)

    if message.channel.id == 842796682114498570 and PUPPET[0] and message.content[0:2] != '--':
        channel = bot.get_channel(int(PUPPET[1]))
        await channel.send(str(message.content))

    if STUDY[1] and message.author.id in [i.id for i in STUDY[2].keys()]:
        STUDY[3] += 1
        if message.channel.id != 866030261341650953:
            await message.author.send(
                f'Don\'t stray from the path to **FOREVER MONKE**. Focus yung wan, you can talk when '
                'you have a break.')
        else:
            if STUDY[3] % 12 == 0:
                await message.channel.send('Focus now, don\'t chit-chat, **Forever Monke** is calling.')
        if STUDY[3] > 50:
            await message.channel.send(module.generator('minecraft'))
            await message.channel.send(explosions[random.randint(0, len(doom) - 1)])
            await message.delete()
        elif STUDY[3] == 48:
            await message.channel.send('2 more messages from those who are supposed to be studying, and I enter doom '
                                       'mode')
    '''
    if message.content.startswith('--'):
        print('entered here')
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
                                           "your phone. But I will give you a cool porn site I found " + 
                                           module.generator(
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
        elif message.content.lower() == '--porn':
            await message.channel.send(module.generator('phrases'))
        elif message.content.lower() == '--monke':
            await message.channel.send(module.generator('sentences'))
        elif message.content.lower() == '--cooldown':
            await message.channel.send(COOLDOWN)
        elif message.content.lower() == '--minecraft':
            await message.channel.send(module.generator('minecraft'))
        elif message.content.lower() == '--website':
            await message.channel.send(module.generator('sites'))
        # ______________________________________________________________________________________________________________
    '''
    author = message.author
    content = str(message.content)
    if author.id not in COUNTER:
        COUNTER.setdefault(author.id, 0)
    else:
        COUNTER[author.id] += 1

    if message.channel.id == 858700343113416704:
        if not any(ele in content.lower() for ele in ['sus', 's u s']):
            embed = Embed(
                description=f"**<@{message.author.id}> You sussy bitch, breaking the sus rule, no sus in your "
                            f"sentence:**\n\n{content}",
                colour=0x1ed9c0)
            embed.set_footer(text=module.generator('sites'))
            await message.channel.send(embed=embed)
            await message.delete()
    if message.channel.category.id != 860176783755313182 and (
            any(ele in content.lower() for ele in [':lewd', 'hentai', 'ecchi', 'l e w d']) or message.author.id in
            [337481187419226113, 571027211407196161]):
        dom = doom[random.randint(0, len(doom) - 1)]
        await message.channel.send(dom)
        await message.delete()
    if message.attachments or any(
            ele in content for ele in ['/', '%', ':', 'http', '--']) or message.reference:
        return
    elif (COUNTER[author.id]) % 50 == 0 and COOLDOWN == 0 and len(content) <= 2048 and not message.author.bot:
        Text = await module.translate(message.content, str(author))
        embed = Embed(description="*" + Text[0] + "*", colour=0x1ed9c0)
        embed.set_footer(text="-" + Text[1])
        if Text[2] == 200:
            await message.channel.send(embed=embed)
            await message.delete()
        if Text[1][-4:] == 'CUNT':
            COOLDOWN = 3600
    return


STUDY = [0, False, {}, 0]


@bot.command()
async def diagnose(ctx):
    variables = f'STUDY : {STUDY}\n\n' \
                f'COOLDOWN: {COOLDOWN}\n\n' \
                f'COUNTER: {COUNTER}\n\n'
    await ctx.send(variables)


@bot.command()
async def start(ctx, study, relax):
    global STUDY

    if ctx.message.channel.id != 866030261341650953:
        await ctx.send('Please use STUDY commands in <#866030261341650953>')
        return

    if STUDY[1]:
        await ctx.send('A study session is already going on!')
        return

    try:
        int(study)
        int(relax)
    except ValueError:
        raise BadArgument(f"Can't convert {study} or {relax} to an integer")

    # asks the setter to enter his task, complete this part later
    await ctx.send('The Journey of the Forever Monke begins with a task. Mine is total world domination, whats yours?')

    def check(m):
        return m.channel == ctx.message.channel and m.author == ctx.author and m.content != '--join'

    try:
        msg = await bot.wait_for('message', timeout=120, check=check)
    except asyncio.TimeoutError:
        await ctx.send('You took longer than 2 minutes to describe your task for this session, come back when you are '
                       'ready to walk the path of the **FOREVER MONKE!!**')
        return
    embed = Embed(
        description=f'```Your goal:\n\n{msg.content}\n\nA timer of {study} minutes of work and {relax} minutes of '
                    f'break has been set```',
        colour=0x1ed9c0)
    await ctx.send(embed=embed)

    task = msg.content
    # send the message and stores it as a clock variable
    countdown = int(study) * 60
    description = "```fix\n" \
                  "Time to get started. MONKE MODE!!\n\nTime left (work) - {}\n```"
    description.format(timedelta(seconds=countdown))
    embed = Embed(description=description.format(timedelta(seconds=countdown)), colour=0x1ed9c0)
    clock = await ctx.send(embed=embed)
    await clock.pin()
    role = ctx.guild.get_role(866357915308785684)
    await ctx.author.add_roles(role)
    nick = ctx.author.name
    newNick = f"[STUDY] {nick}"
    try:
        await ctx.author.edit(nick=newNick)
    except Forbidden:
        pass
    STUDY[2].setdefault(ctx.author, [task, ctx.author.nick])
    STUDY[1] = True
    await asyncio.sleep(15)

    # timer
    while len(STUDY[2].keys()) > 0:
        # this is the part that changes the time
        if countdown > 0:
            countdown -= 5
            description.format(timedelta(seconds=countdown))
            embed = Embed(description=description.format(timedelta(seconds=countdown)), colour=0x1ed9c0)
            await clock.edit(embed=embed)

        # this is the part that switches between break countdown and work countdown
        if countdown == 0:

            # Under the wator alarm
            voice_channel = bot.get_channel(866030210007826453)
            vc = await voice_channel.connect()
            source = FFmpegPCMAudio(source='wator.mp3')
            vc.play(source)
            while vc.is_playing():
                await asyncio.sleep(.1)
            await vc.disconnect()

            if STUDY[1]:
                countdown = int(relax) * 60
                STUDY[1] = False
                description = "```fix\n" \
                              "Its break time, you can chill now, hug a cactus or something\n\nTime left (break) - {" \
                              "}\n``` "

                embed = Embed(description=description.format(timedelta(seconds=countdown)), colour=0x1ed9c0)
                role = ctx.guild.get_role(866357915308785684)
                mentions = ''
                for i in STUDY[2].keys():
                    mentions += i.mention
                    nick = i.name
                    newNick = f"[BREAK] {nick}"
                    try:
                        await i.edit(nick=newNick)
                    except Forbidden:
                        pass
                    await i.remove_roles(role)
                await clock.delete()
                clock = await ctx.send(mentions, embed=embed)
                await clock.pin()
                STUDY[0] += 1

                # asks if they want to change your task
                d = '```'
                for monke in STUDY[2].keys():
                    d += f'{monke.name} : {STUDY[2][monke][0]}\n\n'
                else:
                    d += '```'
                embed = Embed(title='Do you want to change your goal?', description=d, colour=0x1ed9c0)
                embed.set_footer(text='React with a ✅ if you do.')
                message = await ctx.send(embed=embed)
                await message.add_reaction('✅')
                await asyncio.sleep(15)
                message = await ctx.fetch_message(message.id)
                for reaction in message.reactions:
                    if str(reaction) == '✅':
                        user_id = [user.id for user in await reaction.users().flatten()]
                        for monke in STUDY[2].keys():
                            if monke.id in user_id:
                                embed = Embed(
                                    description=f'Your goal is:\n\n{STUDY[2][monke][0]}\n\nWhat do you want to '
                                                f'change it to?', colour=0x1ed9c0)
                                await ctx.send(monke.mention, embed=embed)

                                def check(m):
                                    return m.channel == ctx.message.channel and m.author.id == monke.id \
                                           and m.content != '--join '

                                try:
                                    msg = await bot.wait_for('message', timeout=30, check=check)
                                    STUDY[2][monke][0] = msg.content
                                except asyncio.TimeoutError:
                                    await ctx.send(
                                        f'{monke.mention} you took too long to describe your new goal for this '
                                        f'session, you can change it next session **FOREVER MONKE!!**')

                        else:
                            d = '```'
                            for monke in STUDY[2].keys():
                                d += f'{monke.name} : {STUDY[2][monke][0]}\n\n'
                            else:
                                d += '```'
                            embed = Embed(title='Goals for next round', description=d,
                                          colour=0x1ed9c0)
                            await ctx.send(embed=embed)
                        break
            else:
                countdown = int(study) * 60
                STUDY[1] = True
                STUDY[3] = 0
                description = "```fix\n" \
                              "Play time is over fellow MONKE, now get back to work.\n\nTime left (work) - {}\n```"
                description.format(timedelta(seconds=countdown))
                embed = Embed(description=description.format(timedelta(seconds=countdown)), colour=0x1ed9c0)
                role = ctx.guild.get_role(866357915308785684)
                for i in STUDY[2].keys():
                    nick = i.name
                    newNick = f"[STUDY] {nick}"
                    try:
                        await i.edit(nick=newNick)
                    except Forbidden:
                        pass
                    await i.add_roles(role)
                await clock.delete()
                clock = await ctx.send(role.mention, embed=embed)
                await clock.pin()
        await asyncio.sleep(5)
    else:
        if STUDY[1]:
            minutes = STUDY[0] * int(study) + int(study) - int(countdown / 60)
            STUDY[1] = False
        else:
            minutes = STUDY[0] * int(study)
        await clock.delete()
        description = f'{STUDY[0]} complete sessions and a total of {minutes} minutes of work ' \
                      f'and {STUDY[0] * int(relax)} minutes of break. Come back again, __**FOREVER MONKE!!**__ '
        embed = Embed(description=description, colour=0x1ed9c0)
        embed.set_image(
            url='https://media.discordapp.net/attachments/800004618972037120/867313741293158450/OhMyGodILoveMonkey.png')
        await ctx.send(embed=embed)
        STUDY[0] = 0
        STUDY[3] = 0
        return


@bot.command()
async def leave(ctx):
    global STUDY

    if ctx.message.channel.id != 866030261341650953:
        await ctx.send('Please use STUDY commands in <#866030261341650953>')
        return
    for i in STUDY[2].keys():
        if ctx.author.id == i.id:
            embed = Embed(title='Did you achieve your goal?', description=STUDY[2][i][0], colour=0x1ed9c0)
            message = await ctx.send(ctx.author.mention, embed=embed)
            await message.add_reaction('✅')
            await message.add_reaction('❌')

            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=15,
                                                    check=lambda react, use: use == ctx.author)
                if reaction.emoji == '❌':
                    await ctx.send('The path to Forever Monke is a hard one to navigate, come again at a later time.')
                if reaction.emoji == '✅':
                    await ctx.send(f'Well done! {ctx.author.mention} You are on the path to Forver Monke')
            except asyncio.TimeoutError:
                await ctx.send("Couldn't decide if you succeeded? Nevermind.")

            nick = STUDY[2][i][1]
            try:
                await i.edit(nick=nick)
            except Forbidden:
                pass
            if STUDY[1]:
                role = ctx.guild.get_role(866357915308785684)
                await i.remove_roles(role)
            del STUDY[2][i]
            break
    else:
        return


@bot.command()
async def remindMe(ctx):
    cd = utils.countdown(datetime.strptime(f'2022-01-01 05:30:00', '%Y-%m-%d %H:%M:%S'))
    description = f'**__January 1st 2022__ is __{cd[0]}__ or __{cd[2]} seconds__ or __{cd[1][0] / 30} months__ or __{cd[1][0] / 7}__ weeks away**'
    embed = Embed(description=description, colour=0x1ed9c0)
    embed.set_image(url='https://cdn.discordapp.com/attachments/842796682114498570/876530474472857671/MrM.png')
    await ctx.send(embed=embed)
    return


@bot.command()
async def join(ctx):
    global STUDY
    if ctx.message.channel.id != 866030261341650953:
        await ctx.send('Please use STUDY commands in <#866030261341650953>')
        return

    if ctx.author.id in [i.id for i in STUDY[2].keys()]:
        await ctx.send('You are already a part of the study session')
        return
    if len(STUDY[2].keys()) == 0:
        await ctx.send('You need to start a study session first')
        return
    else:
        await ctx.send(ctx.author.mention + ' what\'s your goal for this session?')

        def check(m):
            return m.channel == ctx.message.channel and m.author == ctx.author and m.content != '--join'

        try:
            msg = await bot.wait_for('message', timeout=120, check=check)
        except asyncio.TimeoutError:
            await ctx.send(
                'You took longer than 2 minutes to describe your goal for this session, come back when you are '
                'ready to walk the path of the **FOREVER MONKE!!**')
            return

        embed = Embed(
            description=f'```Your goal:\n\n{msg.content}\n\nhas been set```',
            colour=0x1ed9c0)
        await ctx.send(embed=embed)

        goal = msg.content
        STUDY[2].setdefault(ctx.author, [goal, ctx.author.nick])
        nick = ctx.author.name
        if STUDY[1]:
            role = ctx.guild.get_role(866357915308785684)
            await ctx.author.add_roles(role)
            newNick = f"[STUDY] {nick}"
        else:
            newNick = f"[BREAK] {nick}"
        try:
            await ctx.author.edit(nick=newNick)
        except Forbidden:
            pass
        return


@bot.command()
async def goal(ctx):
    global STUDY
    for i in STUDY[2].keys():
        if i.id == ctx.author.id:
            await ctx.send(f"{ctx.author.mention} your goal is ```{STUDY[2][i][0]}```")
            return
    else:
        await ctx.send('You haven\'t set a goal yung wan')
        return


@bot.command()
async def counter(ctx):
    user_id = ctx.author.id
    await ctx.send(f"<@{user_id}> you have spoken {COUNTER[user_id]} times since my last reboot.")


@bot.command()
async def ping(ctx):
    latency = bot.latency
    await ctx.send(f'Pong! {round(latency * 1000, 3)} ms')


@bot.command()
async def joke(ctx):
    await ctx.send(await module.joke())


@bot.command()
async def obama(ctx, channel):
    global PUPPET
    if ctx.author.id == 793451663339290644:
        if PUPPET[0]:
            PUPPET[0] = False
            await ctx.send("I am now free")
        else:
            PUPPET = [True, channel]
            await ctx.send(f"I am now being controlled in channel, {bot.get_channel(int(channel))}")
    else:
        await ctx.send(await module.joke())


@bot.command()
async def target(ctx, targeted):
    banned.append(targeted)
    await ctx.send(f'<@{targeted}> successfully targeted chief')


@bot.command()
async def show_target(ctx):
    await ctx.send(banned)


@bot.command()
async def drop(ctx, targeted):
    banned.remove(targeted)
    await ctx.send(f'<@{targeted}> was removed')


@tasks.loop(seconds=5.0)
async def serverStatus():
    global COOLDOWN
    global STUDY
    if COOLDOWN > 0:
        COOLDOWN -= 5.0
    if len(STUDY[2].keys()) == 0 and STUDY[1]:
        await asyncio.sleep(120)
        STUDY[1] = False
    return


bot.run(config.DISCORD_TOKEN)
