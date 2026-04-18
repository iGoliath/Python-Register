import sqlite3
import os

database_path = "/home/tbc/Desktop/src2/RegisterDatabase"

if os.path.exists(database_path):
    os.remove(database_path)

conn = sqlite3.connect(database_path)
cursor = conn.cursor()

with open('database_commands.txt', 'r') as fp:
    text = fp.read().split("\n")

    for command in text:
        try:
            cursor.execute(command)
        except sqlite3.Error as e:
            print(e)

conn.commit()
conn.close()
