import sqlite3

import csv_iterate


def csv_to_sqlite():
  # Create output table.
  conn = sqlite3.connect("wikitree_dump.db")
  c = conn.cursor()
  c.execute("CREATE TABLE parents (child_num INT, parent_num INT)")

  # Iterate CSV
  i = 0
  num_rels = 0
  for person in csv_iterate.iterate_users():
    child_num = person.user_num()
    for parent_num in (person.father_num(), person.mother_num()):
      if parent_num != 0:
        c.execute("INSERT INTO parents VALUES (?,?)", (child_num, parent_num))
        num_rels += 1

    i += 1
    if (i % 100000) == 0:
      print "People: {:,}".format(i), "Relationships: {:,}".format(num_rels)
      conn.commit()

  conn.commit()
  conn.close()


csv_to_sqlite()
