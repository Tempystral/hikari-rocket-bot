from logging import getLogger
import hikari
import lightbulb as lb

from twitchAPI.helper import first
from twitchAPI.oauth import get_user_info

from rocket.extensions.checks import has_elevated_role_in_guild
from rocket.twitch import TwitchHelper
from rocket.util.config import ServerConfig
from rocket.util.errors import RocketBotException

log = getLogger("rocket.extensions.twitch")

twitch_plugin = lb.Plugin("twitch")

@twitch_plugin.command
@lb.add_checks(has_elevated_role_in_guild())
@lb.command("twitch", "Perform Twitch-related actions", hidden=False, guilds=[645680257797586953, 697911541193769021])
@lb.implements(lb.SlashCommandGroup, lb.PrefixCommandGroup)
async def twitch_group(ctx: lb.Context) -> None:
  pass

@twitch_group.child
@lb.option("username", "Your Twitch username", type=str)
@lb.command("authorize", "Perform Twitch-related actions", aliases=["auth"], hidden=False)
@lb.implements(lb.SlashSubCommand, lb.PrefixSubCommand)
async def authorize_user(ctx: lb.Context):
  helper: TwitchHelper = ctx.bot.d.helper
  settings: ServerConfig = ctx.bot.d.settings

  log.info(f"{ (settings is ctx.bot.d.settings) = }")

  tokens = None

  assert ctx.options.username
  assert ctx.guild_id

  if ctx.options.username in settings.get_all_users():
    if ctx.options.username not in settings.get_guild(ctx.guild_id).watching:
      settings.add_user(ctx.guild_id, ctx.options.username)
    # Attempt to re-validate
    if (user := settings.get_user(ctx.options.username)):
      tokens = await helper.validate(user)
  
  if not tokens: # User is not in the list or has invalid tokens
    await ctx.respond(f"You need to authorize Rocketbot with Twitch. Please sign in at <{helper.userauth.return_auth_url()}>", flags=hikari.MessageFlag.EPHEMERAL)
    tokens = await helper.authenticate()
  
  user = await first(helper.twitch.get_users(logins=[ctx.options.username]))
  
  if tokens and user:
    userinfo:dict[str,str] = await get_user_info(tokens[0])
    log.debug(f"User retrieved: {userinfo.get('preferred_username')} | id: {userinfo.get('sub')}")
    if userinfo.get("sub") == user.id:
      log.debug(f"Verified: {user.display_name} is correct user, adding to list of users")
      settings.set_user_tokens(ctx.options.username, int(user.id), user.display_name, tokens[0], tokens[1])
      await helper.add_subscription(ctx.options.username)

      await ctx.respond(
        hikari.Embed(description=f"User successfully authenticated!", colour="#6441a5")
        .set_author(name=user.display_name, icon=user.profile_image_url))
      return

@twitch_plugin.set_error_handler
async def on_error(event: lb.events.CommandErrorEvent) -> bool | None:
  log.warning(f"Caught exception: {type(event.exception)}")

  # if isinstance(event.exception, lb.errors.CommandInvocationError):
  if isinstance(event.exception, RocketBotException):
    await event.context.respond(event.exception.message, flags=hikari.MessageFlag.EPHEMERAL)
    return True # To tell the bot not to propogate this error event up the chain

def load(bot: lb.BotApp) -> None:
  bot.add_plugin(twitch_plugin)

def unload(bot: lb.BotApp) -> None:
  bot.remove_plugin(twitch_plugin)