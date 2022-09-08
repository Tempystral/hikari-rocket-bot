import logging
from logging.handlers import TimedRotatingFileHandler
from os import mkdir, path
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

def setup_logging() -> logging.Logger:
  logger = logging.getLogger()

  logger.setLevel(logging.DEBUG)
  ch = logging.StreamHandler()
  ch.setLevel(logging.INFO)
  ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
  logger.addHandler(ch)

  if not path.exists("./logs"):
    mkdir("./logs")
  
  fh = TimedRotatingFileHandler(filename="./logs/rocketbot.log", when="midnight")
  fh.setFormatter(logging.Formatter("%(levelname)-1.1s %(asctime)23.23s %(name)s: %(message)s"))
  fh.setLevel(logging.DEBUG)
  logger.addHandler(fh)

  return logger