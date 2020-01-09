"""
Tool for reading and writing groupings (partitions) of people.

Examples: connected trees, genetic connected trees, sibling-in-laws.

No person should be in more than one group for a specific group_type.
"""

import argparse
import sqlite3

import data_reader


conn = sqlite3.connect("data/groups.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

def find_group_rep(table, person):
  cursor.execute(f"SELECT rep FROM {table} WHERE user_num=?",
                 (person,))
  rows = cursor.fetchall()
  assert len(rows) == 1, (person, rows)
  return rows[0]["rep"]


def list_group(table, rep):
  cursor.execute(f"SELECT user_num FROM {table} WHERE rep=?",
                 (rep,))
  return frozenset(row["user_num"] for row in cursor.fetchall())


def write_group(table, groups):
  # TODO: Maybe restructure this so that all groups use the same table with a group_name field.
  cursor.execute(f"DROP TABLE IF EXISTS {table}")
  cursor.execute(f"CREATE TABLE {table} (user_num INT, rep INT, PRIMARY KEY (user_num))")

  i = 0
  for rep in groups:
    for person in groups[rep]:
      cursor.execute(f"INSERT INTO {table} VALUES (?,?)",
                (person, rep))
      i += 1
      if i % 1000000 == 0:
        conn.commit()
  conn.commit()

  cursor.execute(f"CREATE INDEX idx_{table}_rep ON sibling_in_law(rep)")
  conn.commit()
  conn.close()


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("group_name")
  parser.add_argument("id_file")
  args = parser.parse_args()

  db = data_reader.Database()

  with open(args.id_file) as f:
    for line in f:
      wt_id = line.strip()
      person = db.id2num(wt_id)
      print("%-20s %s" % (wt_id, db.num2id(find_group_rep(args.group_name, person))))
