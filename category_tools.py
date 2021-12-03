from pathlib import Path
import sqlite3

import utils


class CategoryDb:
  def __init__(self, version):
    self.filename = Path(utils.data_version_dir(version), "categories.db")
    self.conn = sqlite3.connect(self.filename)
    self.conn.row_factory = sqlite3.Row

  def list_categories_for_preson(self, user_num):
    cursor = self.conn.cursor()
    cursor.execute("SELECT category_name FROM categories WHERE user_num=?",
                   (user_num,))
    return frozenset(row["category_name"] for row in cursor.fetchall())

  def list_people_in_category(self, category_name):
    cursor = self.conn.cursor()
    cursor.execute("SELECT user_num FROM categories WHERE category_name=?",
                   (category_name,))
    return frozenset(row["user_num"] for row in cursor.fetchall())
