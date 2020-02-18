"""
Find closest connected people in the "Notables" or any other group.
"""

import argparse
import collections
import sqlite3

import data_reader
import group_tools


def list_distances(db, start, targets):
  dists = {start: 0}
  todo = collections.deque()
  todo.append(start)

  while todo:
    person = todo.popleft()
    dist = dists[person]
    if person in targets:
      print(dist, db.num2id(person), db.name_of(person))
    for neigh in db.neighbors_of(person):
      if neigh not in dists:
        todo.append(neigh)
        dists[neigh] = dist + 1


parser = argparse.ArgumentParser()
parser.add_argument("person_id", help="Person to search from.")
parser.add_argument("--category", default="Notables",
                    help="Category name to search for connections to.")
args = parser.parse_args()

db = data_reader.Database()
db.load_connections()

start = db.id2num(args.person_id)

conn = sqlite3.connect("data/categories.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute("SELECT user_num FROM categories WHERE category_name=?",
               (args.category,))
targets = frozenset(row["user_num"] for row in cursor.fetchall())

list_distances(db, start, targets)