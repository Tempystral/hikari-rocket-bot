from os import path
from typing import Protocol
import aiofiles

class cacheManager:
  def __init__(self, cache:str):
    self.cache = cache
    if not path.exists(cache):
      with open(cache, "w") as file:
        file.write("")
  
  async def contains(self, query:str) -> bool:
    '''Look for a string in the cache. Returns `True` if the string is present.'''
    usernames = await self.__readlines(lambda x: x == query)
    return True if usernames else False

  async def put(self, entry:str) -> None:
    '''Write a new entry to the cache. If the entry is already present, pass.'''
    if not self.contains(entry):
      async with aiofiles.open(self.cache, "a") as f:
        f.write(entry + "\n")
    else:
      print(f"Username {entry} was already cached.")

  async def get(self, query:str) -> str:
    '''Gets an entry from the cache. If the entry is not present, return an empty string.'''
    usernames = await self.__readlines(lambda x: x == query)
    return usernames[0] if usernames else ""
    
  async def remove(self, query:str) -> None:
    '''Removes an entry if it exists in the cache.'''
    entries = await self.__readlines(lambda x: x != "")
    if query in entries:
      entries.remove(query)
    async with aiofiles.open(self.cache, "w") as f:
      for e in entries:
        f.write(e + "\n")
  
  async def __readlines(self, condition: Protocol = None) -> list[str]:
    '''Read lines from the cache file with an optional'''
    async with aiofiles.open(self.cache, "r") as f:
      lines = [line.strip() for line in await f.readlines() if (condition(line.strip()) if condition is not None else True)]
    return lines