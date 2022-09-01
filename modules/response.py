from __future__ import annotations
from logging import getLogger

log = getLogger("twitchResponse")

class TwitchResponse:
  def __init__(self, query: str, data: dict):
    self.query = query
    self.data = data
  
  def parse_data(self) -> TwitchStream:
    if not self.data:
      log.warning("Data not initialized!")
      return None
    if not self.data.get("data"):
      log.debug(f"No streams found for '{self.query}'")
      return None
    # Filter results
    entry:list = [result for result in self.data["data"] if result["broadcaster_login"] == self.query ]
    result = TwitchStream(entry[0]) if entry else None
    #log.info(result)
    return result

class TwitchStream():
  def __init__(self, data: dict):
    self.broadcaster_language:str = data["broadcaster_language"]
    self.broadcaster_login:str = data["broadcaster_login"]
    self.display_name:str = data["display_name"]
    self.game_id = int(data["game_id"])
    self.game_name = data["game_name"]
    self.id = int(data["id"])
    self.is_live = bool(data["is_live"])
    self.tag_ids:list = data["tag_ids"]
    self.thumbnail_url:str = data["thumbnail_url"]
    self.title:str = data["title"]
    self.started_at:str = data["started_at"]
  
  def __str__(self) -> str:
    return str(vars(self))