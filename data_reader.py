"""
Single interface for accessing data via either SQLite or CSV into memory.
"""

import collections
import time

import csv_iterate
import sqlite_reader


def load_connections(version,
                     include_parents,
                     include_children,
                     include_siblings,
                     include_spouses):
  connections = collections.defaultdict(set)
  children_of = collections.defaultdict(set)

  print("Loading people", time.process_time())
  num_conns = 0
  for i, person in enumerate(csv_iterate.iterate_users(version=version)):
    person_num = person.user_num()
    for parent_num in (person.father_num(), person.mother_num()):
      if parent_num:
        if include_parents:
          connections[person_num].add(parent_num)
          num_conns += 1
        if include_children:
          connections[parent_num].add(person_num)
          num_conns += 1
        if include_siblings:
          for sibling_num in children_of[parent_num]:
            connections[person_num].add(sibling_num)
            connections[sibling_num].add(person_num)
            num_conns += 2
          children_of[parent_num].add(person_num)
    if i % 1000000 == 0:
      print(" ... {:,}".format(i), "{:,}".format(num_conns), time.process_time())

  if include_spouses:
    print("Loading marriages", time.process_time())
    for marriage in csv_iterate.iterate_marriages(version=version):
      user1, user2 = marriage.user_nums()
      connections[user1].add(user2)
      connections[user2].add(user1)

  print("All connections loaded", time.process_time())
  return connections

class Database(sqlite_reader.Database):
  def __init__(self, version=None):
    super(Database, self).__init__(version)
    self.version = version
    self.connections = None

  def neighbors_of(self, person):
    if self.connections:
      return self.connections[person]
    else:
      return super(Database, self).neighbors_of(person)

  def load_connections(self):
    self.connections = load_connections(version=args.version,
                                        include_parents=True,
                                        include_children=True,
                                        include_siblings=True,
                                        include_spouses=True)
