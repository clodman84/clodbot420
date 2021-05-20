import sqlite3 as sql

mycon = sql.connect('data.db')
cursor = mycon.cursor()
cursor.execute(f'update users set daily = 0 where userID = "clodman84#1215"')
mycon.commit()
for row in cursor.execute("select * from users"):
    print(row)