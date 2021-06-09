import argparse
import collections
import itertools
import time

import count_descendants
import data_reader


def descendants_per_ancestor(db, start_num, args):
  todo = [(1, start_num, None)]
  for gen in range(14):
    best_count = 0
    next_todo = []
    for ahnentafel, person_num, child_num in todo:
      remove_num = child_num if args.ignore_my_line else None
      descendants = count_descendants.count_descendants(db, person_num, remove_num)
      total_descendants = sum(descendants)
      count = sum(descendants[:args.num_gens + 1]) if args.num_gens else total_descendants
      if args.print_all:
        print(gen, ahnentafel, db.num2id(person_num), db.name_of(person_num), total_descendants, count, descendants)
      if count > best_count:
        best_result = ahnentafel, person_num, descendants
        best_count = count
      # Add parents
      father_num = db.father_of(person_num)
      if father_num:
        next_todo.append((ahnentafel * 2, father_num, person_num))
      mother_num = db.mother_of(person_num)
      if mother_num:
        next_todo.append((ahnentafel * 2 + 1, mother_num, person_num))
    ahnentafel, person_num, descendants = best_result
    print("Best:", gen, ahnentafel, db.num2id(person_num), db.name_of(person_num), sum(descendants), best_count, descendants)
    todo = next_todo


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("wikitree_id")
  parser.add_argument("--version", help="Data version (defaults to most recent).")
  parser.add_argument("--ignore-my-line", action="store_true")
  parser.add_argument("--print-all", action="store_true")
  parser.add_argument("--num-gens", type=int,
                      help="Restrict num gens to look down")
  args = parser.parse_args()

  db = data_reader.Database(args.version)
  start_num = db.id2num(args.wikitree_id)

  descendants_per_ancestor(db, start_num, args)
