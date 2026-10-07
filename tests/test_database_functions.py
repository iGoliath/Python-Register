import json
import os
import sqlite3
from pathlib import Path

from database_tools.create_config_json import create_config_json
from database_tools.create_database import create_database, seed_database

database_path = Path(__file__).parent / "TestsRegisterDatabase"
config_path = Path(__file__).parent / "Testsconfig.json"


def test_create_database():
    """Database should successfully create if it doesn't already exist."""
    if os.path.exists(database_path):
        os.remove(database_path)
    assert not os.path.exists(database_path)
    create_database(database_path)
    assert os.path.exists(database_path)
    os.remove(database_path)


def test_database_schema():
    """Schema should match that in src/database_tools/database_commands.txt"""
    if os.path.exists(database_path):
        os.remove(database_path)
    create_database(database_path)
    with open(
        Path(__file__).parent / "../src/database_tools/database_commands.txt", "r"
    ) as file:
        lines = file.read().splitlines()
    conn = sqlite3.connect(database_path)
    c = conn.cursor()
    c.execute(
        "SELECT sql FROM sqlite_master where sql IS NOT NULL AND tbl_name != 'sqlite_sequence'"
    )
    database_commands = [row[0] for row in c.fetchall()]
    assert lines == database_commands
    os.remove(database_path)


def test_create_database_already_exists():
    """Database creation should fail if it already exists."""
    if not os.path.exists(database_path):
        create_database(database_path)
    assert os.path.exists(database_path)
    assert not create_database(database_path)
    os.remove(database_path)


def test_seed_example_data():
    """seed_database() should insert data from
    src/database_tools/example_database_data. Other tables
    should remain empty. Test grabs and formats the data from
    all tables in the database, and then builds a dictionary of lists
    from the commands to match."""
    if os.path.exists(database_path):
        os.remove(database_path)
    create_database(database_path)
    assert seed_database(database_path)
    conn = sqlite3.connect(database_path)
    c = conn.cursor()

    c.execute(
        "SELECT DISTINCT tbl_name FROM sqlite_master WHERE tbl_name != 'sqlite_sequence'"
    )
    table_names = [row[0] for row in c.fetchall()]
    table_info = {}
    for table in table_names:
        c.execute("SELECT * FROM '%s'" % (table,))
        table_info[table] = [str(row).replace("None", "NULL") for row in c.fetchall()]

    example_commands = {key: [] for key in table_names}
    with open(
        Path(__file__).parent / "../src/database_tools/example_database_data.txt"
    ) as file:
        lines = file.read().splitlines()
        for line in lines:
            example_commands[line.split("INSERT INTO ")[1].split(" VALUES")[0]].append(
                line.split("INSERT INTO ")[1].split("VALUES")[1]
            )
    assert table_info == example_commands
    os.remove(database_path)


def test_create_json():
    """Ensure that creating the json file
    works and default data is as expected"""
    if os.path.exists(config_path):
        os.remove(config_path)
    assert not os.path.exists(config_path)
    create_config_json(config_path)
    assert os.path.exists(config_path)
    with open(config_path, "r", encoding="utf-8") as file:
        actual_data = json.load(file)
    expected_data = {
        "printing_width": 42,
        "backup_interval": 5,
        "tax_amount": "0.06625",
        "backup_removal_cutoff": 14,
        "manual_time_last_boot": True,
        "database_name": "RegisterDatabase",
        "backup_path": "~/Desktop/",
        "printer_vendor_id": "0x0000",
        "printer_product_id": "0x0000",
        "email_address": "johnsmith123@gmail.com",
        "reconciling_mode": True,
    }
    assert actual_data == expected_data
    os.remove(config_path)
