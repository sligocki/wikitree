import argparse
import sqlite3
import time

import csv_iterate


def csv_to_sqlite(only_update_custom=False):
  conn = sqlite3.connect("data/wikitree_dump.db")
  c = conn.cursor()

  if not only_update_custom:
    # Create output table.
    c.execute("CREATE TABLE people (user_num INT, wikitree_id STRING, birth_name STRING, birth_date DATE, death_date DATE, father_num INT, mother_num INT, PRIMARY KEY (user_num))")
    c.execute("CREATE TABLE relationships (user_num INT, relative_num INT, relationship_type ENUM)")

  # Iterate CSV
  i = 0
  num_rels = 0
  print("Loading people from CSV", time.process_time())
  for person in csv_iterate.iterate_users(only_update_custom):
    c.execute("INSERT INTO people VALUES (?,?,?,?,?,?,?)",
              (person.user_num(), person.wikitree_id(), person.birth_name(),
               person.birth_date(), person.death_date(),
               person.father_num(), person.mother_num()))
    child_num = person.user_num()
    for parent_num in (person.father_num(), person.mother_num()):
      if parent_num != 0:
        c.execute("INSERT INTO relationships VALUES (?,?,'parent')",
                  (child_num, parent_num))
        c.execute("INSERT INTO relationships VALUES (?,?,'child')",
                  (parent_num, child_num))
        num_rels += 2

    i += 1
    if (i % 1000000) == 0:
      print("People: {:,}".format(i), "Relationships: {:,}".format(num_rels), "Runtime:", time.process_time())
      conn.commit()
  print("People: {:,}".format(i), "Relationships: {:,}".format(num_rels), "Runtime:", time.process_time())
  conn.commit()

  print("Loading marriages from CSV", time.process_time())
  for marriage in csv_iterate.iterate_marriages(only_update_custom):
    user1, user2 = marriage.user_nums()
    c.execute("INSERT INTO relationships VALUES (?,?,'spouse')",
              (user1, user2))
    c.execute("INSERT INTO relationships VALUES (?,?,'spouse')",
              (user2, user1))
    num_rels += 2
    # Note: We are ignoring the marriage dates.
  print("People: {:,}".format(i), "Relationships: {:,}".format(num_rels), "Runtime:", time.process_time())
  conn.commit()

  # TODO: Figure out how to update siblings incrementally.
  if not only_update_custom:
    print("Computing siblings", time.process_time())
    c.execute("INSERT INTO relationships SELECT a.relative_num, b.relative_num, 'sibling' FROM relationships AS a, relationships AS b WHERE a.relationship_type = 'child' AND b.relationship_type = 'child' AND a.user_num = b.user_num AND a.relative_num <> b.relative_num")

  print("Done", time.process_time())
  conn.commit()

  # Add additional indexes for fast lookup.
  # Note: Adding them at the end is the most efficient.
  c.execute("CREATE INDEX idx_people_wikitree_id ON people(wikitree_id)")
  c.execute("CREATE INDEX idx_relationships_user ON relationships(user_num)")

  conn.commit()
  conn.close()


parser = argparse.ArgumentParser()
parser.add_argument("--only-update-custom", action="store_true")
args = parser.parse_args()

csv_to_sqlite(args.only_update_custom)
