# Load 100 Circles data from URL.

import argparse
import datetime
import json
from pathlib import Path
from pprint import pprint
import urllib.parse
import urllib.request

import utils


parser = argparse.ArgumentParser()
parser.add_argument("wikitree_id")
parser.add_argument("--time", action="store_true",
                    help="Include time-of-day in filename.")
args = parser.parse_args()

utils.log("Loading URL")
params = urllib.parse.urlencode({"WikiTreeID": args.wikitree_id})
url = f"https://wikitree.sdms.si/function/WT100Circles/Tree.json?{params}"
with urllib.request.urlopen(url) as resp:
  data_text = resp.read().decode("ascii")

utils.log("Parsing JSON")
try:
  data = json.loads(data_text)
except json.decoder.JSONDecodeError:
  print("Error while parsing JSON response:")
  print(data_text)
  raise

try:
  utils.log("Extracting circle sizes")
  circle_sizes = []
  for step in data["debug"]["steps"]:
    circle_num, circle_size, cumulative_size, _ = step
    circle_sizes.append(circle_size)

  utils.log("Writing results")
  if args.time:
    date = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M")
  else:
    date = datetime.date.today().strftime("%Y-%m-%d")
  filename = Path("results", "circles", f"{args.wikitree_id}_{date}.json")
  with open(filename, "w") as f:
    json.dump({args.wikitree_id: circle_sizes}, f)

  utils.log(f"Wrote {filename}")

except:
  print("Error while processing data")
  pprint(data)
  raise
