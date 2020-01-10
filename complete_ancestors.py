import argparse
import itertools

import data_reader
import enum_kin


parser = argparse.ArgumentParser()
parser.add_argument("start_id")
args = parser.parse_args()

db = data_reader.Database()

start_num = db.id2num(args.start_id)
for ahn, ancestor in enum_kin.enum_ancestors(db, start_num):
  print(ahn, db.name_of(ancestor), end = "")
  for gen in enum_kin.enum_descendant_generations(db, ahn, ancestor):
    num_complete = 0
    for _, kin in gen:
      if db.get(kin, "no_more_children"):
        num_complete += 1
    print(" %.2f" % (num_complete / len(gen)), end = "")
  print()
