from types import FunctionType
from typing import Iterable

from dateutil import parser as dp

def parseTimestamp(isoString:str) -> str:
  timestamp:str = ""
  try:
    timestamp = f"<t:{int(dp.isoparse(isoString).timestamp())}>"
  except ValueError as e:
    timestamp = isoString
  return timestamp

def find(predicate: FunctionType, it: Iterable):
  matches = []
  for element in it:
    if predicate(element):
      matches.append(element)
  return matches if matches else None