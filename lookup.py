#!/usr/bin/env python3

import argparse

import data_reader


parser = argparse.ArgumentParser()
parser.add_argument("people", nargs="+")
parser.add_argument("--version", help="Data version (defaults to most recent).")
args = parser.parse_args()

db = data_reader.Database(args.version)

for id_or_num in args.people:
  user_num = db.get_person_num(id_or_num)
  print(db.num2id(user_num), user_num, repr(db.name_of(user_num)))
