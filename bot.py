import random
from datetime import datetime
import asyncio
from discord import Embed
from discord.ext import tasks
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

# ______________________________________________________________________________________________________________________

LOUD = True
COOLDOWN = 3600
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
    monke.Monke.channel = bot.get_channel(866030261341650953)
    now = datetime.utcnow()
    current_time = now.strftime("%d/%m/%Y %H:%M:%S")  # starts server
    channel = bot.get_channel(799957897017688065)
    monke.Monke.MONKE_ROLE = channel.guild.get_role(866357915308785684)
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
        description = f"**__February 1st 2022__ is __{cd[0]}__ or __{cd[2]} seconds__ or __{cd[1][0] / 30} months__ " \
                      f"or __{cd[1][0] / 7}__ weeks away** "
        embed = Embed(description=description, colour=0x1ED9C0)
        embed.set_image(
            url="https://cdn.discordapp.com/attachments/842796682114498570/876530474472857671/MrM.png"
        )
        await channel.send(embed=embed)
    db = await asyncpg.create_pool(config.DATABASE_URL)
    DATABASE = databases.DataBase(db=db)
    serverStatus.start()


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    # commands
    global COOLDOWN
    global PUPPET
    global COUNTER
    global DATABASE
    await bot.process_commands(message)
    if str(message.author.id) in banned:
        explosion = explosions[random.randint(0, len(explosions) - 1)]
        launch = nukeLaunch[random.randint(0, len(nukeLaunch) - 1)]
        if message.attachments or "tenor" in message.content:
            await message.reply(launch)
            await asyncio.sleep(5)
            await message.reply(explosion)
            await asyncio.sleep(5)
            await message.delete()

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

    if utils.contains(message.content.lower(), ["who-asked", "who asked"]):
        await message.channel.send("**IT WAS ME! I WAS THE ONE WHO ASKED**")
        dom = doom[random.randint(0, len(doom) - 1)]
        await message.channel.send(dom)

    if (
        message.channel.id == 842796682114498570
        and PUPPET[0]
        and message.content[0:2] != "--"
    ):
        channel = bot.get_channel(int(PUPPET[1]))
        await channel.send(str(message.content))

    if not monke.Monke.is_break and message.author.id in [
        monkey.member.id for monkey in monke.MONKEY_LIST
    ]:
        monke.Monke.counter += 1
        if message.channel.id != 866030261341650953:
            await message.author.send(
                f"Don't stray from the path to **FOREVER MONKE**. Focus yung wan, you can talk when "
                "you have a break."
            )
        else:
            if monke.Monke.counter % 12 == 0:
                await message.channel.send(
                    "Focus now, don't chit-chat, **Forever Monke** is calling."
                )
        if monke.Monke.counter > 50:
            await message.channel.send(module.generator("minecraft"))
            await message.channel.send(explosions[random.randint(0, len(doom) - 1)])
            await message.delete()
        elif monke.Monke.counter == 48:
            await message.channel.send(
                "2 more messages from those who are supposed to be studying, and I enter doom "
                "mode"
            )

    author = message.author
    content = str(message.content)
    if (
        message.reference is not None
        and not message.is_system()
        and len(content.split()) == 4
    ):
        content = content.split()
        if content[0].lower() == "based":
            recipient = await message.channel.fetch_message(
                message.reference.message_id
            )
            await DATABASE.addPill(str(recipient.author.id), '"' + content[2] + '"')
            await message.channel.send(
                f"{recipient.author.mention} your based counter has increased by 1!"
            )

    if author.id not in COUNTER:
        COUNTER.setdefault(author.id, 0)
    else:
        COUNTER[author.id] += 1

    if message.channel.id == 858700343113416704:
        if not utils.contains(message.content.lower(), ["sus", "s u s"]):
            embed = Embed(
                description=f"**<@{message.author.id}> You sussy bitch, breaking the sus rule, no sus in your "
                f"sentence:**\n\n{content}",
                colour=0x1ED9C0,
            )
            embed.set_footer(text=module.generator("sites"))
            await message.channel.send(embed=embed)
            await message.delete()
    if message.channel.category.id != 860176783755313182 and (
        utils.contains(message.content.lower(), [":lewd", "hentai", "ecchi", "l e w d"])
        or message.author.id in [337481187419226113, 571027211407196161]
    ):
        dom = doom[random.randint(0, len(doom) - 1)]
        await message.channel.send(dom)
        await message.delete()
    if (
        message.attachments
        or utils.contains(content, ["/", "%", ":", "http", "--"])
        or message.reference
    ):
        return
    elif (
        (COUNTER[author.id]) % 50 == 0
        and COOLDOWN == 0
        and len(content) <= 2048
        and not message.author.bot
    ):
        Text = await module.translate(message.content, str(author))
        embed = Embed(description="*" + Text[0] + "*", colour=0x1ED9C0)
        embed.set_footer(text="-" + Text[1])
        if Text[2] == 200:
            await message.channel.send(embed=embed)
            await message.delete()
        if Text[1][-4:] == "CUNT":
            COOLDOWN = 3600
    return


@bot.command()
async def diagnose(ctx):
    variables = (
        f"STUDY : {[str(monk) for monk in monke.MONKEY_LIST]}\n\n"
        f"MUSICUNT: {[str(cunt) for cunt in music.MusiCUNT.cunts]}\n\n"
        f"COOLDOWN: {COOLDOWN}\n\n"
        f"COUNTER: {COUNTER}\n\n"
    )
    await ctx.send(variables)


@bot.command()
async def remindMe(ctx):
    cd = utils.countdown(datetime.strptime(f"2022-01-31 18:30:00", "%Y-%m-%d %H:%M:%S"))
    description = f"**__February 1st 2022__ is __{cd[0]}__ or __{cd[2]} seconds__ or __{cd[1][0] / 30} months__ or __{cd[1][0] / 7}__ weeks away**"
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
    else:
        author_numeric = ''
        for i in author_id:
            if i.isdigit():
                author_numeric += i
        author_id = author_numeric

    pill_list = await DATABASE.getPills(str(author_id))
    await ctx.send(
        embed=Embed(
            description=f"<@!{author_id}>\n```css\n{pill_list}```",
            colour=0x1ED9C0,
        )
    )
    return


@tasks.loop(seconds=5.0)
async def serverStatus():
    global COOLDOWN
    if COOLDOWN > 0:
        COOLDOWN -= 5.0
    if len(monke.MONKEY_LIST) == 0 and not monke.Monke.is_break:
        await asyncio.sleep(120)
        monke.Monke.is_break = True
    return


bot.run(config.DISCORD_TOKEN)
