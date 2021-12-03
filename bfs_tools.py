"""
Breadth-first search tools for enumerating connections or relatives of a person.
"""
import collections

import data_reader


def ConnectionBfs(db, start, ignore_people=frozenset()):
  todos = collections.deque()
  dists = {}

  todos.append(start)
  dists[start] = 0

  while todos:
    person = todos.popleft()
    dist = dists[person]
    yield (person, dist)
    for neigh in db.neighbors_of(person):
      if neigh not in ignore_people and neigh not in dists:
        todos.append(neigh)
        dists[neigh] = dist + 1


def RelativeBfs(db, start):
  todos = collections.deque()
  dists = {}

  todos.append(start)
  dists[start] = (0, 0)

  while todos:
    person = todos.popleft()
    (dist_up, dist_down) = dists[person]
    yield (person, (dist_up, dist_down))
    if dist_down == 0:
      for parent in db.parents_of(person):
        if parent not in dists:
          todos.append(parent)
          dists[parent] = (dist_up + 1, dist_down)
    for child in db.children_of(person):
      if child not in dists:
        todos.append(child)
        dists[child] = (dist_up, dist_down + 1)
