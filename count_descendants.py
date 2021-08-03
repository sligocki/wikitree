import argparse
import collections
import time

import data_reader


def count_descendants(db, person_num, remove_num=None):
  parents = {person_num}
  num_descendants = []
  while parents:
    num_descendants.append(len(parents))
    children = set()
    for parent in parents:
      children.update(db.children_of(parent))
    children.discard(remove_num)
    parents = children
  return num_descendants

def load_descendants(db, person_num):
  parents = {person_num}
  descendants = set()
  while parents:
    children = set()
    for parent in parents:
      if parent not in descendants:
        children.update(db.children_of(parent))
    descendants.update(parents)
    parents = children
  return descendants


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("wikitree_id")
  parser.add_argument("--version", help="Data version (defaults to most recent).")
  args = parser.parse_args()

  db = data_reader.Database(args.version)
  start_num = db.id2num(args.wikitree_id)

  descendants = load_descendants(db, start_num)

  descendants_born_in_centuries = collections.Counter()
  for person in descendants:
    birth_date = db.birth_date_of(person)
    if birth_date:
      birth_year = birth_date.year
      birth_century = (birth_year // 100) * 100
      descendants_born_in_centuries[birth_century] += 1
    else:
      descendants_born_in_centuries[0] += 1

  print("Descendants by (birth) century")
  for birth_century in sorted(descendants_born_in_centuries.keys()):
    print(f" * {birth_century:6d} {descendants_born_in_centuries[birth_century]:10_d}")
  print(f"Total # descendants: {len(descendants):_}")
