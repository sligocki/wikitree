"""
Single interface for accessing data via either SQLite or CSV into memory.
"""

import collections

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

    for person in csv_iterate.iterate_users():
      for parent in (person.father_num(), person.mother_num()):
        if parent:
          self.connections[person].add(parent)
          self.connections[parent].add(person)
          for sibling in children_of[parent]:
            self.connections[person].add(sibling)
            self.connections[sibling].add(person)
          children_of[parent].add(person)

    for marriage in csv_iterate.iterate_marriages():
      user1, user2 = marriage.user_nums()
      self.connections[user1].add(user2)
      self.connections[user2].add(user1)
