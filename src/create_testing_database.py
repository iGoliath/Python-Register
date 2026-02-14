import sqlite3
import os

database_path = "/tmp/RegisterDatabase"

if os.path.exists(database_path):
    os.remove(database_path)

conn = sqlite3.connect('/tmp/RegisterDatabase')
cursor = conn.cursor()

with open('database_commands.txt', 'r') as fp:
    text = fp.read().split("\n")

    for command in text:
        try:
            cursor.execute(command)
        except sqlite3.Error:
            print(sqlite3.Error)

conn.commit()
conn.close()
