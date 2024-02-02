#!/usr/bin/env python3

import argparse

import data_reader


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("people", nargs="+")
  parser.add_argument("--only-ids", action="store_true")
  parser.add_argument("--version", help="Data version (defaults to most recent).")
  args = parser.parse_args()

  db = data_reader.Database(args.version)

  for id_or_num in args.people:
    user_num = db.get_person_num(id_or_num)
    if args.only_ids:
      print(db.num2id(user_num))
    else:
      print("Neighbors of:", db.name_of(user_num), db.num2id(user_num), user_num)
    neighbors = [(db.relationship_type(user_num, neigh), neigh)
                 for neigh in db.neighbors_of(user_num)]
    neighbors.sort()
    for rel_type, neigh in neighbors:
      if args.only_ids:
        print(db.num2id(neigh))
      else:
        print(f" - {rel_type:10} {db.name_of(neigh):30} {db.num2id(neigh):20} {neigh:10}")
    print()

if __name__ == "__main__":
  main()
