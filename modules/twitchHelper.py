from __future__ import annotations

from decouple import config
from pprint import pprint
from twitchAPI.twitch import Twitch


class TwitchHelper:
  def __init__(self, channel):
    self.query = channel
    self.data:dict = None
    self.twitch = self.init_twitch(config("TWITCH_ID"), config("TWITCH_SECRET"))

  def init_twitch(self, id, secret) -> Twitch:
    if not id or not secret:
      return None
    return Twitch(id, secret)

  def search_channels(self) -> TwitchHelper:
    self.data = self.twitch.search_channels(self.query, live_only=True)
    return self
    
  def parse_data(self) -> dict:
    if not self.data:
      pprint("Data not initialized.")
      return None
    if not self.data.get("data"):
      pprint(f"No streams found for '{self.query}'")
      return None
    # Filter results
    entry:list = [result for result in self.data["data"] if result["broadcaster_login"] == self.query ]
    return entry[0] if entry else None

  def get_thumbnail(self, width:int, height:int) -> str:
    data:dict = self.twitch.get_streams(user_login=self.query)
    if not data:
      pprint("Data not initialized.")
      return None
    if not data.get("data"):
      pprint("No streams found.")
      return None
    thumbnail:str = data.get("data")[0].get("thumbnail_url")
    return thumbnail.replace(r'{width}', str(width)).replace(r'{height}', str(height))