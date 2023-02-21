import logging
from logging.handlers import TimedRotatingFileHandler
from os import mkdir, path

def setup_logging(log_level: str) -> logging.Logger:
  logger = logging.getLogger()
  logger.setLevel(log_level)

  logging.getLogger("pyngrok").setLevel(logging.INFO)
  logging.getLogger("hikari").setLevel(logging.INFO)
  logging.getLogger("lightbulb").setLevel(logging.INFO)

  if not path.exists("./logs"):
    mkdir("./logs")
  
  fh = TimedRotatingFileHandler(filename="./logs/rocketbot.log", when="midnight")
  fh.setFormatter(logging.Formatter("%(levelname)-1.1s %(asctime)23.23s %(name)s: %(message)s"))
  fh.setLevel(log_level)
  logger.addHandler(fh)

  return logger