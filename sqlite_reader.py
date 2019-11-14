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

  def id2num(self, wikitree_id):
    self.cursor.execute("SELECT user_num FROM people WHERE wikitree_id=?", (wikitree_id,))
    rows = self.cursor.fetchall()
    assert len(rows) == 1, (wikitree_id, rows)
    return rows[0]["user_num"]

  def num2id(self, user_num):
    self.cursor.execute("SELECT wikitree_id FROM people WHERE user_num=?", (user_num,))
    rows = self.cursor.fetchall()
    assert len(rows) == 1, (user_num, rows)
    return rows[0]["wikitree_id"]

  def name_of(self, user_num):
    self.cursor.execute("SELECT birth_name FROM people WHERE user_num=?", (user_num,))
    rows = self.cursor.fetchall()
    assert len(rows) == 1, (user_num, rows)
    return rows[0]["birth_name"]

  def neighbors_of(self, user_num):
    self.cursor.execute("SELECT relative_num FROM relationships WHERE user_num=?", (user_num,))
    rows = self.cursor.fetchall()
    return frozenset(row["relative_num"] for row in rows)

  def father_of(self, child_num):
    self.cursor.execute("SELECT father_num FROM people WHERE user_num=?", (child_num,))
    rows = self.cursor.fetchall()
    if rows:
      assert len(rows) == 1, (child_num, rows)
      return rows[0]["father_num"]

  def mother_of(self, child_num):
    self.cursor.execute("SELECT mother_num FROM people WHERE user_num=?", (child_num,))
    rows = self.cursor.fetchall()
    if rows:
      assert len(rows) == 1, (child_num, rows)
      return rows[0]["mother_num"]

  def children_of(self, parent_num):
    self.cursor.execute("SELECT relative_num FROM relationships WHERE user_num=? AND relationship_type = 'child'", (parent_num,))
    rows = self.cursor.fetchall()
    return frozenset(row["relative_num"] for row in rows)

  def relationship_type(self, user_num, relative_num):
    self.cursor.execute("SELECT relationship_type FROM relationships WHERE user_num=? AND relative_num=?", (user_num, relative_num))
    rows = self.cursor.fetchall()
    assert len(rows) >= 1, (user_num, relative_num, rows)
    return rows[0]["relationship_type"]
