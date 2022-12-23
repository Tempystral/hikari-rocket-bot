import lightbulb as lb
from hikari import MessageFlag
from rocket.util.config import ServerConfig
from rocket.extensions.checks import has_elevated_role_in_guild

debug_plugin = lb.Plugin("Debug")

@debug_plugin.command
@lb.add_checks(has_elevated_role_in_guild())
@lb.command("debug", "Manage internal settings for the bot", hidden=True)
@lb.implements(lb.SlashCommandGroup, lb.PrefixCommandGroup)
async def module_group(ctx: lb.Context) -> None:
  pass

@module_group.child
@lb.option("module_name", "The module to target.", type=str)
@lb.command("reload", "Reloads a module.", inherit_checks=True)
@lb.implements(lb.SlashSubCommand, lb.PrefixSubCommand)
async def reload_module(ctx: lb.Context):
  """Reload a lightbulb extension"""

  module_name = getModuleName(ctx)

  try:
    ctx.bot.reload_extensions(module_name)
  except ValueError:
    ctx.bot.load_extensions(module_name)

  #await ctx.bot.declare_global_commands()
  await ctx.respond(f"Reloaded module {module_name}", flags=MessageFlag.EPHEMERAL)

@module_group.child
@lb.command("test", "Puts the bot in testing mode.", inherit_checks=True)
@lb.implements(lb.SlashSubCommand, lb.PrefixSubCommand)
async def test_module(ctx: lb.Context):
  """Put a module into test mode"""
  if not ctx.bot.d.testmode:
    ctx.bot.d.testmode = True
  else:
    ctx.bot.d.testmode = not ctx.bot.d.testmode

  prefix = "en" if ctx.bot.d.testmode else "dis"
  await ctx.respond(f"Test mode {prefix}abled!")


def load(bot: lb.BotApp) -> None:
  bot.add_plugin(debug_plugin)

def getModuleName(ctx: lb.Context) -> str:
  return f"rocket.extensions.{ctx.options.module_name}"