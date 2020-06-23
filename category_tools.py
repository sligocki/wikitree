import sqlite3


conn = sqlite3.connect("data/categories.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

def list_category(category_name):
  cursor.execute("SELECT user_num FROM categories WHERE category_name=?",
                 (category_name,))
  return frozenset(row["user_num"] for row in cursor.fetchall())
