"""
Tool for reading and writing partitions (groupings) of people.

Examples: connected trees, genetic connected trees, sibling-in-laws.
"""

import argparse
from collections.abc import Sequence
from pathlib import Path
import sqlite3
from typing import Iterator

import data_reader
import utils


class PartitionDb:
  def __init__(self, version : str) -> None:
    self.filename = Path(utils.data_version_dir(version), "partitions.db")
    self.conn = sqlite3.connect(self.filename)
    self.conn.row_factory = sqlite3.Row

  # Readers
  def find_partition_rep(self, table : str, person : int) -> int:
    cursor = self.conn.cursor()
    cursor.execute(f"SELECT rep FROM {table} WHERE user_num=?",
                   (person,))
    rows = cursor.fetchall()
    assert len(rows) == 1, (person, rows)
    return rows[0]["rep"]

  def list_partition(self, table : str, rep : int) -> frozenset[int]:
    cursor = self.conn.cursor()
    cursor.execute(f"SELECT user_num FROM {table} WHERE rep=?", (rep,))
    return frozenset(row["user_num"] for row in cursor.fetchall())

  def main_component_rep(self, table : str) -> int:
    # Note: I just pick the component that Samuel Lothrop (Lothrop-29) belongs
    # to. He is one of the most central profiles on WikiTree. This is certainly
    # the correct component for the `connected` graph. For other partitions,
    # it may not be the largest component ...
    return self.find_partition_rep(table, 142891)  # Lothrop-29

  def enum_all(self, table : str) -> Iterator:
    cursor = self.conn.cursor()
    cursor.execute(f"SELECT user_num, rep FROM {table}")
    while row := cursor.fetchone():
      yield row


  # Writers
  def write_partition(self, table : str,
                      partitions : dict[int, Sequence[int]]) -> None:
    # TODO: Maybe restructure this so that all partitions use the same table with a partition_type field.
    cursor = self.conn.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS {table}")
    cursor.execute(f"CREATE TABLE {table} (user_num INT, rep INT, PRIMARY KEY (user_num))")

    i = 0
    for rep in partitions:
      for person in partitions[rep]:
        cursor.execute(f"INSERT INTO {table} VALUES (?,?)",
                  (person, rep))
        i += 1
        if i % 1000000 == 0:
          self.conn.commit()
    self.conn.commit()

    cursor.execute(f"CREATE INDEX idx_{table}_rep ON {table} (rep)")
    self.conn.commit()


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("partition_name")
  parser.add_argument("id_file")
  args = parser.parse_args()

  db = data_reader.Database("default")
  partition_db = PartitionDb("default")

  with open(args.id_file) as f:
    for line in f:
      wt_id = line.strip()
      person = db.id2num(wt_id)
      rep_num = partition_db.find_partition_rep(args.partition_name, person)
      print("%-20s %s" % (wt_id, db.num2id(rep_num)))
