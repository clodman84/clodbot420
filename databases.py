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
        return data['pills']

    async def getAllPills(self):
        data = await self.db.fetch(f"SELECT * FROM based_counter")
        return data
