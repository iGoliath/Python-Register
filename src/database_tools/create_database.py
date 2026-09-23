import sqlite3
import os
import sys
from pathlib import Path

def create_database():
    database_path = (Path(__file__).parent / '../python_register/RegisterDatabase')
    if os.path.exists(database_path):
        return False

    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    with open(Path(__file__).parent / 'database_commands.txt') as fp:
        text = fp.read().split("\n")

        for command in text:
            try:
                cursor.execute(command)
            except sqlite3.Error as e:
                print(e)

    conn.commit()
    conn.close()
    return True

def seed_database():
    
    conn = sqlite3.connect((Path(__file__).parent / '../python_register/RegisterDatabase'))
    cursor = conn.cursor()

    with open(Path(__file__).parent / 'example_database_data.txt') as fp:
        commands = fp.read().split("\n")

        for command in commands:
            try:
                cursor.execute(command)
            except sqlite3.Error as e:
                print(e)

    conn.commit()
    conn.close()
