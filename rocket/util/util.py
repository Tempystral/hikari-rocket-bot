import logging
from logging.handlers import TimedRotatingFileHandler
from os import mkdir, path
from types import FunctionType
from typing import Iterable

from dateutil import parser as dp
from .config import LOG_LEVEL

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
  logger.setLevel(LOG_LEVEL)

  if not path.exists("./logs"):
    mkdir("./logs")
  
  fh = TimedRotatingFileHandler(filename="./logs/rocketbot.log", when="midnight")
  fh.setFormatter(logging.Formatter("%(levelname)-1.1s %(asctime)23.23s %(name)s: %(message)s"))
  fh.setLevel(LOG_LEVEL)
  logger.addHandler(fh)

  return logger