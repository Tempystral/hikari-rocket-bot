import tomli

with open("config.toml", "rb") as f:
  config = tomli.load(f)

LOG_LEVEL = config.get("LOG_LEVEL")
CACHE_FILE = config["CACHE"]
SETTINGS_FILE = config["SETTINGS_FILE"]

TWITCH_ID = config["TWITCH_ID"]
TWITCH_SECRET = config["TWITCH_SECRET"]
EVENTSUB_PORT = config["EVENTSUB_PORT"]

DISCORD_TOKEN = config["DISCORD_TOKEN"]

NGROK_PATH = config["NGROK_PATH"]
NGROK_CONF = config["NGROK_CONF"]