import argparse
import collections
import time

import data_reader


def count_descendants(db, person_num, remove_num=None):
  parents = set()
  parents.add(person_num)
  descendants = []
  while parents:
    descendants.append(len(parents))
    children = set()
    for parent in parents:
      children.update(db.children_of(parent))
    children.discard(remove_num)
    parents = children
  return descendants


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("wikitree_id")
  parser.add_argument("remove_id", nargs='?')
  args = parser.parse_args()

  db = data_reader.Database()
  start_num = db.id2num(args.wikitree_id)
  remove_num = db.id2num(args.remove_id) if args.remove_id else None

  descendants = count_descendants(db, start_num, remove_num)
  print(sum(descendants), descendants)
