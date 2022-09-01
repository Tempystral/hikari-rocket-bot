from os import path

class cacheManager:
  def __init__(self, cache:str):
    self.cache = cache
    if not path.exists(cache):
      with open(cache, "w") as file:
        file.write("")
  
  def contains(self, query:str) -> bool:
    '''Look for a string in the cache. Returns `True` if the string is present.'''
    with open(self.cache, "r") as f:
      usernames = [line.strip() for line in f if line.strip() == query]
      if usernames:
        return True
      return False

  def put(self, entry:str):
    '''Write a new entry to the cache. If the entry is already present, pass.'''
    if not self.contains(entry):
      with open(self.cache, "a") as f:
        f.write(entry + "\n")
        return
    else:
      print(f"Username {entry} was already cached.")

  def get(self, query:str) -> str:
    '''Gets an entry from the cache. If the entry is not present, return an empty string.'''
    with open(self.cache, "r") as f:
      usernames = [line.strip() for line in f if line.strip() == query]
      if usernames:
        return usernames[0]
      return ""
    
  def remove(self, entry:str):
    '''Removes an entry if it exists in the cache.'''
    entries = list()
    with open(self.cache, "r") as f:
      entries = [line.strip() for line in f if line.strip() != ""]
    if entry in entries:
      entries.remove(entry)
    with open(self.cache, "w") as f:
      for e in entries:
        f.write(e + "\n")