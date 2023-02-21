import functools
from rocket.util.config import ServerConfig
import lightbulb as lb

def _has_streamer_role(context: lb.context.Context) -> bool:
  lb.checks._guild_only(context)
  assert context.guild_id is not None
  assert context.member is not None

  settings:ServerConfig = context.bot.d.settings
  role = settings.get_guild(context.guild_id).streamer_role
  if role in context.member.role_ids:
    return True
  raise lb.errors.MissingRequiredRole(
    "You are missing one or more roles required to run this command",
    roles=[role if role else -1],
    mode=any)
  

def has_streamer_role_in_guild() -> lb.Check:
  return lb.Check(functools.partial(_has_streamer_role))