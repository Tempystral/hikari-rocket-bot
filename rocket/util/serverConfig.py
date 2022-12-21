from dataclasses import dataclass, field
from dataclass_wizard import JSONWizard

@dataclass
class UserConfig:
  id:int
  username:str
  display_name:str
  user_token:str
  refresh_token:str

@dataclass
class GuildConfig:
  name:str | None = None
  guild_id:int | None = None
  notification_channel:int | None = None
  everyone:bool = False
  elevated_roles:list[int] = field(default_factory=list)
  watching:list[str] = field(default_factory=list)

@dataclass
class ServerConfig(JSONWizard):
  class _(JSONWizard.Meta):
    key_transform_with_load = "SNAKE"

  guilds: dict[int, GuildConfig] = field(default_factory=dict)
  users: list[UserConfig] = field(default_factory=list)