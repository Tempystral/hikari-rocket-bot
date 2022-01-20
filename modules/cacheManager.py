from os import path


class cacheManager:
  def __init__(self, cache:str):
    self.cache = cache
    if not path.exists(cache):
      with open(cache, "w") as file:
        file.write("")
  
  def checkCache(self, query:str) -> bool:
    with open(self.cache, "r") as f:
      usernames = [line.strip() for line in f if line.strip() == query]
      if usernames:
        return True
      return False

  def writeCache(self, entry:str):
    if not self.checkCache(entry):
      with open(self.cache, "a") as f:
        f.write(entry + "\n")
        return
    else:
      print(f"Username {entry} was already cached.")

  def readCache(self, query:str) -> str:
    with open(self.cache, "r") as f:
      usernames = [line.strip() for line in f if line.strip() == query]
      if usernames:
        return usernames[0]
      return ""
    
  def removeEntry(self, entry:str):
    entries = list()
    with open(self.cache, "r") as f:
      entries = [line.strip() for line in f if line.strip() != ""]
    if entry in entries:
      entries.remove(entry)
    with open(self.cache, "w") as f:
      for e in entries:
        f.write(e + "\n")