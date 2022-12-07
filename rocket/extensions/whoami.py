from hikari import Embed
import lightbulb as lb

whoami_plugin = lb.Plugin(name="Whoami")

@whoami_plugin.command()
@lb.command(name="whoami", description="Get information about your account.")
@lb.implements(lb.PrefixCommand, lb.SlashCommand)
async def whoami(ctx: lb.Context):
    """Replies with information about the user."""
    date_format = "%a, %d %b %Y %I:%M %p"
    member = ctx.member

    embed = Embed(description=member.mention)

    embed.set_author(name=member.nickname, icon=member.avatar_url)
    embed.set_thumbnail(member.avatar_url)
    embed.add_field(name="Joined", value=member.joined_at.strftime(date_format), inline=True)
    members = sorted(ctx.get_guild().get_members().values(), key=lambda m: m.joined_at)
    #embed.add_field(name="Join position", value=str(members.index(member)+1), inline=True)
    embed.add_field(name="Registered", value=member.created_at.strftime(date_format), inline=True)

    if len(member.get_roles()) > 1:
        role_string = ', '.join([r.mention for r in member.get_roles() if r.name != "@everyone"])
        embed.add_field(name="Roles [{}]".format(len(member.get_roles())-1), value=role_string)

    #perm_string = ", ".join(str(member.permissions.split()))
    #embed.add_field(name="Guild permissions", value=perm_string)

    embed.set_footer(text='ID: ' + str(member.id))
    await ctx.respond(embed=embed)

def load(bot: lb.BotApp) -> None:
    bot.add_plugin(whoami_plugin)

def unload(bot: lb.BotApp) -> None:
    bot.remove_plugin(whoami_plugin)