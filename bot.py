import random
from datetime import datetime
import asyncio
from discord import Embed, File
import module
import commands
import utils
from space import apod
import reddit
import config
import monke
import music
import databases
import asyncpg
import meme
from pygicord import Paginator

# ______________________________________________________________________________________________________________________

LOUD = False

# TODO: This nuke launch thing kinda off sucks.
nukeLaunch = [
    "https://c.tenor.com/29eE-n-_4xYAAAAM/atomic-nuke.gif",
    "https://c.tenor.com/Bupb0hg8c-EAAAAM/cat-launch.gif",
    "https://c.tenor.com/xW6YocQ1DokAAAAM/nasa-rocket-launch.gif",
    "https://c.tenor.com/4O7uNcs8vHgAAAAM/rocket-launch.gif",
    "https://c.tenor.com/1s8cZTvNNMsAAAAM/sup-dog.gif",
    "https://c.tenor.com/uGwGAzGhP50AAAAM/shooting-missiles-zeo-zord-i.gif"
    "https://tenor.com/view/star-wars-death-star-laser-gif-9916316",
]
banned = []
explosions = [
    "https://c.tenor.com/BESeHXAH14IAAAAM/little-bit.gif",
    "https://c.tenor.com/CWV41b03zPMAAAAM/jenmotzu.gif",
    "https://c.tenor.com/9n0weQuYRQ8AAAAM/explosion-dragon-ball.gif",
    "https://c.tenor.com/2vTxvF4JV7UAAAAM/blue-planet.gif",
    "https://c.tenor.com/_bbChuywxYsAAAAM/%D0%BF%D0%BB%D0%B0%D0%BD%D0%B5%D1%82%D0%B0-explosion.gif",
    "https://c.tenor.com/lMVdiUIZamcAAAAM/planet-collide-collision.gif",
    "https://c.tenor.com/eM_H-IQfig8AAAAM/fedisbomb-explode.gif",
    "https://c.tenor.com/LRPLtCBu1WYAAAAM/run-bombs.gif",
    "https://c.tenor.com/Rqe9gYz_WPcAAAAM/explosion-boom.gif",
    "https://c.tenor.com/u8jwYAiT_DgAAAAM/boom-bomb.gif",
    "https://c.tenor.com/f0zEg6sf1bsAAAAM/destory-eexplode.gif"
    "https://c.tenor.com/f0zEg6sf1bsAAAAM/destory-eexplode.gif",
    "https://c.tenor.com/jkRrt2SrlMkAAAAM/pepe-nuke.gif",
    "https://c.tenor.com/24gGug50GqQAAAAM/nuke-nuclear.gif",
]
doom = [
    "https://tenor.com/view/crucible-doom-eternal-slayer-video-game-gif-16830152",
    "https://tenor.com/view/doom-logo-doom-video-game-logo-gif-14624225",
    "https://tenor.com/view/doom-eternal-gif-18822003",
    "https://tenor.com/view/doomslayer-doomguy-doom-eternal-seraphimsaber-gif-21010574",
    "https://tenor.com/view/sword-doom-doom-sword-gif-21163712",
    "https://tenor.com/view/destory-eexplode-nuke-gif-6073338",
]

PUPPET = [False, None]
bot = commands.bot
COUNTER = {}


# ______________________________________________________________________________________________________________________
@bot.event
async def on_ready():
    global DATABASE
    global SUS_PINGU

    now = datetime.utcnow()
    current_time = now.strftime("%d/%m/%Y %H:%M:%S")  # starts server
    channel = bot.get_channel(799957897017688065)
    SUS_PINGU = bot.get_channel(858700343113416704)
    # TODO: needs to change
    monke.MonkeSession.MONKE_ROLE = channel.guild.get_role(866357915308785684)
    print(channel)
    print(
        "The bot is logged in as {0.user}".format(bot)
    )  # these variables are going to be used again

    if LOUD:
        APoD = await apod()
        embed = Embed(title=APoD[2], description=APoD[0], colour=0x1ED9C0)
        embed.set_image(url=APoD[1])
        embed.set_footer(text="That's it nothing more " + current_time)
        await channel.send(embed=embed)
        cd = utils.countdown(
            datetime.strptime(f"2022-01-31 18:30:00", "%Y-%m-%d %H:%M:%S")
        )
        description = (
            f"**__February 1st 2022__ was __{cd[0]}__ or __{cd[2]} seconds__ or __{cd[1][0] / 30} months__ "
            f"or __{cd[1][0] / 7}__ weeks ago** "
        )
        embed = Embed(description=description, colour=0x1ED9C0)
        embed.set_image(
            url="https://cdn.discordapp.com/attachments/842796682114498570/876530474472857671/MrM.png"
        )
        await channel.send(embed=embed)

    db = await asyncpg.create_pool(config.DATABASE_URL)
    DATABASE = databases.DataBase(db=db)
    monke.DATABASE = DATABASE

    recoverSession = (
        await DATABASE.recoverSession()
    )  # data recovery in case a monke session gets interrupted

    if recoverSession:
        sessionList = []
        monke.MONKEY_LIST = []
        guildMap = {}

        for session in recoverSession[0]:
            # now we create the sessions:
            channel = bot.get_channel(int(session["channelid"]))
            await channel.send(
                        "```fix\nA monkey session was interrupted, commencing session recovery.```",
                        delete_after=30
                    )
            sessionID = session['sessionid']
            guildMap[sessionID] = channel.guild
            start = session['starttime']
            clockID = session['clock_id']
            break_ = session["breakduration"]
            work = session['workduration']

            # trying to check how many hours have passed.
            elapsed = int(datetime.now().timestamp() - start.timestamp())
            n_rounds, remainder = divmod(elapsed, (work + break_)*60)
            if remainder > work*60:
                is_break = True
                time = break_*60 - remainder
            else:
                is_break = False
                time = work*60 - remainder
            sessionList.append(monke.MonkeSession(work, break_, channel, rounds=n_rounds,
                                                  clock_id=clockID, is_break=is_break,
                                                  sessionID=sessionID, timer=time))
            await channel.send("```fix\nSession recovered, monkey session recreated...```", delete_after=30)

        for simian in recoverSession[1]:
            sessionID = simian['sessionid']
            guild = guildMap[sessionID]
            member = await guild.fetch_member(int(simian['discordid']))
            nick = simian['nick']
            goal = simian['goal']
            print(goal)
            monke.MONKEY_LIST.append(monke.Monke(sessionID, member, nick, False, goal))

        for session in sessionList:
            await session.channel.send("```fix\nThe monkeys were rescued!```", delete_after=30)
            bot.loop.create_task(session.start())


@bot.event
async def on_message(message):
    # this entire function and the whole program in general is a massive fucking mess and my brain calcifies while I try
    # to read this shit, I will fix it later

    if message.author == bot.user:
        return
    # commands
    global PUPPET
    global DATABASE
    global SUS_PINGU
    await bot.process_commands(message)

    # missile program
    if str(message.author.id) in banned:
        explosion = explosions[random.randint(0, len(explosions) - 1)]
        launch = nukeLaunch[random.randint(0, len(nukeLaunch) - 1)]
        if message.attachments or "tenor" in message.content:
            await message.reply(launch)
            await asyncio.sleep(5)
            await message.reply(explosion)
            await asyncio.sleep(5)
            await message.delete()

    # reddit moment
    if (
            len(message.content.split()) == 1
            and "https://www.reddit.com/r/" in message.content
    ):
        data = await reddit.get_image(message.content)
        if data is not None:
            embed = Embed(title=data["title"], url=data["permalink"], colour=0x1ED9C0)
            embed.set_image(url=data["url"])
            embed.set_author(name=message.author.name)
            embed.set_footer(
                text=f'{data["upvotes"]} upvotes in {data["subreddit"]}. {data["ratio"]}% upvote rate.'
            )
            await message.channel.send(embed=embed)
            await message.delete()

    # he asked
    if utils.contains(message.content.lower(), ["who-asked", "who asked"]):
        await message.channel.send("**IT WAS ME! I WAS THE ONE WHO ASKED**")
        dom = doom[random.randint(0, len(doom) - 1)]
        await message.channel.send(dom)

    # ventriloquist
    if (
            message.channel.id == 842796682114498570
            and PUPPET[0]
            and message.content[0:2] != "--"
    ):
        channel = bot.get_channel(int(PUPPET[1]))
        await channel.send(str(message.content))

    # evolve to monke
    if len(monke.MONKEY_LIST) > 0 and not monke.MONKEY_LIST[0].is_break:

        monkey = False
        for m in monke.MONKEY_LIST:
            if m.member.id == message.author.id and not m.lite:
                m.counter += 1
                monkey = m

        if not monkey:
            pass
        else:
            if message.channel.id != 866030261341650953:
                await message.author.send(
                    f"Don't stray from the path to **FOREVER MONKE**. Focus yung wan, you can talk when "
                    "you have a break."
                )
            else:
                if monkey.counter % 12 == 0:
                    await message.channel.send(
                        f"Focus now, don't chit-chat {message.author.mention}, **Forever Monke** is calling."
                    )
                if monkey.counter > 50:
                    await message.channel.send(module.generator("minecraft"))
                    await message.channel.send(
                        explosions[random.randint(0, len(doom) - 1)]
                    )
                    await message.delete()

                elif monkey.counter == 48:
                    await message.channel.send(
                        f"2 more messages from {message.author.mention} and I enter doom "
                        "mode"
                    )

    # clown emoji ban
    if message.author.id == 797152303757000715 and utils.contains(message.content.lower(), ['????', '????', '????']):
        await message.delete()
        await message.channel.send('Shut the fuck up Gayathri, no more ????, ????, ???? emojis for you.', delete_after=30)

    # based on what?
    content = str(message.content)
    if (
            # the message has to be reply to trigger this part, and not a system message
            message.reference is not None
            and not message.is_system()
    ):
        split_content = content.split()
        # the content gets split and depending on what the first word is, one of three things happen
        is_based = (split_content[0].lower() == "based" and len(split_content) == 4)
        is_chad = (split_content[0].lower() == "giga-quote")
        is_cringe = (split_content[0].lower() == "cringe")

        # we find the recipient
        recipient = await message.channel.fetch_message(
            message.reference.message_id
        )
        # the chad-text is whatever the recipient said that was either based or cringe
        chad_text = recipient.content.split()

        # we append the recipients name to the end of their sentence
        chad_text.append('\n-' + str(recipient.author).split("#")[0])

        if message.author.id == recipient.author.id and is_based:
            # cringe bro, calling yourself based??? smh what a normie
            is_based = False
            is_cringe = True
            chad_text = ['somebody', 'pls', 'call', 'me', 'based', 'waaaaaa!!!!']

        if is_based:
            await DATABASE.addPill(split_content[2], recipient.author.id, message.author.id, message.channel.guild.id, message.channel.id)
            await message.channel.send(
                f"{recipient.author.mention} your based counter has increased by 1!"
            )
            # chad_text = ['The', 'based', 'counter', 'is', 'down', 'for', 'maintenance', '\n-clodbot420']
            # is_chad = True

        if (is_based and len(chad_text) <= 50) or is_chad:
            meme.giga_chad(' '.join(chad_text)).save("tmp.jpg")
            if message.channel.guild.id == 797800736599441488 and not is_chad:
                await SUS_PINGU.send(file=File("tmp.jpg"))
            else:
                await message.channel.send(file=File("tmp.jpg"))
        elif is_cringe and len(chad_text) <= 50:
            meme.angrysoyjack(' '.join(chad_text)).save("tmp.jpg")
            await message.channel.send(file=File("tmp.jpg"))

    return


@bot.command()
async def diagnose(ctx):
    variables = (
        f"STUDY : {[str(monk) for monk in monke.MONKEY_LIST]}\n\n"
        f"MUSICUNT: {[str(cunt) for cunt in music.MusiCUNT.cunts]}\n\n"
        f"COUNTER: {COUNTER}\n\n"
    )
    await ctx.send(variables)


@bot.command()
async def remindMe(ctx):
    cd = utils.countdown(datetime.strptime(f"2022-01-31 18:30:00", "%Y-%m-%d %H:%M:%S"))
    description = f"**__February 1st 2022__ was __{cd[0]}__ or __{cd[2]} seconds__ or __{cd[1][0] / 30} months__ or __{cd[1][0] / 7}__ weeks ago**"
    embed = Embed(description=description, colour=0x1ED9C0)
    embed.set_image(
        url="https://cdn.discordapp.com/attachments/842796682114498570/876530474472857671/MrM.png"
    )
    await ctx.send(embed=embed)
    return


@bot.command()
async def counter(ctx):
    user_id = ctx.author.id
    await ctx.send(
        f"<@{user_id}> you have spoken {COUNTER[user_id]} times since my last reboot."
    )


@bot.command()
async def ping(ctx):
    latency = bot.latency
    await ctx.send(f"Pong! {round(latency * 1000, 3)} ms")


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
            await ctx.send(
                f"I am now being controlled in channel, {bot.get_channel(int(channel))}"
            )
    else:
        await ctx.send(await module.joke())


@bot.command()
async def target(ctx, targeted):
    banned.append(targeted)
    await ctx.send(f"<@{targeted}> successfully targeted chief")


@bot.command()
async def show_target(ctx):
    await ctx.send(banned)


@bot.command()
async def drop(ctx, targeted):
    banned.remove(targeted)
    await ctx.send(f"<@{targeted}> was removed")


@bot.command()
async def pills(ctx, author_id=None):
    global DATABASE
    if author_id is None:
        author_id = ctx.author.id
        server = None
    else:
        author_numeric = ""
        for i in author_id:
            if i.isdigit():
                author_numeric += i
        author_id = author_numeric
        server = ctx.guild.id

    pill_list = await DATABASE.getPills(author_id, server=server)
    n = 20
    # the list of pills gets brocken into smaller lists each with n pills in them
    pill_list = [pill_list[i * n: (i + 1) * n] for i in range((len(pill_list) + n - 1) // n)]
    pages = []
    for pillGroup in pill_list:
        pills = '\n'.join(['**'+pill[0]+'**  `'+pill[1]+'`  -<@!'+pill[2]+'>' for pill in pillGroup])
        embed = Embed(
            description=f"<@!{author_id}>'s pills:\n\n{pills}",
            colour=0x1ED9C0,
        )
        pages.append(embed)

    paginator = Paginator(pages=pages)
    await paginator.start(ctx)


@bot.command()
async def pillsGiven(ctx, author_id=None):
    global DATABASE
    if author_id is None:
        author_id = ctx.author.id
        server = None
    else:
        author_numeric = ""
        for i in author_id:
            if i.isdigit():
                author_numeric += i
        author_id = author_numeric
        server = ctx.guild.id

    pill_list = await DATABASE.getPillsGiven(author_id, server=server)
    n = 20
    # the list of pills gets brocken into smaller lists each with n pills in them
    pill_list = [pill_list[i * n: (i + 1) * n] for i in range((len(pill_list) + n - 1) // n)]
    pages = []
    for pillGroup in pill_list:
        pills = '\n'.join(['**'+pill[0]+'**  `'+pill[1]+'`  -<@!'+pill[2]+'>' for pill in pillGroup])
        embed = Embed(
            description=f"<@!{author_id}>'s pills:\n\n{pills}",
            colour=0x1ED9C0,
        )
        pages.append(embed)

    paginator = Paginator(pages=pages)
    await paginator.start(ctx)


print("Starting bot...")
bot.run(config.DISCORD_TOKEN)
