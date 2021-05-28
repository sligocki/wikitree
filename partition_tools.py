"""
Tool for reading and writing partitions (groupings) of people.

Examples: connected trees, genetic connected trees, sibling-in-laws.
"""

import argparse
from pathlib import Path
import sqlite3

import data_reader
import utils


class PartitionDb:
  def __init__(self, version=None):
    self.filename = Path(utils.data_version_dir(version), "partitions.db")
    self.conn = sqlite3.connect(self.filename)
    self.conn.row_factory = sqlite3.Row
    self.cursor = self.conn.cursor()

  def find_partition_rep(self, table, person):
    self.cursor.execute(f"SELECT rep FROM {table} WHERE user_num=?",
                   (person,))
    rows = self.cursor.fetchall()
    assert len(rows) == 1, (person, rows)
    return rows[0]["rep"]


  def list_partition(self, table, rep):
    self.cursor.execute(f"SELECT user_num FROM {table} WHERE rep=?", (rep,))
    return frozenset(row["user_num"] for row in self.cursor.fetchall())


  def write_partition(self, table, partitions):
    # TODO: Maybe restructure this so that all partitions use the same table with a partition_type field.
    self.cursor.execute(f"DROP TABLE IF EXISTS {table}")
    self.cursor.execute(f"CREATE TABLE {table} (user_num INT, rep INT, PRIMARY KEY (user_num))")

    i = 0
    for rep in partitions:
      for person in partitions[rep]:
        self.cursor.execute(f"INSERT INTO {table} VALUES (?,?)",
                  (person, rep))
        i += 1
        if i % 1000000 == 0:
          self.conn.commit()
    self.conn.commit()

    self.cursor.execute(f"CREATE INDEX idx_{table}_rep ON sibling_in_law(rep)")
    self.conn.commit()


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("partition_name")
  parser.add_argument("id_file")
  args = parser.parse_args()

  db = data_reader.Database()
  partition_db = PartitionDb()

  with open(args.id_file) as f:
    for line in f:
      wt_id = line.strip()
      person = db.id2num(wt_id)
      rep_num = partition_db.find_partition_rep(args.partition_name, person)
      print("%-20s %s" % (wt_id, db.num2id(rep_num)))
