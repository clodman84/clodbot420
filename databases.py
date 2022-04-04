
class DataBase:
    def __init__(self, db):
        self.db: asyncpg.pool.Pool = db

    async def management(self, query):
        connection = await self.db.acquire()
        async with connection.transaction():
            data = await connection.execute(query)
        await self.db.release(connection)
        return data

    async def addPill(self, pill, receiver, sender, server, channel):
        connection = await self.db.acquire()
        async with connection.transaction():
            pill.replace("`", "")   # no quotes allowed.
            pill.replace('"', "")
            data = await connection.execute(
                f"insert into pills (id, pill, receiver, sender, server, channel) "
                f"values (DEFAULT,'{pill}','{receiver}','{sender}','{server}','{channel}');"
            )
        await self.db.release(connection)
        return data

    async def getPills(self, author_id, server):
        if server is not None:
            data = await self.db.fetch(f"SELECT pill, sender FROM pills "
                                       f"WHERE (receiver = '{author_id}' and server = '{server}')")
        else:
            data = await self.db.fetch(f"SELECT pill, sender FROM pills WHERE receiver = '{author_id}'")

        if len(data) > 0:
            return [(str(index+1), i["pill"], i["sender"]) for index, i in enumerate(data)]
        else:
            return ["wow such empty, you are not based in this server yet"]

    async def getPillsGiven(self, author_id, server):
        if server is not None:
            data = await self.db.fetch(f"SELECT pill, receiver FROM pills "
                                       f"WHERE (sender = '{author_id}' and server = '{server}')")
        else:
            data = await self.db.fetch(f"SELECT pill, receiver FROM pills WHERE sender = '{author_id}'")

        if len(data) > 0:
            return [(str(index+1), i["pill"], i["receiver"]) for index, i in enumerate(data)]
        else:
            return ["wow such empty, you are not based in this server yet"]

    async def getAllPills(self):
        data = await self.db.fetch(f"SELECT * FROM pills")
        return data

    async def getUserGoals(self, discordid):
        data = await self.db.fetch(f"select distinct goal from monke "
                                   f"where complete = false and discordid='{discordid}'")
        if data:
            data = [[index, goal["goal"]] for index, goal in enumerate(data)]
        return data

    async def addMonke(self, sessionID, authorID, goal, nick):
        # called during the __init__ of a Monke
        # and also when the monke changes its goal, whether, there is a bool val
        print(f"Trying to add monke - {authorID} to session - {sessionID}")
        connection = await self.db.acquire()
        async with connection.transaction():
            query = f"UPDATE monke set active = FALSE where sessionID = '{sessionID}' and discordid = '{authorID}';"
            await connection.execute(
                # turn off all the active goals in the session by this author and then add another row
                query
            )
            query = f"INSERT INTO monke (sessionID, discordID, goal, nick, complete) " \
                    f"VALUES('{sessionID}','{authorID}', '{goal}', '{nick}', false);"
            data = await connection.execute(
                query
            )
        print("Monkey Added!")
        await self.db.release(connection)
        return data

    async def removeMonke(self, authorID, sessionID):
        # called during the leave command
        print("Monkey Removed")
        connection = await self.db.acquire()
        async with connection.transaction():
            data = await connection.execute(
                f"UPDATE monke set active = FALSE where discordid = '{authorID}' and sessionID = '{sessionID}'"
            )
        await self.db.release(connection)
        return data

    async def endSession(self, sessionID):
        # called during the end of a MonkeSession.start() the id_ of a monkey session is Monke
        connection = await self.db.acquire()
        async with connection.transaction():
            data = await connection.execute(
                f"UPDATE monkesessions SET endtime = current_timestamp WHERE sessionID = '{sessionID}';"
            )
        await self.db.release(connection)
        return data

    async def setSession(self, sessionID, channelID, serverID, starterID, break_ , study, clock_id):
        # called during the __init__ of a MonkeSession
        print("Setting Session...")
        connection = await self.db.acquire()
        async with connection.transaction():
            data = await connection.execute(
                f"INSERT INTO MonkeSessions "
                f"(sessionID,channelID, serverid, starterid, starttime, breakduration, workduration, clock_id) "
                f"VALUES('{sessionID}', '{channelID}','{serverID}','{starterID}', "
                f"current_timestamp, {break_}, {study}, '{clock_id}');"
            )
        await self.db.release(connection)
        print(f"Session - {sessionID} has been set!")
        return data

    async def getAvailableSessions(self, serverID):
        data = await self.db.fetchrow(f"SELECT sessionID from monkesessions "
                                      f"where serverID = '{serverID}' and endtime is null")
        if data is None:
            return False
        else:
            return data['sessionid']

    async def updateClock(self, clock_id, sessionID):
        # called in MonkeSession.start() to increment the number of rounds
        print(f"Trying to update clock_id to {clock_id} to session - {sessionID}")
        connection = await self.db.acquire()
        async with connection.transaction():
            query = f"UPDATE MonkeSessions set clock_id = '{clock_id}' WHERE sessionID = '{sessionID}';"
            print(query)
            data = await connection.execute(
                query
            )
        print("Clock Updated!")
        await self.db.release(connection)
        return data

    async def incrementRounds(self, sessionID):
        connection = await self.db.acquire()
        async with connection.transaction():
            query = f"UPDATE monke set rounds = rounds + 1 where sessionid = '{sessionID}'"
            data = await connection.execute(query)
        await self.db.release(connection)
        return data

    async def recoverSession(self):
        session_data = await self.db.fetch("SELECT * FROM monkesessions where endtime is null")
        if not session_data:
            return False
        else:
            monkey_data = await self.db.fetch("SELECT * FROM monke where active = true")
            return session_data, monkey_data

    async def logComplete(self, goal):
        # marks all the goals with the same name as complete
        connection = await self.db.acquire()
        async with connection.transaction():
            query = f"UPDATE monke set complete = true where goal = '{goal}' "
            data = await connection.execute(query)
        await self.db.release(connection)
        return data


async def setup():
    # This function is an entry point for me to do some database management and checkups etc, it's bad, but it works

    db = await asyncpg.create_pool(config.DATABASE_URL)
    DATABASE = DataBase(db=db)
    # query = """CREATE TABLE pills (
    #     id serial primary key,
    #     pill varchar(128) not null,
    #     receiver char(18) not null,
    #     sender char(18) not null,
    #     server char(18) not null,
    #     channel char(18) not null,
    #     pillDate date not null default current_date
    # );"""
    query = "select * from monke"
    data = await DATABASE.getUserGoals("793451663339290644")
    print(data)


if __name__ == '__main__':
    import asyncpg
    import config
    import asyncio
    asyncio.get_event_loop().run_until_complete(setup())
