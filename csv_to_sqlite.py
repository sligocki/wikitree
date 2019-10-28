import sqlite3
import time

import csv_iterate


def csv_to_sqlite():
  # Create output table.
  conn = sqlite3.connect("wikitree_dump.db")
  c = conn.cursor()
  c.execute("CREATE TABLE parents (child_num INT, parent_num INT)")
  c.execute("CREATE TABLE id_num (user_num INT, wikitree_id STRING)")
  # Indexes for fast lookup:
  c.execute("CREATE INDEX idx_parents_child ON parents(child_num)")
  c.execute("CREATE INDEX idx_parents_parent ON parents(parent_num)")
  c.execute("CREATE UNIQUE INDEX idx_id_num_id ON id_num(wikitree_id)")
  c.execute("CREATE UNIQUE INDEX idx_id_num_num ON id_num(user_num)")

  # Iterate CSV
  i = 0
  num_rels = 0
  for person in csv_iterate.iterate_users():
    child_num = person.user_num()
    c.execute("INSERT INTO id_num VALUES (?,?)", (child_num, person.wikitree_id()))
    for parent_num in (person.father_num(), person.mother_num()):
      if parent_num != 0:
        c.execute("INSERT INTO parents VALUES (?,?)", (child_num, parent_num))
        num_rels += 1

    i += 1
    if (i % 1000000) == 0:
      print "People: {:,}".format(i), "Relationships: {:,}".format(num_rels), "Runtime:", time.clock()
      conn.commit()

  conn.commit()
  conn.close()


csv_to_sqlite()
