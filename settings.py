import json

with open('/run/secrets/discord_bot_secrets') as file:
    settings = json.load(file)

ERROR_WEBHOOK = settings["ERROR_WEBHOOK"]
DEV_GUILD = settings["DEV_GUILD"]
COLOUR = settings["COLOUR"]
DISCORD_TOKEN = settings["DISCORD_TOKEN"]

