import argparse
from pathlib import Path
import sqlite3
import time

import csv_iterate
import utils


def csv_to_sqlite(args):
  data_dir = utils.data_version_dir(args.version)
  conn = sqlite3.connect(Path(data_dir, "wikitree_dump.db"))
  c = conn.cursor()

  # Create output table.
  c.execute("""CREATE TABLE people (
    user_num INT, wikitree_id STRING, birth_name STRING,
    father_num INT, mother_num INT,
    birth_date DATE, death_date DATE,
    birth_location STRING, death_location STRING,
    gender_code INT,
    no_more_children BOOL, no_more_siblings BOOL,
    registered_time TIMESTAMP, touched_time TIMESTAMP,
    edit_count INT, privacy_level INT,
    manager_num INT,
    PRIMARY KEY (user_num))""")
  c.execute("CREATE TABLE relationships (user_num INT, relative_num INT, relationship_type ENUM)")

  # Iterate CSV
  i = 0
  num_rels = 0
  utils.log("Loading people from CSV")
  for person in csv_iterate.iterate_users(version=args.version):
    try:
      c.execute("INSERT INTO people VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (person.user_num(), person.wikitree_id(),
                 person.birth_name(),
                 person.father_num(), person.mother_num(),
                 person.birth_date(), person.death_date(),
                 person.birth_location(), person.death_location(),
                 person.gender_code(),
                 person.no_more_children(), person.no_more_siblings(), #person.no_more_spouses(),
                 person.registered_time(), person.touched_time(),
                 person.edit_count(), person.privacy_level(),
                 person.manager_num()))
    except Exception as e:
      print("ERROR inserting person:", person.user_num(), person.row)
      print(e)
    child_num = person.user_num()
    for parent_num in (person.father_num(), person.mother_num()):
      if parent_num:
        c.execute("INSERT INTO relationships VALUES (?,?,'parent')",
                  (child_num, parent_num))
        c.execute("INSERT INTO relationships VALUES (?,?,'child')",
                  (parent_num, child_num))
        num_rels += 2

    i += 1
    if (i % 1000000) == 0:
      utils.log(f"People: {i:_} Relationships: {num_rels:_}")
      conn.commit()
  utils.log(f"People: {i:_} Relationships: {num_rels:_}")
  conn.commit()

  utils.log("Loading marriages from CSV")
  for marriage in csv_iterate.iterate_marriages(version=args.version):
    user1, user2 = marriage.user_nums()
    c.execute("INSERT INTO relationships VALUES (?,?,'spouse')",
              (user1, user2))
    c.execute("INSERT INTO relationships VALUES (?,?,'spouse')",
              (user2, user1))
    num_rels += 2
    # Note: We are ignoring the marriage dates.
  utils.log(f"People: {i:_} Relationships: {num_rels:_}")
  conn.commit()

  utils.log("Computing siblings")
  # Siblings are two people who are both children of a third person (share a parent).
  c.execute("""
    INSERT INTO relationships SELECT a.relative_num, b.relative_num, 'sibling'
      FROM relationships AS a,
           relationships AS b
      WHERE a.relationship_type = 'child'
        AND b.relationship_type = 'child'
        AND a.user_num = b.user_num
        AND a.relative_num <> b.relative_num""")
  conn.commit()

  utils.log("Computing co-parents")
  # Co-parents are two people who are both parents of a third person (share a child).
  # They may or may not be married.
  c.execute("""
    INSERT INTO relationships SELECT a.relative_num, b.relative_num, 'coparent'
      FROM relationships AS a,
           relationships AS b
      WHERE a.relationship_type = 'parent'
        AND b.relationship_type = 'parent'
        AND a.user_num = b.user_num
        AND a.relative_num <> b.relative_num""")
  conn.commit()

  utils.log("Indexing")
  # Add indexes for fast lookup. Note: Adding them at the end is the most efficient.
  c.execute("CREATE INDEX idx_people_wikitree_id ON people(wikitree_id)")
  c.execute("CREATE INDEX idx_relationships_user ON relationships(user_num)")

  conn.commit()
  conn.close()
  utils.log("Done")


parser = argparse.ArgumentParser()
parser.add_argument("--version", help="Data version (defaults to most recent).")
args = parser.parse_args()

csv_to_sqlite(args)
