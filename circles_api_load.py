# Load 100 Circles data from URL.

import argparse
import datetime
import json
from pathlib import Path
from pprint import pprint
import subprocess
import urllib.parse

import utils


def read_url(url : str) -> str:
  # Recently this started failing with error:
  #   urllib.error.URLError: <urlopen error [SSL: SSLV3_ALERT_HANDSHAKE_FAILURE] ssl/tls alert handshake failure (_ssl.c:1000)>
  # with urllib.request.urlopen(url) as resp:
  #   data_text = resp.read().decode("ascii")
  return subprocess.run(["curl", url], stdout=subprocess.PIPE, check=True, encoding="ascii").stdout


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("wikitree_id")
  parser.add_argument("--time", action="store_true",
                      help="Include time-of-day in filename.")
  parser.add_argument("--infile", "-f", type=Path)
  args = parser.parse_args()

  if args.infile:
    data_text = args.infile.read_text()
  else:
    params = urllib.parse.urlencode({"WikiTreeID": args.wikitree_id})
    url = f"https://plus.wikitree.com/function/WT100Circles/Tree.json?{params}"
    utils.log(f"Loading URL {url}")
    data_text = read_url(url)

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

main()
