import functools
import lightbulb as lb
from rocket.util.settingsManager import SettingsHelper

twitch_plugin = lb.Plugin("notifier")

def _has_elevated_role(context: lb.context.Context) -> bool:
  lb.checks._guild_only(context)
  assert context.guild_id is not None
  assert context.member is not None

  helper:SettingsHelper = context.bot.d.settingsHelper
  roles = helper.get_guild(context.guild_id).elevated_roles
  for state in (r in roles for r in context.member.role_ids):
    if state is True:
      return state
  raise lb.errors.MissingRequiredRole(
    "You are missing one or more roles required to run this command",
    roles=roles,
    mode=any)
  

def has_elevated_role_in_guild() -> lb.Check:
  return lb.Check(functools.partial(_has_elevated_role))

@twitch_plugin.command
@lb.add_checks(has_elevated_role_in_guild())
@lb.command("twitch", "Perform Twitch-related actions", hidden=False)
@lb.implements(lb.SlashCommandGroup, lb.PrefixCommandGroup)
async def twitch_group(ctx: lb.Context) -> None:
  pass

@twitch_group.child
@lb.command("authorize", "Perform Twitch-related actions", aliases=["auth"], hidden=False)
@lb.implements(lb.SlashCommandGroup, lb.PrefixCommandGroup)
async def authorize_user(ctx: lb.Context):
  # Look at oauth.py > __handle_callback() and authenticate() from pyTwitchAPI for inspiration
  pass

@twitch_group.child
@lb.option("channel", "Twitch channel to receive notifications about", type=str)
@lb.command("add", "Add a Twitch channel to the bot's notification list", inherit_checks=True)
@lb.implements(lb.SlashSubCommand, lb.PrefixSubCommand)
async def add_stream_online_notifications(ctx: lb.Context):
  '''
  - Check to see whether this user is authenticated in this or another server
    - If they are authenticated in another server, copy the details from that server's list to this one
    - Attempt to validate the user token
      - If authentication fails, attempt to refresh the user token with the listed refresh token.
        - If refresh fails, user is not authenticated
  - If the user is not authenticated, prompt them to authorize the app
  - Add a subscription for the user in EventSub
  '''

  # This function might require some restructuring of the settings.json file
  # It'll probably be easier to make each server a dict with the guild ID as a key, and to store a dict for each twitch channel as well
  pass

@twitch_group.child
@lb.command("test", "Puts the bot in testing mode.", inherit_checks=True)
@lb.implements(lb.SlashSubCommand, lb.PrefixSubCommand)
async def remove_stream_online_notifications(ctx: lb.Context):
  pass

def load(bot: lb.BotApp) -> None:
  bot.add_plugin(twitch_plugin)

def unload(bot: lb.BotApp) -> None:
  bot.remove_plugin(twitch_plugin)