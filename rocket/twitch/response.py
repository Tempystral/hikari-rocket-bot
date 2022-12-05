from __future__ import annotations
from dataclasses import dataclass, field
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
    stream = (result for result in self.data["data"] if result["broadcaster_login"] == self.query )
    try:
      return TwitchStream(**next(stream)) if stream else None
    except StopIteration as stop:
      log.debug("No more values")
      return None

@dataclass(frozen=True)
class TwitchStream():
  broadcaster_language:str
  broadcaster_login:str
  display_name:str
  game_id:int
  game_name:str
  id:str
  is_live:bool
  thumbnail_url:str
  title:str
  started_at:str
  tag_ids: field(default_factory=list)