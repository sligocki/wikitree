import collections
import sqlite3
import sys
import time

import data_reader

results_conn = sqlite3.connect("distances.db")
results_conn.row_factory = sqlite3.Row

def get_distances(db, start):
  """Get distances to all other items in graph via breadth-first search."""
  dists = {start: 0}
  queue = collections.deque()
  queue.append(start)
  total_dist = 0
  max_dist = 0
  hist_dist = []
  while queue:
    person = queue.popleft()
    dist = dists[person]
    for neigh in db.neighbors_of(person):
      if neigh not in dists:
        dists[neigh] = dist + 1
        total_dist += dist + 1
        max_dist = dist + 1
        while len(hist_dist) <= dist + 1:
          hist_dist.append(0)
        hist_dist[dist + 1] += 1
        queue.append(neigh)
        #if len(dists) % 1000000 == 0:
        #  print "...", len(dists), max_dist, float(total_dist) / len(dists), time.clock()
  mean_dist = float(total_dist) / len(dists)
  return dists, hist_dist, mean_dist, max_dist

def get_mean_dists(db, start):
  c = results_conn.cursor()
  c.execute("SELECT mean_dist, max_dist FROM distances WHERE user_num=?", (start,))
  rows = c.fetchall()
  if rows:
    assert len(rows) == 1, rows
    return rows[0]["mean_dist"], rows[0]["max_dist"]
  else:
    _, _, mean_dist, max_dist = get_distances(db, start)
    try:
      results_conn.execute("INSERT INTO distances VALUES (?,?,?)", (start, mean_dist, max_dist))
      results_conn.commit()
    except e:
      print "Ignoring distances.db write failure:", e
    return mean_dist, max_dist

if __name__ == "__main__":
  db = data_reader.Database()
  db.load_connections()

  for wikitree_id in sys.argv[1:]:
    user_num = db.id2num(wikitree_id)
    print
    dists, d_hist, d_mean, d_max = get_distances(db, user_num)
    print
    #cum_count = 0
    #for dist, count in enumerate(d_hist):
    #  cum_count += count
    #  print dist, count, cum_count
    print wikitree_id, d_mean, d_max, len(dists), time.clock()
