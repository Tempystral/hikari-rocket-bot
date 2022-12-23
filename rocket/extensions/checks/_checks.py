import functools
from rocket.util.config import ServerConfig
import lightbulb as lb

def _has_elevated_role(context: lb.context.Context) -> bool:
  lb.checks._guild_only(context)
  assert context.guild_id is not None
  assert context.member is not None

  settings:ServerConfig = context.bot.d.settings
  roles = settings.get_guild(context.guild_id).elevated_roles
  for state in (r in roles for r in context.member.role_ids):
    if state is True:
      return state
  raise lb.errors.MissingRequiredRole(
    "You are missing one or more roles required to run this command",
    roles=roles,
    mode=any)
  

def has_elevated_role_in_guild() -> lb.Check:
  return lb.Check(functools.partial(_has_elevated_role))