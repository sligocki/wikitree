#!/usr/bin/env python3

import sys

import data_reader

db = data_reader.Database()

for id_or_num in sys.argv[1:]:
  try:
    user_num = int(id_or_num)
  except ValueError:
    user_num = db.id2num(id_or_num)
  print("Neighbors of:", db.name_of(user_num), db.num2id(user_num), user_num)
  neighbors = [(db.relationship_type(user_num, neigh), neigh)
               for neigh in db.neighbors_of(user_num)]
  neighbors.sort()
  for rel_type, neigh in neighbors:
    print(f" - {rel_type:10} {db.name_of(neigh):30} {db.num2id(neigh):20} {neigh:10}")
  print()
