import argparse
import collections

import data_reader
import group_tools


def connected_to(start, connections):
  """BFS and return set of all people connected to start."""
  todos = collections.deque()
  todos.append(start)
  visited = set([start])
  while todos:
    person = todos.popleft()
    for neigh in connections[person]:
      if neigh not in visited:
        todos.append(neigh)
        visited.add(neigh)
  return visited


def get_connection_groups(connections):
  """Partition people into groups based on who is connected to who.

  Returns a map {representative -> set(members)}
  """
  groups = {}
  visited = set()
  for person in connections:
    if person not in visited:
      group = connected_to(person, connections)
      visited.update(group)
      rep = min(group)
      groups[rep] = group
  return groups

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--sibling-in-law", action="store_true")
  args = parser.parse_args()

  if args.sibling_in_law:
    connections = data_reader.load_connections(include_parents=False,
                                               include_children=False,
                                               include_siblings=True,
                                               include_spouses=True)
    groups = get_connection_groups(connections)
    group_tools.write_group("sibling_in_law", groups)

  else:
    connections = data_reader.load_connections(include_parents=True,
                                               include_children=True,
                                               include_siblings=True,
                                               include_spouses=True)
    groups = get_connection_groups(connections)
    group_tools.write_group("connected", groups)
