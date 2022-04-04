import discord
from discord.ext.commands.errors import BadArgument
from discord import Embed, FFmpegPCMAudio
from discord.errors import Forbidden
from datetime import timedelta
from pygicord import Paginator
import databases
from commands import bot
from discord import MessageType
import asyncio
from typing import List, Any
from music import MusiCUNT, Song
import uuid

DATABASE: databases.DataBase

# somebody touch mah spaghetti

# here is the idea there will be a class called self which is in control of the Monke Session, there will be an
# external list called MONKEY_LIST which containes MONKES, members of the monke sessions, The monke session will have
# inbuilt methods start join leave and setBreak and setStudy. The external discord command functions exist to only pass
# on whatever happens to the monke session class.

# TODO: Restructure the monkey list technique to be able to handle multiple sessions,
#  make it an attribute for each session

# TODO: Easy TODOs
#  1. Add a rounds column for the monke table and an increment active rounds for session function to keep track of
#  number of rounds that a specific goal was used for.
#  2. Make the timer setting functions not read and look at the message to set, set it in the constructor
MONKEY_LIST: List[Any] = []


class MonkeSession:
    MONKE_ROLE = None

    def __init__(self, study, break_, channel, rounds=0, clock_id=0, is_break=0, sessionID=None, timer=None):
        self.study = study  # The number of study minutes
        self.break_ = break_  # The number of break minutes
        if timer is None:
            self.timer = self.study * 60  # The amount time that is left
        else:
            self.timer = timer
        self.clock: discord.Message
        self.channel: discord.TextChannel = channel

        if is_break == 0:
            self.is_break = False  # Self explanatory
        else:
            self.is_break = True
        self.rounds = rounds  # Number of complete monke sessions

        self.clock_id = clock_id

        if not self.is_break and self.rounds == 0:
            self.clock_des = (
                "```fix\n"
                "Time to get started. MONKE MODE!!\n\nTime left (work) - {}\n```"
            )
        elif not self.is_break:
            self.clock_des = (
                "```fix\n"
                "Play time is over fellow MONKE, now get back to work.\n\nTime left (work) - {}\n```"
            )
        else:
            self.clock_des = (
                "```fix\n"
                "Its break time, you can chill now, hug a cactus or something\n\nTime left (break) - {"
                "}\n``` "
            )
        # String template for the clock
        if sessionID is None:
            self.sessionID = uuid.uuid1().hex
        else:
            self.sessionID = sessionID

    async def start(self):

        if self.clock_id != 0:
            self.clock = await self.channel.fetch_message(self.clock_id)
        else:
            # creation of the clock if there is no clock already
            self.clock_des.format(timedelta(seconds=self.timer))
            embed = Embed(
                description=self.clock_des.format(timedelta(seconds=self.timer)),
                colour=0x1ED9C0,
            )
            embed.set_footer(text=str(self.timer))
            self.clock = await self.channel.send(embed=embed)
            await self.clock.pin()
            await DATABASE.updateClock(self.clock.id, self.sessionID)

            async for message in self.channel.history(limit=10):
                if message.type is MessageType.pins_add:
                    await message.delete()

        await asyncio.sleep(15)
        while len(MONKEY_LIST) > 0:
            if self.timer > 0:
                self.timer -= 5
                self.clock_des.format(timedelta(seconds=self.timer))
                embed = Embed(
                    description=self.clock_des.format(timedelta(seconds=self.timer)),
                    colour=0x1ED9C0,
                )
                embed.set_footer(text=str(self.timer))
                await self.clock.edit(embed=embed)
                await asyncio.sleep(5)

            if self.timer == 0:

                voice_channel = bot.get_channel(866030210007826453)
                is_playing = False
                for cunt in MusiCUNT.cunts:
                    if cunt.client.channel.guild == voice_channel.guild:
                        is_playing = True
                        under_the_wator = Song("https://youtu.be/z6-FWJteNLI")
                        cunt.playlist.insert(0, under_the_wator)
                        cunt.client.stop()
                        if cunt.is_loop:
                            cunt.playlist.pop(-1)
                        break

                if not is_playing:
                    await alarm(voice_channel)
                if self.is_break:
                    await self.setStudy()
                else:
                    await self.setBreak()
                    await DATABASE.incrementRounds(self.sessionID)
                    self.rounds += 1
                    d = ""
                    for monke in MONKEY_LIST:
                        d += f"```fix\n{monke.nickname} : {monke.goal}```\n"
                    embed = Embed(
                        title="Do you want to change your goal?",
                        description=d,
                        colour=0x1ED9C0,
                    )
                    embed.set_footer(text="Changing your goal marks it as completed.")
                    message = await self.channel.send(embed=embed, delete_after=20)
                    await message.add_reaction("✅")
                    await asyncio.sleep(15)
                    message = await self.channel.fetch_message(message.id)

                    for reaction in message.reactions:
                        if str(reaction) == "✅":
                            user_id = [
                                user.id for user in await reaction.users().flatten()
                            ]
                            for monke in MONKEY_LIST:
                                if monke.member.id in user_id:
                                    await changeGoal(monke, self.channel)
                                    await monke.logComplete()
                    d = ""
                    for monke in MONKEY_LIST:
                        d += f"{monke.member.name} : {monke.goal}\n\n"

                    embed = Embed(
                        title=f"Goals for round {self.rounds + 1}",
                        description=d,
                        colour=0x1ED9C0,
                    )
                    await self.channel.send(embed=embed)

        if not self.is_break:
            minutes = (
                    self.rounds * int(self.study) + int(self.study) - int(self.timer / 60)
            )
        else:
            minutes = self.rounds * int(self.study)

        await self.clock.delete()
        description = (
            f"{self.rounds} complete sessions and a total of {minutes} minutes of work "
            f"and {self.rounds * int(self.break_)} minutes of break. Come back again, __**FOREVER MONKE!!**__ "
        )
        embed = Embed(description=description, colour=0x1ED9C0)
        embed.set_image(
            url="https://media.discordapp.net/attachments/800004618972037120/867313741293158450/OhMyGodILoveMonkey.png"
        )
        # removes the Monke session from the monke table in the DATABASE
        await DATABASE.endSession(self.sessionID)
        await self.channel.send(embed=embed)
        return

    async def setBreak(self):
        """Changes the timer variable and sets all the members of the session to a break state"""
        mentions = ""
        for monke in MONKEY_LIST:
            author = monke.member
            new_nick = f"[BREAK] {author.name}"
            monke.counter = 0
            monke.is_break = True
            await author.remove_roles(MonkeSession.MONKE_ROLE)
            try:
                await author.edit(nick=new_nick)
            except Forbidden:
                pass
            mentions += author.mention

        self.timer = self.break_ * 60
        self.is_break = True
        self.clock_des = (
            "```fix\n"
            "Its break time, you can chill now, hug a cactus or something\n\nTime left (break) - {"
            "}\n``` "
        )

        embed = Embed(
            description=self.clock_des.format(timedelta(seconds=self.timer)),
            colour=0x1ED9C0,
        )
        embed.set_footer(text=self.timer)
        await self.clock.delete()
        self.clock = await self.channel.send(mentions, embed=embed)
        await self.clock.pin()
        await DATABASE.updateClock(self.clock.id, self.sessionID)
        async for message in self.channel.history(limit=10):
            if message.type is MessageType.pins_add:
                await message.delete()

    async def setStudy(self):
        """Changes the timer variable and sets all the members of the session to a Monke state"""
        await self.clock.delete()
        role = self.MONKE_ROLE
        for monke in MONKEY_LIST:
            author = monke.member
            new_nick = f"[STUDY] {author.name}"
            monke.is_break = False
            await author.add_roles(role)
            try:
                await author.edit(nick=new_nick)
            except Forbidden:
                pass

        self.timer = self.study * 60
        self.is_break = False

        self.clock_des = (
            "```fix\n"
            "Play time is over fellow MONKE, now get back to work.\n\nTime left (work) - {}\n```"
        )
        embed = Embed(
            description=self.clock_des.format(timedelta(seconds=self.timer)),
            colour=0x1ED9C0,
        )
        embed.set_footer(text=self.timer)
        self.clock = await self.channel.send(role.mention, embed=embed)
        await self.clock.pin()
        await DATABASE.updateClock(self.clock.id, self.sessionID)
        # gets rid of the system message that says a message was pinned by aternos_cunt
        async for message in self.channel.history(limit=10):
            if message.type is MessageType.pins_add:
                await message.delete()


class Monke:
    def __init__(self, sessionID, member, nick, add2DB=True, goal=None):
        self.nickname = nick
        self.goal = goal
        self.member = member
        self.counter = 0
        self.lite = False
        self.is_break = False
        self.sessionID = sessionID
        if add2DB:
            self.changeGoal(goal)

    def changeGoal(self, new_goal):
        self.goal = new_goal  # this can be modded for Microsoft To Do integration
        asyncio.run_coroutine_threadsafe(
            DATABASE.addMonke(self.sessionID, self.member.id, self.goal, self.nickname), bot.loop
        )

    async def logComplete(self):
        await DATABASE.logComplete(self.goal)

    def __str__(self):
        return f"{self.nickname}, {self.goal}, <@{self.member.id}>"


@bot.command()
async def start(ctx, study, relax):
    if ctx.message.channel.id != 866030261341650953:
        await ctx.send("Please use STUDY commands in <#866030261341650953>")
        return

    if ctx.author.id in [monke.member.id for monke in MONKEY_LIST]:
        await ctx.send("You are already in a monke session")
        return

    try:
        int(study)
        int(relax)
    except ValueError:
        raise BadArgument(f"Can't convert {study} or {relax} to an integer")

    unfinished_goals = await DATABASE.getUserGoals(ctx.author.id)
    if unfinished_goals:
        n = 20
        goalDivisions = [unfinished_goals[i * n: (i + 1) * n] for i in range((len(unfinished_goals) + n - 1) // n)]
        pages = []

        for goalGroup in goalDivisions:
            pills = '\n'.join([f"{goal[0] + 1}. {goal[1]}" for goal in goalGroup])
            embed = Embed(
                description=f"You can pick up where you left off last time.```fix\n{pills}\n``` Set short achievable "
                            f"goals that you can complete in a few sessions. Not **MATHS!!**.",
                colour=0x1ED9C0,
            )
            embed.set_footer(text="Enter a number from the menu to start a session with one of these goals, "
                                  "or just enter a brand new goal.")
            pages.append(embed)

        paginator = Paginator(pages=pages)
        bot.loop.create_task(paginator.start(ctx))
    else:
        await ctx.send("The Journey of the Forever Monke begins with a goal. "
                       "Mine is total world domination, what's yours?")

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

    try:
        goal = unfinished_goals[int(msg.content) - 1][1]
    except ValueError:
        goal = msg.content
    except IndexError:
        await ctx.send("Enter a valid number from the menu.")
        return

    embed = Embed(
        description=f"```Your goal:\n\n{goal}\n\nhas been set```",
        colour=0x1ED9C0,
    )
    await ctx.send(embed=embed)

    Session = MonkeSession(int(study), int(relax), msg.channel)
    await DATABASE.setSession(Session.sessionID, msg.channel.id, msg.channel.guild.id, ctx.author.id, int(relax),
                              int(study), 0)
    MONKEY_LIST.append(Monke(Session.sessionID, ctx.author, ctx.author.nick, goal=goal))

    await ctx.author.add_roles(MonkeSession.MONKE_ROLE)
    newNick = f"[STUDY] {ctx.author.name}"
    try:
        await ctx.author.edit(nick=newNick)
    except Forbidden:
        pass

    bot.loop.create_task(Session.start())
    return


async def alarm(voice_channel):
    vc = await voice_channel.connect()
    source = FFmpegPCMAudio(source="wator.mp3")
    vc.play(source)
    while vc.is_playing():
        await asyncio.sleep(0.1)
    await vc.disconnect()


@bot.command()
async def lite(ctx):
    if ctx.message.channel.id != 866030261341650953:
        await ctx.send("Please use STUDY commands in <#866030261341650953>")
        return

    for monke in MONKEY_LIST:
        if ctx.author.id == monke.member.id:
            monke.lite = not monke.lite
            await ctx.send(
                f"Lite mode set for user {ctx.author.mention} set to {monke.lite}"
            )
            return
    else:
        await ctx.send("You are not in the monke session")
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
                    await monke.logComplete()
            except asyncio.TimeoutError:
                await ctx.send("Couldn't decide if you succeeded? Nevermind.")

            nick = monke.nickname
            try:
                await monke.member.edit(nick=nick)
            except Forbidden:
                pass
            if not monke.is_break:
                await monke.member.remove_roles(MonkeSession.MONKE_ROLE)
            MONKEY_LIST.remove(monke)
            await DATABASE.removeMonke(monke.member.id, monke.sessionID)
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
        await ctx.send("You are already a part of a monke session")
        return

    sessionID = await DATABASE.getAvailableSessions(ctx.guild.id)

    if not sessionID:
        await ctx.send("You need to start a study session first")
        return
    else:
        unfinished_goals = await DATABASE.getUserGoals(ctx.author.id)
        if unfinished_goals:
            n = 20
            goalDivisions = [unfinished_goals[i * n: (i + 1) * n] for i in range((len(unfinished_goals) + n - 1) // n)]
            pages = []

            for goalGroup in goalDivisions:
                pills = '\n'.join([f"{goal[0] + 1}. {goal[1]}" for goal in goalGroup])
                embed = Embed(
                    description=f"You can pick up where you left off last time.```fix\n{pills}\n``` Set short "
                                f"achievable goals that you can complete in a few sessions. Not **MATHS!!**.",
                    colour=0x1ED9C0,
                )
                embed.set_footer(text="Enter a number from the menu to start a session with one of these goals, "
                                      "or just enter a brand new goal.")
                pages.append(embed)

            paginator = Paginator(pages=pages)
            bot.loop.create_task(paginator.start(ctx))
        else:
            await ctx.send("The Journey of the Forever Monke begins with a goal. "
                           "Mine is total world domination, what's yours?")

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

        try:
            goal = unfinished_goals[int(msg.content) - 1][1]
        except ValueError:
            goal = msg.content
        except IndexError:
            await ctx.send("Enter a valid number from the menu.")
            return

        embed = Embed(
            description=f"```Your goal:\n\n{goal}\n\nhas been set```",
            colour=0x1ED9C0,
        )
        await ctx.send(embed=embed)

        MONKEY_LIST.append(Monke(sessionID, ctx.author, ctx.author.nick, goal=goal))
        nick = ctx.author.name
        if not MONKEY_LIST[0].is_break:
            await ctx.author.add_roles(MonkeSession.MONKE_ROLE)
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
            await changeGoal(monke, ctx)
            description = (
                f"{monke.member.mention} your goal was set to:\n\n {monke.goal}."
            )
            embed = Embed(
                description=description,
                colour=0x1ED9C0,
            )
            await ctx.send(embed=embed, delete_after=30)
            break
    else:
        await ctx.send("You have not set a goal yung wan.")


async def changeGoal(monke, channel):
    embed = Embed(
        description=f"Your goal is:\n\n{monke.goal}\n\nWhat do you want to "
                    f"change it to?",
        colour=0x1ED9C0,
    )
    await channel.send(monke.member.mention, embed=embed, delete_after=30)

    def check(m):
        return (
                m.channel.id == channel.id
                and m.author.id == monke.member.id
                and m.content != "--join "
                and len(m.content) < 255
        )

    try:
        msg = await bot.wait_for("message", timeout=30, check=check)
        monke.changeGoal(msg.content)

    except asyncio.TimeoutError:
        await channel.send(
            f"{monke.member.mention} you took too long to describe your new goal for this "
            f"session, you can change it next session **FOREVER MONKE!!**"
        )
