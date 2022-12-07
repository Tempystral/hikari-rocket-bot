from decouple import config
import json
import rocket.util

def _load_settings(settings_file: str) -> list[dict]:
    settings = None
    with open(settings_file, "r") as f:
      settings = json.load(f)
    return settings["servers"]

def _getall(l: list, key: str) -> list:
  return [ obj[key] for obj in l ]

LOG_LEVEL = config("LOG_LEVEL", cast=str)
CACHE_FILE = config("CACHE", cast=str, default="./cache")
SETTINGS_FILE = config("SETTINGS_FILE", cast=str, default="./settings.json")
_settings: list = _load_settings(SETTINGS_FILE)

ELEVATED_ROLES = [ int(guild["elevated_role"]) for guild in _settings ]
GUILDS = [ int(guild["guild_id"]) for guild in _settings ]

def get_watchlist(guild:int) -> list[str]:
  return rocket.util.find(lambda x: guild == x["guild_id"], _settings)[0].get("watching")


TWITCH_ID = config("TWITCH_ID", cast=str)
TWITCH_SECRET = config("TWITCH_SECRET", cast=str)
EVENTSUB_URL = config("EVENTSUB_URL", cast=str)
EVENTSUB_PORT = config("EVENTSUB_PORT", cast=int)

DISCORD_TOKEN = config("DISCORD_TOKEN", cast=str)


