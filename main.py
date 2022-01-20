import asyncio
import hikari
from dateutil import parser as dp
from decouple import config

from modules import TwitchHelper
from modules import cacheManager

discord_token = config("DISCORD_TOKEN")
notif_channel = config("NOTIFICATION_CHANNEL")
twitch_channel = config("TWITCH_CHANNELS").split(",")[0]

bot = hikari.RESTApp()
cm = cacheManager(config("CACHE"))

async def run(token, notif_channel, twitch_channel):
    # We acquire a client with a given token. This allows one REST app instance
    # with one internal connection pool to be reused.
    async with bot.acquire(token, hikari.TokenType.BOT) as client:
            twitchHelper = TwitchHelper(twitch_channel)
            data = twitchHelper.poll_stream().read_user_data()
            if data:
                try:
                    timestamp = f"<t:{int(dp.isoparse(data['started_at']).timestamp())}>"
                except ValueError as e:
                    timestamp = data['started_at']
                    
                notif = hikari.Embed(title=f"{data['title']}",
                                    url=f"https://www.twitch.tv/{data['broadcaster_login']}",
                                    colour="#9146FF")\
                    .set_image(twitchHelper.get_stream_thumbnail(1280, 720))\
                    .set_author(icon=data["thumbnail_url"], name=data["display_name"])\
                    .add_field(name="Game", value=data["game_name"], inline=True)\
                    .add_field(name="Started at", value=timestamp, inline=True)

                #pprint(data)
                if not cm.checkCache(twitch_channel):
                    await client.create_message(channel=notif_channel, content="@everyone", embed=notif)
                    cm.writeCache(twitch_channel)
            else:
                cm.removeEntry(twitch_channel)

asyncio.run(run(discord_token, notif_channel, twitch_channel))

#pprint(twitchHelper.poll_stream("macaw45").read_user_data())
