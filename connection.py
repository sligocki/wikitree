import collections
import sys
import time

import csv_load
from distances import get_distances
import sqlite_reader


class Bfs(object):
  def __init__(self, user_num):
    self.user_num = user_num
    # Example shortest path to each other person.
    self.path = {user_num: ()}
    self.todo = [user_num]
    self.num_steps = 0

  def next_gen(self):
    """Enumerate next generation of connections."""
    self.num_steps += 1
    next_todo = []
    for person in self.todo:
      path = self.path[person]
      for neigh in db.neighbors_of(person):
        if neigh not in self.path:
          self.path[neigh] = path + (person,)
          next_todo.append(neigh)
          yield neigh
    self.todo = next_todo


def find_connection(person1, person2):
  bfs1 = Bfs(person1)
  bfs2 = Bfs(person2)

  while True:
    if len(bfs1.todo) <= len(bfs2.todo):
      this = bfs1
      other = bfs2
    else:
      this = bfs2
      other = bfs1

    for person in this.next_gen():
      if person in other.path:
        # Done, we found a common person.
        # TODO: Find all connections of this length.
        print "Evaluated %d (%d around %s) & %d (%d around %s)" % (
          len(bfs1.path), bfs1.num_steps, person1_id, len(bfs2.path), bfs2.num_steps, person2_id)
        return bfs1.path[person] + (person,) + tuple(reversed(bfs2.path[person]))


person1_id = unicode(sys.argv[1], encoding="utf-8", errors="strict")
person2_id = unicode(sys.argv[2], encoding="utf-8", errors="strict")

db = sqlite_reader.Database()
#db = csv_load.CsvLoad()
#db.load_all()

person1 = db.id2num(person1_id)
person2 = db.id2num(person2_id)

connection = find_connection(person1, person2)

print "Connection from", person1_id, "to", person2_id
for dist, user_num in enumerate(connection):
  print dist, db.num2id(user_num), db.name_of(user_num)
