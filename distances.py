import collections

def get_distances(connections, start):
  """Get distances to all other items in graph via breadth-first search."""
  dists = {start: 0}
  queue = collections.deque()
  queue.append(start)
  total_dist = 0
  max_dist = 0
  while queue:
    person = queue.popleft()
    dist = dists[person]
    for neigh in connections.get(person, set()):
      if neigh not in dists:
        dists[neigh] = dist + 1
        total_dist += dist + 1
        max_dist = dist + 1
        queue.append(neigh)
  return dists, float(total_dist) / len(dists), max_dist

if __name__ == "__main__":
  import sys
  import csv_dump

  connections, id2num, num2id = csv_dump.load_connections()

  for user_id in sys.argv[1:]:
    dists, d_mean, d_max = get_distances(connections, id2num[user_id])
    print user_id, d_mean, d_max
