from database_tools.create_database import create_database, seed_database
from database_tools.create_config_json import create_config_json

print("Database intialized") if create_database() else print("Database already exists, skipping")
print("config.json created") if create_config_json() else print("config.json already exists, skipping")

answer = input("Seed database with testing data? y/n ")

if answer == ('y' or 'Y' or 'yes' or 'Yes'):
    seed_database()
