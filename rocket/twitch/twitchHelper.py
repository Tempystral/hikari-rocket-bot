from __future__ import annotations

from logging import getLogger
from pprint import pprint

from decouple import config
from twitchAPI.twitch import Twitch

from . import TwitchResponse, TwitchStream

logger = getLogger("twitchHelper")

def get_streams(twitch_channels:list[str]) -> list[TwitchStream]:
  return [TwitchHelper().get_live_channels(ch).parse_data() for ch in twitch_channels]

def get_stream(channel:str) -> TwitchStream:
  data = TwitchHelper().get_live_channels(channel).parse_data()
  if data:
    logger.info(f"Found data for channel: {channel} playing {data.game_name} since {data.started_at}")
  return data

class TwitchHelper:
  def __init__(self):
    self.twitch = self.init_twitch(config("TWITCH_ID"), config("TWITCH_SECRET"))

  def init_twitch(self, id, secret) -> Twitch:
    if not id or not secret:
      return None
    return Twitch(id, secret)

  def get_live_channels(self, query: str) -> TwitchResponse:
    response = self.twitch.search_channels(query, live_only=True)
    return TwitchResponse(query, response)

  def get_thumbnail(self, channel:str, width:int, height:int) -> str:
    data:dict = self.twitch.get_streams(user_login=channel)
    if not data:
      logger.error("Data not initialized!")
      return None
    if not data.get("data"):
      logger.error("No streams found!")
      return None
    thumbnail:str = data.get("data")[0].get("thumbnail_url")
    return thumbnail.replace(r'{width}', str(width)).replace(r'{height}', str(height))
