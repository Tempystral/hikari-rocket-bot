from dateutil import parser as dp

def parseTimestamp(isoString:str) -> str:
  timestamp:str = ""
  try:
    timestamp = f"<t:{int(dp.isoparse(isoString).timestamp())}>"
  except ValueError as e:
    timestamp = isoString
  return timestamp

