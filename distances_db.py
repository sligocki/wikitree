import sqlite3

conn = sqlite3.connect("data/distances.db", timeout=20)
conn.row_factory = sqlite3.Row
conn.execute("CREATE TABLE IF NOT EXISTS distances (graph STRING, node STRING, mean_dist REAL, randomly_sampled BOOL)")

def LogDistance(graph, node, mean_dist, randomly_sampled):
  try:
    conn.execute("INSERT INTO distances VALUES (?, ?, ?, ?)", (graph, node, mean_dist, randomly_sampled))
    conn.commit()
    return True
  except sqlite3.OperationalError:
    print("!!! SQLite error !!!")
    return False
