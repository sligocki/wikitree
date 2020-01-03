"""
Single interface for accessing data via either SQLite or CSV into memory.
"""

import collections
import time

import csv_iterate
import sqlite_reader

class Database(sqlite_reader.Database):
  def __init__(self):
    super(Database, self).__init__()
    self.connections = None

  def neighbors_of(self, person):
    if self.connections:
      return self.connections[person]
    else:
      return super(Database, self).neighbors_of(person)

  def load_connections(self):
    self.connections = collections.defaultdict(set)
    children_of = collections.defaultdict(set)

    print("Loading people", time.clock())
    num_conns = 0
    for i, person in enumerate(csv_iterate.iterate_users()):
      person_num = person.user_num()
      for parent_num in (person.father_num(), person.mother_num()):
        if parent_num:
          self.connections[person_num].add(parent_num)
          self.connections[parent_num].add(person_num)
          num_conns += 2
          for sibling_num in children_of[parent_num]:
            self.connections[person_num].add(sibling_num)
            self.connections[sibling_num].add(person_num)
            num_conns += 2
          children_of[parent_num].add(person_num)
      if i % 1000000 == 0:
        print(" ... {:,}".format(i), "{:,}".format(num_conns), time.clock())

    print("Loading marriages", time.clock())
    for marriage in csv_iterate.iterate_marriages():
      user1, user2 = marriage.user_nums()
      self.connections[user1].add(user2)
      self.connections[user2].add(user1)
    print("All connections loaded", time.clock())
