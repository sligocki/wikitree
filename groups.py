import argparse
import sqlite3

import data_reader


conn = sqlite3.connect("data/groups.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

def find_group(table, person):
  cursor.execute(f"SELECT rep FROM {table} WHERE user_num=?",
                 (person,))
  rows = cursor.fetchall()
  assert len(rows) == 1, (person, rows)
  return rows[0]["rep"]


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("id_file")
  args = parser.parse_args()

  db = data_reader.Database()

  with open(args.id_file) as f:
    for line in f:
      wt_id = line.strip()
      person = db.id2num(wt_id)
      print("%-20s %s" % (wt_id, db.num2id(find_group("sibling_in_law", person))))
