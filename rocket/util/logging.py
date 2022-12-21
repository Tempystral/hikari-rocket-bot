import logging
from logging.handlers import TimedRotatingFileHandler
from os import mkdir, path

from .config import LOG_LEVEL

def setup_logging() -> logging.Logger:
  logger = logging.getLogger()
  logger.setLevel(LOG_LEVEL)

  logging.getLogger("pyngrok.process.ngrok").setLevel(logging.DEBUG)

  if not path.exists("./logs"):
    mkdir("./logs")
  
  fh = TimedRotatingFileHandler(filename="./logs/rocketbot.log", when="midnight")
  fh.setFormatter(logging.Formatter("%(levelname)-1.1s %(asctime)23.23s %(name)s: %(message)s"))
  fh.setLevel(LOG_LEVEL)
  logger.addHandler(fh)

  return logger