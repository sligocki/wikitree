"""
Breadth-first search tools for enumerating connections or relatives of a person.
"""
import collections
from collections.abc import Set
from typing import Iterator

import data_reader
from data_reader import UserNum


class BfsNode:
  def __init__(self, person : UserNum, prevs : list[UserNum],
               dist : int) -> None:
    # Currently enumerated person.
    self.person = person
    # List of previous nodes we reached person from.
    self.prevs = prevs
    # Dist from start to person.
    self.dist = dist

  def __repr__(self) -> str:
    return f"BfsNode({self.person}, {self.prevs}, {self.dist})"

def ConnectionBfs(db : data_reader.Database,
                  start : UserNum,
                  ignore_people : Set[UserNum] = frozenset()
                  ) -> Iterator[BfsNode]:
  todos : collections.deque[UserNum] = collections.deque()
  todos.append(start)
  nodes = {start: BfsNode(start, [], 0)}
  while todos:
    person = todos.popleft()
    yield nodes[person]
    dist = nodes[person].dist
    for neigh in db.neighbors_of(person):
      if neigh not in ignore_people:
        if neigh in nodes:
          if nodes[neigh].dist == dist + 1:
            # If we have reached neigh equivalently from two
            # different directions, save both.
            nodes[neigh].prevs.append(person)
        else:
          todos.append(neigh)
          nodes[neigh] = BfsNode(neigh, [person], dist + 1)


def RelativeBfs(db : data_reader.Database, start : UserNum
                ) -> Iterator[tuple[UserNum, tuple[int, int]]]:
  todos : collections.deque[UserNum] = collections.deque()
  todos.append(start)
  dists = {start: (0, 0)}

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
