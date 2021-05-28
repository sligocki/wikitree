import argparse
import collections

import data_reader
import partition_tools


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


def get_connection_partitions(connections):
  """Partition people into groups based on who is connected to who.

  Returns a map {representative -> set(members)}
  """
  partitions = {}
  visited = set()
  for person in connections:
    if person not in visited:
      partition = connected_to(person, connections)
      visited.update(partition)
      rep = min(partition)
      partitions[rep] = partition
  return partitions

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--version", help="Data version (defaults to most recent).")
  parser.add_argument("--sibling-in-law", action="store_true")
  args = parser.parse_args()

  partition_db = partition_tools.PartitionDb(args.version)

  if args.sibling_in_law:
    connections = data_reader.load_connections(version=args.version,
                                               include_parents=False,
                                               include_children=False,
                                               include_siblings=True,
                                               include_spouses=True)
    partitions = get_connection_partitions(connections)
    partition_db.write_partition("sibling_in_law", partitions)

  else:
    connections = data_reader.load_connections(version=args.version,
                                               include_parents=True,
                                               include_children=True,
                                               include_siblings=True,
                                               include_spouses=True)
    partitions = get_connection_partitions(connections)
    partition_db.write_partition("connected", partitions)
