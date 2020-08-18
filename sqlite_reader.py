import datetime
import sqlite3


# TODO:
#class User(object):
#  def __init__(self, db, user_num):
#    self.db = db
#    self.user_num = user_num


class Database(object):
  def __init__(self, filename="data/wikitree_dump.db"):
    self.conn = sqlite3.connect(filename)
    self.conn.row_factory = sqlite3.Row
    self.cursor = self.conn.cursor()

  def get(self, user_num, attribute):
    self.cursor.execute(f"SELECT {attribute} FROM people WHERE user_num=?", (user_num,))
    rows = self.cursor.fetchall()
    if rows:
      assert len(rows) == 1, (child_num, rows)
      return rows[0][0]

  def id2num(self, wikitree_id):
    self.cursor.execute("SELECT user_num FROM people WHERE wikitree_id=?", (wikitree_id,))
    rows = self.cursor.fetchall()
    assert len(rows) == 1, (wikitree_id, rows)
    return rows[0]["user_num"]

  def num2id(self, user_num):
    return self.get(user_num, "wikitree_id")

  def name_of(self, user_num):
    return self.get(user_num, "birth_name")

  def birth_date_of(self, user_num):
    date_str = self.get(user_num, "birth_date")
    if date_str:
      return datetime.date.fromisoformat(date_str)

  def father_of(self, user_num):
    return self.get(user_num, "father_num")

  def mother_of(self, user_num):
    return self.get(user_num, "mother_num")

  def parents_of(self, user_num):
    return frozenset(
      p for p in (self.father_of(user_num), self.mother_of(user_num)) if p)

  def has_person(self, user_num):
    self.cursor.execute("SELECT 1 FROM people WHERE user_num=?", (user_num,))
    rows = self.cursor.fetchall()
    return len(rows) > 0

  def enum_people(self):
    cursor = self.conn.cursor()
    cursor.execute("SELECT user_num FROM people")
    while True:
      row = cursor.fetchone()
      if not row:
        return
      yield row["user_num"]


  def neighbors_of(self, user_num):
    self.cursor.execute("SELECT relative_num FROM relationships WHERE user_num=?", (user_num,))
    rows = self.cursor.fetchall()
    return frozenset(row["relative_num"] for row in rows)

  def relative_of(self, user_num, relationship_type):
    self.cursor.execute("SELECT relative_num FROM relationships WHERE user_num = ? AND relationship_type = ?", (user_num, relationship_type))
    rows = self.cursor.fetchall()
    return frozenset(row["relative_num"] for row in rows)

  def relative_of_mult(self, user_num, relationship_types):
    self.cursor.execute("SELECT relative_num, relationship_type FROM relationships WHERE user_num=?", (user_num,))
    rows = self.cursor.fetchall()
    return frozenset(row["relative_num"] for row in rows
                     if row["relationship_type"] in relationship_types)

  def children_of(self, parent_num):
    return self.relative_of(parent_num, "child")

  def siblings_of(self, user_num):
    return self.relative_of(user_num, "sibling")

  def spouses_of(self, user_num):
    return self.relative_of(user_num, "spouse")

  def relationship_type(self, user_num, relative_num):
    self.cursor.execute("SELECT relationship_type FROM relationships WHERE user_num=? AND relative_num=?", (user_num, relative_num))
    rows = self.cursor.fetchall()
    assert len(rows) >= 1, (user_num, relative_num, rows)
    return rows[0]["relationship_type"]

  def enum_connections(self):
    cursor = self.conn.cursor()
    cursor.execute("SELECT user_num, relative_num FROM relationships")
    while True:
      row = cursor.fetchone()
      if not row:
        return
      yield (row["user_num"], row["relative_num"])
