"""
Measure distances between randomly chosen points repeatedly
"""


import argparse
import random

import collections
import connection
import data_reader
import itertools
import math
import partition_tools
import time
import utils


parser = argparse.ArgumentParser()
parser.add_argument("--version", help="Data version (defaults to most recent).")
parser.add_argument("--load-db", action="store_true")
args = parser.parse_args()

utils.log("Load DB")
db = data_reader.Database(version=args.version)
if args.load_db:
  db.load_connections()
partition_db = partition_tools.PartitionDb(version=args.version)

utils.log("Loading all user_nums in main tree")
focus_id = db.id2num("Lothrop-29")
rep = partition_db.find_partition_rep("connected", focus_id)
main_nums = list(partition_db.list_partition("connected", rep))
utils.log(f"Loaded {len(main_nums):_} nodes")

hist = collections.Counter()
total = 0
total2 = 0
try:
  for i in itertools.count():
    start_time = time.time()
    start_num = random.choice(main_nums)
    end_num = random.choice(main_nums)
    paths = connection.find_connections(db, start_num, end_num)
    dist = len(next(paths)) - 1
    utils.log(f"Distance {i}: {start_num} -> {end_num} = {dist} ({time.time() - start_time:.1f}s)")

    hist[dist] += 1
    total += dist
    total2 += dist**2
    count = i + 1
    mean = total / count
    stddev = math.sqrt(total2 / count - mean**2)
    utils.log(f"Mean dist = {mean:.1f} ± {stddev:.1f}")

except KeyboardInterrupt:
  utils.log("Dist", [hist[i] for i in range(max(hist.keys()) + 1)])
  utils.log("Quiting")
