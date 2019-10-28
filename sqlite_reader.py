import sqlite3


class Database(object):
  def __init__(self, filename="wikitree_dump.db"):
    self.conn = sqlite3.connect(filename)
    self.conn.row_factory = sqlite3.Row
    self.cursor = self.conn.cursor()

  def id2num(self, wikitree_id):
    self.cursor.execute("SELECT user_num FROM id_num WHERE wikitree_id=?", (wikitree_id,))
    rows = self.cursor.fetchall()
    assert len(rows) == 1, rows
    return rows[0]["user_num"]

  def num2id(self, user_num):
    self.cursor.execute("SELECT wikitree_id FROM id_num WHERE user_num=?", (user_num,))
    rows = self.cursor.fetchall()
    assert len(rows) ==1, rows
    return rows[0]["wikitree_id"]

  def parents_of(self, child_num):
    self.cursor.execute("SELECT parent_num FROM parents WHERE child_num=?", (child_num,))
    rows = self.cursor.fetchall()
    return [row["parent_num"] for row in rows]

  def children_of(self, parent_num):
    self.cursor.execute("SELECT child_num FROM parents WHERE parent_num=?", (parent_num,))
    rows = self.cursor.fetchall()
    return [row["child_num"] for row in rows]
