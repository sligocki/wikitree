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


def descendants_per_ancestor(db, start_num):
  todo = collections.deque()
  todo.append((0, 1, start_num))
  best_count = 0
  while todo:
    gen, ahnentafel, person_num = todo.popleft()
    descendants = count_descendants(db, person_num)
    count = sum(descendants)
    if True: #count > best_count:
      print(gen, ahnentafel, db.num2id(person_num), db.name_of(person_num), sum(descendants), descendants)
      best_count = count
    # Add parents
    father_num = db.father_of(person_num)
    if father_num:
      todo.append((gen + 1, ahnentafel * 2, father_num))
    mother_num = db.mother_of(person_num)
    if mother_num:
      todo.append((gen + 1, ahnentafel * 2 + 1, mother_num))


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
