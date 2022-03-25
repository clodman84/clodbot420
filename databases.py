import pprint

class DataBase:
    def __init__(self, db):
        self.db = db

    async def registerBased(self, author_id, pill):
        connection = await self.db.acquire()
        async with connection.transaction():
            data = await self.db.execute(
                f"INSERT INTO based_counter VALUES('{author_id}', '{'{' + pill + '}'}');"
            )
        await self.db.release(connection)
        return data

    async def addPill(self, author_id, pill):
        connection = await self.db.acquire()
        async with connection.transaction():
            pill.replace("`", "")
            pill.replace('"', "")
            data = await self.db.execute(
                f"UPDATE based_counter set pills = pills || '{'{' + pill + '}'}' WHERE id = '{author_id}';"
            )
            if data.split()[-1] == "0":
                data = await self.registerBased(author_id, pill)
        await self.db.release(connection)
        return data

    async def getPills(self, author_id):
        data = await self.db.fetchrow(
            f"SELECT pills FROM based_counter WHERE id = '{author_id}'"
        )
        try:
            return data["pills"]
        except TypeError:
            return ["wow such empty, you are not based yet"]

    async def getAllPills(self):
        data = await self.db.fetch(f"SELECT * FROM based_counter")
        return data

    async def createMonkeTable(self):
        connection = await self.db.acquire()
        async with connection.transaction():
            data = await self.db.execute(
                "DROP TABLE Monkeys;"
                "CREATE TABLE Monkeys (id_ varchar, goal varchar, nick varchar);"
            )
        await self.db.release(connection)
        return data

    async def addMonke(self, author_id, goal, nick):
        print("Monkey Added")
        # called during the __init__ of a Monke
        connection = await self.db.acquire()
        async with connection.transaction():
            data = await self.db.execute(
                f"INSERT INTO Monkeys VALUES('{author_id}', '{goal}', '{nick}');"
            )
        await self.db.release(connection)
        return data

    # The monke functions
    async def setGoal(self, author_id, goal):
        # called during monke.changeGoal()
        connection = await self.db.acquire()
        async with connection.transaction():
            data = await self.db.execute(
                f"UPDATE Monkeys set goal = '{goal}' WHERE id_ = '{author_id}';"
            )
        await self.db.release(connection)
        return data

    async def removeMonke(self, author_id):
        # called during the leave command
        print("Monkey Removed")
        connection = await self.db.acquire()
        async with connection.transaction():
            data = await self.db.execute(
                f"DELETE FROM Monkeys WHERE id_ = '{author_id}';"
            )
        await self.db.release(connection)
        return data

    async def createMonkeSession(self):
        connection = await self.db.acquire()
        async with connection.transaction():
            data = await self.db.execute(
                "DROP TABLE MonkeSession; "
                "CREATE TABLE MonkeSession (id_ varchar, study int, break int, rounds int, clock_id varchar, is_break int);"
            )
        await self.db.release(connection)
        return data

    async def clearSession(self):
        # called during the end of a MonkeSession.start() the id_ of a monkey session is Monke
        connection = await self.db.acquire()
        async with connection.transaction():
            data = await self.db.execute(
                f"DELETE FROM MonkeSession WHERE id_ = 'Monke';"
            )
        await self.db.release(connection)
        return data

    async def setSession(self, study, break_, rounds, clock_id, is_break):
        # called during the __init__ of a MonkeSession
        connection = await self.db.acquire()
        async with connection.transaction():
            data = await self.db.execute(
                f"INSERT INTO MonkeSession VALUES('Monke', {study}, {break_}, {rounds}, '{clock_id}', {is_break});"
            )
        await self.db.release(connection)
        return data

    async def incrementRounds(self):
        # called in MonkeSession.start() to increment the number of rounds
        connection = await self.db.acquire()
        async with connection.transaction():
            data = await self.db.execute(
                f"UPDATE MonkeSession set rounds = rounds + 1 WHERE id_ = 'Monke';"
            )
        await self.db.release(connection)
        return data

    async def updateClock(self, clock_id, is_break):
        # called in MonkeSession.start() to increment the number of rounds
        connection = await self.db.acquire()
        async with connection.transaction():
            data = await self.db.execute(
                f"UPDATE MonkeSession set clock_id = '{clock_id}' WHERE id_ = 'Monke';"
            )
            await self.db.execute(
                f"UPDATE MonkeSession set is_break = {is_break} WHERE id_ = 'Monke';"
            )
        await self.db.release(connection)
        return data

    async def recoverSession(self):
        # called when bot on_ready() to get details for any incomplete sessions if none are found, it returns False
        session_data = await self.db.fetchrow("SELECT * FROM MonkeSession")
        if session_data is None:
            return False
        else:
            monkeyData = await self.db.fetch("SELECT * FROM Monkeys")
            return session_data, monkeyData


async def setup():
    # This function is an entry point for me to do some database management and checkups etc, it's bad, but it works
    db = await asyncpg.create_pool(config.DATABASE_URL)
    DATABASE = DataBase(db=db)
    pills = await DATABASE.getAllPills()
    # [[pillID, pillData, pillReceiver, pillSender, serverID, channelID, time]]
    newStructure = []
    count = 1
    for user in pills:
        for pill in user["pills"]:
            data = [None]*7
            data[0] = count
            data[1] = pill
            data[2] = user["id"]
            newStructure.append(data)
            count += 1
    pprint.pprint(newStructure)

if __name__ == '__main__':
    import asyncpg
    import config
    import asyncio
    asyncio.get_event_loop().run_until_complete(setup())
