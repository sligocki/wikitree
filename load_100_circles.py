# Load 100 Circles data from URL.

import argparse
import datetime
import json
from pathlib import Path
import urllib.parse
import urllib.request

import utils


parser = argparse.ArgumentParser()
parser.add_argument("wikitree_id")
args = parser.parse_args()

utils.log("Loading URL")
params = urllib.parse.urlencode({"WikiTreeID": args.wikitree_id})
url = f"https://wikitree.sdms.si/function/WT100Circles/Tree.json?{params}"
with urllib.request.urlopen(url) as resp:
  data_text = resp.read().decode("ascii")

utils.log("Parsing JSON")
data = json.loads(data_text)

utils.log("Extracting circle sizes")
circle_sizes = []
for step in data["debug"]["steps"]:
  # Format: circle_num ":" circle_size ":" cumulative_size ":" ???
  this_size = step.split(":")[1]
  circle_sizes.append(int(this_size))

utils.log("Writing results")
date = datetime.date.today().strftime("%Y-%m-%d")
with open(Path("results", "circles", f"{args.wikitree_id}_{date}.json"), "w") as f:
  json.dump({args.wikitree_id: circle_sizes}, f)

utils.log("Finished")
