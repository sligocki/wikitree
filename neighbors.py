#!/usr/bin/env python3

import argparse

import data_reader


parser = argparse.ArgumentParser()
parser.add_argument("people", nargs="+")

parser.add_argument("--version", help="Data version (defaults to most recent).")
parser.add_argument("--load-db", action="store_true")
args = parser.parse_args()

db = data_reader.Database(args.version)

for id_or_num in args.people:
  user_num = db.get_person_num(id_or_num)
  print("Neighbors of:", db.name_of(user_num), db.num2id(user_num), user_num)
  neighbors = [(db.relationship_type(user_num, neigh), neigh)
               for neigh in db.neighbors_of(user_num)]
  neighbors.sort()
  for rel_type, neigh in neighbors:
    print(f" - {rel_type:10} {db.name_of(neigh):30} {db.num2id(neigh):20} {neigh:10}")
  print()
