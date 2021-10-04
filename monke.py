from discord.ext.commands.errors import BadArgument
from discord import Embed, FFmpegPCMAudio
from discord.errors import Forbidden
from datetime import timedelta
from commands import bot
import asyncio
from typing import List, Any


class Monke:
    timer = 0  # Time to be displayed on the clock
    break_ = 0  # Break time duration
    study = 0  # Study time duration
    is_break = True
    rounds = 0  # number of monke sessions
    clock = None  # The clock
    clock_des = None
    counter = 0

    channel = None
    MONKE_ROLE = None

    def __init__(self, nick, goal, member):
        self.nickname = nick
        self.goal = goal
        self.member = member

    def changeGoal(self, new_goal):
        self.goal = new_goal  # this can be modded for Microsoft To Do integration


MONKEY_LIST: List[Any] = []


@bot.command()
async def start(ctx, study, relax):
    if ctx.message.channel.id != 866030261341650953:
        await ctx.send("Please use STUDY commands in <#866030261341650953>")
        return

    if ctx.author.id in [monke.member.id for monke in MONKEY_LIST]:
        await ctx.send("You are already in a monke session")

    try:
        int(study)
        int(relax)
    except ValueError:
        raise BadArgument(f"Can't convert {study} or {relax} to an integer")

    await ctx.send(
        "The Journey of the Forever Monke begins with a goal. Mine is total world domination, what's yours?"
    )

    def check(m):
        return (
            m.channel == ctx.message.channel
            and m.author == ctx.author
            and m.content != "--join"
        )

    try:
        msg = await bot.wait_for("message", timeout=120, check=check)
    except asyncio.TimeoutError:
        await ctx.send(
            "You took longer than 2 minutes to describe your goal for this session, come back when you are "
            "ready to walk the path of the **FOREVER MONKE!!**"
        )
        return

    MONKEY_LIST.append(Monke(ctx.author.nick, msg.content, ctx.author))

    # timer settings
    Monke.break_ = int(relax) * 60
    Monke.study = int(study) * 60
    Monke.timer = Monke.study
    Monke.is_break = False

    # Confirmation of Goal
    embed = Embed(
        description=f"```Your goal:\n\n{msg.content}\n\nA timer of {study} minutes of work and {relax} minutes of "
        f"break has been set```",
        colour=0x1ED9C0,
    )
    await ctx.send(embed=embed)

    Monke.clock_des = (
        "```fix\n" "Time to get started. MONKE MODE!!\n\nTime left (work) - {}\n```"
    )
    Monke.clock_des.format(timedelta(seconds=Monke.timer))
    embed = Embed(
        description=Monke.clock_des.format(timedelta(seconds=Monke.timer)),
        colour=0x1ED9C0,
    )

    # creation of the clock
    Monke.clock = await ctx.send(embed=embed)
    await Monke.clock.pin()

    await asyncio.sleep(15)
    while len(MONKEY_LIST) > 0:
        if Monke.timer > 0:
            Monke.timer -= 5
            Monke.clock_des.format(timedelta(seconds=Monke.timer))
            embed = Embed(
                description=Monke.clock_des.format(timedelta(seconds=Monke.timer)),
                colour=0x1ED9C0,
            )
            await Monke.clock.edit(embed=embed)
            await asyncio.sleep(5)

        if Monke.timer == 0:

            voice_channel = bot.get_channel(866030210007826453)
            vc = await voice_channel.connect()
            source = FFmpegPCMAudio(source="wator.mp3")
            vc.play(source)
            while vc.is_playing():
                await asyncio.sleep(0.1)
            await vc.disconnect()

            if Monke.is_break:
                await setStudy()
            else:
                await setBreak()
                Monke.rounds += 1
                d = ""
                for monke in MONKEY_LIST:
                    d += f"{monke.nickname} : {monke.goal}\n\n"
                embed = Embed(
                    title="Do you want to change your goal?",
                    description=d,
                    colour=0x1ED9C0,
                )
                embed.set_footer(text="React with a ✅ if you do.")
                message = await ctx.send(embed=embed)
                await message.add_reaction("✅")
                await asyncio.sleep(15)
                message = await ctx.fetch_message(message.id)

                for reaction in message.reactions:
                    if str(reaction) == "✅":
                        user_id = [user.id for user in await reaction.users().flatten()]
                        for monke in MONKEY_LIST:
                            if monke.member.id in user_id:
                                await changeGoal(monke=monke)

                d = ""
                for monke in MONKEY_LIST:
                    d += f"{monke.member.name} : {monke.goal}\n\n"

                embed = Embed(
                    title="Goals for next round",
                    description=d,
                    colour=0x1ED9C0,
                )
                await ctx.send(embed=embed)

    if not Monke.is_break:
        minutes = Monke.rounds * int(study) + int(study) - int(Monke.timer / 60)
    else:
        minutes = Monke.rounds * int(study)

    await Monke.clock.delete()
    description = (
        f"{Monke.rounds} complete sessions and a total of {minutes} minutes of work "
        f"and {Monke.rounds * int(relax)} minutes of break. Come back again, __**FOREVER MONKE!!**__ "
    )
    embed = Embed(description=description, colour=0x1ED9C0)
    embed.set_image(
        url="https://media.discordapp.net/attachments/800004618972037120/867313741293158450/OhMyGodILoveMonkey.png"
    )
    await ctx.send(embed=embed)
    Monke.rounds = 0
    Monke.counter = 0
    return


@bot.command()
async def leave(ctx):
    if ctx.message.channel.id != 866030261341650953:
        await ctx.send("Please use STUDY commands in <#866030261341650953>")
        return

    for monke in MONKEY_LIST:
        if ctx.author.id == monke.member.id:
            embed = Embed(
                title="Did you achieve your goal?",
                description=monke.goal,
                colour=0x1ED9C0,
            )
            message = await ctx.send(ctx.author.mention, embed=embed)
            await message.add_reaction("✅")
            await message.add_reaction("❌")

            try:
                reaction, user = await bot.wait_for(
                    "reaction_add",
                    timeout=15,
                    check=lambda react, use: use == ctx.author,
                )
                if reaction.emoji == "❌":
                    await ctx.send(
                        "The path to Forever Monke is a hard one to navigate, come again at a later time."
                    )
                if reaction.emoji == "✅":
                    await ctx.send(
                        f"Well done! {ctx.author.mention} You are on the path to Forver Monke"
                    )
            except asyncio.TimeoutError:
                await ctx.send("Couldn't decide if you succeeded? Nevermind.")

            nick = monke.nickname
            try:
                await monke.member.edit(nick=nick)
            except Forbidden:
                pass
            if not Monke.is_break:
                role = ctx.guild.get_role(866357915308785684)
                await monke.member.remove_roles(role)
            MONKEY_LIST.remove(monke)
            del monke
            break
    else:
        return


@bot.command()
async def join(ctx):
    if ctx.message.channel.id != 866030261341650953:
        await ctx.send("Please use STUDY commands in <#866030261341650953>")
        return

    if ctx.author.id in [monke.member.id for monke in MONKEY_LIST]:
        await ctx.send("You are already a part of the study session")
        return
    if len(MONKEY_LIST) == 0:
        await ctx.send("You need to start a study session first")
        return
    else:
        await ctx.send(ctx.author.mention + " what's your goal for this session?")

        def check(m):
            return (
                m.channel == ctx.message.channel
                and m.author == ctx.author
                and m.content != "--join"
            )

        try:
            msg = await bot.wait_for("message", timeout=120, check=check)
        except asyncio.TimeoutError:
            await ctx.send(
                "You took longer than 2 minutes to describe your goal for this session, come back when you are "
                "ready to walk the path of the **FOREVER MONKE!!**"
            )
            return

        embed = Embed(
            description=f"```Your goal:\n\n{msg.content}\n\nhas been set```",
            colour=0x1ED9C0,
        )
        await ctx.send(embed=embed)

        MONKEY_LIST.append(Monke(ctx.author.nick, msg.content, ctx.author))
        nick = ctx.author.name
        if not Monke.is_break:
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
async def change_goal(ctx):
    if ctx.message.channel.id != 866030261341650953:
        await ctx.send("Please use STUDY commands in <#866030261341650953>")
        return

    for monke in MONKEY_LIST:
        if monke.member.id == ctx.author.id:
            await changeGoal(monke)
            description = f"{monke.member.mention} your goal was set to:\n\n {monke.goal}."
            embed = Embed(
                description=description,
                colour=0x1ED9C0,
            )
            await ctx.send(embed=embed)
            break
    else:
        await ctx.send("You have not set a goal yung wan.")


async def setStudy():
    """Changes the timer variable and sets all the members of the session to a Monke state"""
    await Monke.clock.delete()
    role = Monke.MONKE_ROLE
    for monke in MONKEY_LIST:
        author = monke.member
        new_nick = f"[STUDY] {author.name}"

        await author.add_roles(role)
        try:
            await author.edit(nick=new_nick)
        except Forbidden:
            pass

    Monke.timer = Monke.study
    Monke.is_break = False

    Monke.clock_des = (
        "```fix\n"
        "Play time is over fellow MONKE, now get back to work.\n\nTime left (work) - {}\n```"
    )
    Monke.clock_des.format(timedelta(seconds=Monke.timer))
    embed = Embed(
        description=Monke.clock_des.format(timedelta(seconds=Monke.timer)),
        colour=0x1ED9C0,
    )

    Monke.clock = await Monke.channel.send(role.mention, embed=embed)
    await Monke.clock.pin()


async def setBreak():
    """Changes the timer variable and sets all the members of the session to a break state"""
    mentions = ""
    for monke in MONKEY_LIST:
        author = monke.member
        new_nick = f"[BREAK] {author.name}"

        await author.remove_roles(Monke.MONKE_ROLE)
        try:
            await author.edit(nick=new_nick)
        except Forbidden:
            pass
        mentions += author.mention

    Monke.timer = Monke.break_
    Monke.is_break = True
    Monke.counter = 0
    Monke.clock_des = (
        "```fix\n"
        "Its break time, you can chill now, hug a cactus or something\n\nTime left (break) - {"
        "}\n``` "
    )

    embed = Embed(
        description=Monke.clock_des.format(timedelta(seconds=Monke.timer)),
        colour=0x1ED9C0,
    )

    await Monke.clock.delete()
    Monke.clock = await Monke.channel.send(mentions, embed=embed)
    await Monke.clock.pin()


async def changeGoal(monke):
    embed = Embed(
        description=f"Your goal is:\n\n{monke.goal}\n\nWhat do you want to "
        f"change it to?",
        colour=0x1ED9C0,
    )
    await Monke.channel.send(monke.member.mention, embed=embed)

    def check(m):
        return (
            m.channel == Monke.channel
            and m.author.id == monke.member.id
            and m.content != "--join "
        )

    try:
        msg = await bot.wait_for("message", timeout=30, check=check)
        monke.changeGoal(msg.content)

    except asyncio.TimeoutError:
        await Monke.channel.send(
            f"{monke.member.mention} you took too long to describe your new goal for this "
            f"session, you can change it next session **FOREVER MONKE!!**"
        )
