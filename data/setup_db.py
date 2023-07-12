import sqlite3

if __name__ == '__main__':
    with open("schema.sql") as file:
        sql = '\n'.join(file.readlines())

    with sqlite3.connect("data.db") as connection:
        connection.executescript(sql)
    print("Done!")
