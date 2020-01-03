"""
Load N people around a person and output in graph format.
"""



import argparse
import collections

import data_reader


def Bfs(db, start):
  todos = collections.deque()
  visited = set()

  todos.append(start)
  visited.add(start)

  while todos:
    person = todos.popleft()
    yield person
    for neigh in db.neighbors_of(person):
      if neigh not in visited:
        todos.append(neigh)
        visited.add(neigh)


def get_subset(db, start, num_people):
  subset = set()
  for person in Bfs(db, start):
    subset.add(person)
    if len(subset) >= num_people:
      return subset


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("start_id")
  parser.add_argument("--num-people", type=int, default=10000)
  args = parser.parse_args()

  db = data_reader.Database()

  start = db.id2num(args.start_id)

  subset = get_subset(db, start, args.num_people)

  for person in subset:
    neighs = [neigh for neigh in db.neighbors_of(person) if neigh in subset]
    print(person, *neighs)
