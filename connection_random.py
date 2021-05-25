"""
Measure distances between randomly chosen points repeatedly
"""


import random

import collections
import connection
import data_reader
import group_tools
import itertools
import math
import time
import utils


db = data_reader.Database()
db.load_connections()

utils.log("Loading all user_nums in main tree")
focus_id = db.id2num("Lothrop-29")
rep = group_tools.find_group_rep("connected", focus_id)
main_nums = list(group_tools.list_group("connected", rep))
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
  utils.log("Dist", sorted(hist.items()))
  utils.log("Quiting")
