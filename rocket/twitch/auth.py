import asyncio
import logging
from concurrent.futures import CancelledError
from threading import Thread
from time import sleep
from typing import Coroutine

from aiohttp import web
from aiohttp.web import AppRunner
from twitchAPI import Twitch
from twitchAPI.helper import (TWITCH_AUTH_BASE_URL, build_scope, build_url, get_uuid)
from twitchAPI.types import AuthScope

log = logging.getLogger("rocket.twitch.auth")

class AuthServer:
  def __init__(self, twitch: Twitch, scopes: list[AuthScope], url: str, state: str):
    # Auth params
    self.__twitch: Twitch = twitch
    self.scopes: list[AuthScope] = scopes
    self.url: str = url
    self.host, self.port = url.rsplit(":", 1)
    self.state: str = state if state else str(get_uuid())
    # Server state params
    self.__user_token: str | None = None
    self.__is_running: bool = False
    self.__is_stopped: bool = False
    self.__can_stop: bool = False
    # Threading params
    self.__loop: asyncio.AbstractEventLoop = None
    self.__thread: Thread = None
    self.__runner: web.AppRunner = None

  def __build_auth_url(self):
    params = {
      'client_id': self.__twitch.app_id,
      'redirect_uri': self.url,
      'response_type': 'code',
      'scope': build_scope(self.scopes),
      'force_verify': str(False).lower(),
      'state': self.state
    }
    return build_url(TWITCH_AUTH_BASE_URL + 'oauth2/authorize', params)

  def state_valid(self, value: str | None) -> bool:
    return self.state == value

  async def is_started(self) -> bool:
    '''Returns true when the webserver has started'''
    if not self.__is_running:
      await asyncio.sleep(0.01)
    return True

  def __run_server(self, runner: AppRunner):
    self.__loop = asyncio.new_event_loop()
    asyncio.set_event_loop(self.__loop)
    self.__loop.run_until_complete(runner.setup())
    self.__runner = runner # For persistence I think
    server = web.TCPSite(runner, host=self.host, port=int(self.port))
    self.__loop.run_until_complete(server.start())
    self.__is_running = True
    log.debug("Started auth server")
    try:
      self.__loop.run_until_complete(self.__run_check())
    except (CancelledError, asyncio.CancelledError) as e:
      log.info(f"Server run cancelled: {e.__class__}")
    
  async def __run_check(self):
    while not self.__can_stop:
      try:
        await asyncio.sleep(.5)
      except (CancelledError, asyncio.CancelledError):
        pass
    # Else...
    log.debug("Shutting down auth server")
    for task in asyncio.all_tasks(self.__loop):
      log.info("Task cancelled!")
      task.cancel()
    self.__is_stopped = True

  def __start(self):
    self.__thread = Thread(target=self.__run_server, args=(self.__create_runner(), ))
    log.debug("Starting thread...")
    self.__thread.start()

  def __stop(self):
    log.debug("Stopping web server...")
    self.__can_stop = True

  def __create_runner(self) -> AppRunner:
    app = web.Application()
    app.add_routes([web.get("/", self.__handle_callback)])
    runner = AppRunner(app)
    return runner

  async def __handle_callback(self, request: web.Request) -> web.Response:
    # Is the state the same one sent with the auth request?
    state = request.rel_url.query.get("state")
    log.debug(f"Received callback: {state}")
    if not self.state_valid(state):
      return web.Response(status=401)
    
    # Was the user ID returned?
    self.__user_token = request.rel_url.query.get("code")
    if self.__user_token is None:
      return web.Response(status=400)

    # Display OK page
    with open("./rocket/twitch/response.html", "rb") as f:
      document = f.read()
    return web.Response(body=document, content_type="text/html")
  
  async def go(self, message_callback: Coroutine) -> str | None:
    '''
    Starts a webserver to listen for authorization requests from Twitch.
    '''
    self.__can_stop = False
    self.__is_stopped = False

    # Start server and wait for it to finish starting
    self.__start()
    while not self.__is_running:
      sleep(0.01)
    # Send message with the server URL
    message = asyncio.create_task(message_callback)
    # Now wait for the user to authenticate OR five minutes
    timer = 0.0
    while self.__user_token is None and timer <= 300:
      sleep(0.01)
      timer += 0.01
    # Stop the server and wait for it to stop
    self.__stop()
    while not self.__is_stopped:
      await asyncio.sleep(0.01)

    if timer >= 300:
      raise TimeoutError

    return self.__user_token
