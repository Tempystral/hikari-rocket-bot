import asyncio
import logging

from aiohttp import ClientSession

from rocket.util.config import EVENTSUB_PORT, TWITCH_ID, TWITCH_SECRET
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.helper import first
from twitchAPI.twitch import Twitch

log = logging.getLogger()



TARGET_USERNAME = 'tempystral'

async def get_ngrok_url(session: ClientSession):
    async with session.get("http://localhost:4040/api/tunnels") as response:
        return await response.json()

async def on_follow(data: dict):
    # our event happend, lets do things with the data we got!
    print(data)


async def eventsub_example():
    # create the api instance and get the ID of the target user
    twitch = await Twitch(TWITCH_ID, TWITCH_SECRET)
    await twitch.authenticate_app([])
    twitch.user_auth_refresh_callback
    user = await first(twitch.get_users(logins=TARGET_USERNAME))
    print(user.id)
    print(user.display_name)

    auth = UserAuthenticator(twitch, [])

    access_token, refresh_token = await auth.authenticate()
    print(f"Access token: {access_token} | Refresh token: {refresh_token}")


# lets run our example
loop = asyncio.new_event_loop()
loop.run_until_complete(eventsub_example())
loop.close()

# async def run(token:str, cache:str, settings: dict):
#   cm = cacheManager(cache)

#   channels = {ch for server in settings["servers"] for ch in server["watching"]}
#   for channel in channels:
#     stream = get_stream(channel)
#     if stream and not await cm.contains(channel):
#       # If the stream is live and has NOT been announced
#       for server in find(lambda x: channel in x["watching"], settings["servers"]):
#         # If the selected channel is not in the cache, an embed can be posted
#         notif = (
#           Embed(title=f"{stream.title}", url=f"https://www.twitch.tv/{stream.broadcaster_login}", colour="#9146FF")
#             .set_image(twitch.get_thumbnail(channel, 1280, 720))
#             .set_author(name=stream.display_name, icon=stream.thumbnail_url)
#             .add_field(name="Game", value=stream.game_name, inline=True)
#             .add_field(name="Started at", value=parseTimestamp(stream.started_at), inline=True)
#         )
        
#         message_text = f"{'@everyone, ' if server['everyone'] else ''}{stream.display_name} is live!"
#         try:
#           await client.create_message(channel=server["notification_channel"], content=message_text, embed=notif)
#         except ForbiddenError as e:
#           log.error(f"Not authorized to post in server: {server['name']}!")
      
#       await cm.put(channel) # Add the channel to the cache so it isn't announced again

#     elif not stream and await cm.contains(channel):
#       #If the stream is not live but is still in the cache
#       await cm.remove(channel)
#     else:
#       if await cm.contains(channel):
#         log.debug(f"{channel} already announced, skipping...")