"""
Produces a graph representing "nuclear family units".

Represented as a bipartite graph where each node is either:
 * a person or
 * a family unit (representing 2 parents and all their children
                  or a married couple with no children)
Every person is connected to every family unit they are a member of.

Note: This is similar to the graph created by graph_make_family.py, see the
comments in that file to understand the difference.

In the traditional connection graph, there are many highly connected blocks.
For example, given 2 parents with 4 children, all 6 will be directly connected
to each other. But does this really represent 15 different connections?

Instead, in this representation it would be represented as a star of 6 person
nodes attached to a central family node.

The resulting graph will have drastically fewer cliques and running through
graph_core.py will be much more effective.
"""

import argparse
import collections
from pathlib import Path

import networkit as nk

import data_reader
import graph_tools
import utils


def id_or_num(db, num):
  id = db.num2id(num)
  if id:
    return id
  else:
    # Fallback to num if we can't find ID (should be rare).
    return str(num)

def UnionNodeName(db, parent_nums):
  """Name for node which represents the union (marriage or co-parentage)."""
  parent_ids = []
  for num in parent_nums:
    parent_ids.append(id_or_num(db, num))

  return "Union/" + "/".join(str(p) for p in sorted(parent_ids))

class BipartiteBuilder:
  def __init__(self, db):
    self.db = db
    self.people_ids = set()
    self.union_ids = set()
    self.edge_ids = set()

  def compute_node_ids(self):
    return list(self.people_ids) + list(self.union_ids)

  def add_person(self, self_num):
    # Add person node for self.
    self_id = id_or_num(self.db, self_num)
    self.people_ids.add(self_id)

    # Add union node for parents and connect to it.
    parent_nums = self.db.parents_of(self_num)
    if parent_nums:
      union_id = UnionNodeName(self.db, parent_nums)
      self.union_ids.add(union_id)
      self.edge_ids.add((self_id, union_id))
      # Make sure parents are connected ... this will generally happen
      # automatically below with the partners iteration (unless one parent is unknown).
      for parent_num in parent_nums:
        parent_id = id_or_num(self.db, parent_num)
        self.people_ids.add(parent_id)
        self.edge_ids.add((parent_id, union_id))

    # Add partner node for each partner and connect to it.
    for partner_num in self.db.partners_of(self_num):
      union_id = UnionNodeName(self.db, [self_num, partner_num])
      self.union_ids.add(union_id)
      self.edge_ids.add((self_id, union_id))
      # Explicitly add partner as well ... this shouldn't be necessary, but
      # some private partners may not be in the DB.
      partner_id = id_or_num(self.db, partner_num)
      self.people_ids.add(partner_id)
      self.edge_ids.add((partner_id, union_id))


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--version", help="Data version (defaults to most recent).")
  args = parser.parse_args()

  db = data_reader.Database(args.version)

  utils.log("Building list of all nodes and edges")
  graph_info = BipartiteBuilder(db)
  for index, user_num in enumerate(db.enum_people()):
    graph_info.add_person(user_num)
    if index % 1_000_000 == 0:
      utils.log(f" ... {len(graph_info.people_ids):_}  {len(graph_info.union_ids):_}")
  utils.log(f"Found {len(graph_info.people_ids):_} people nodes, {len(graph_info.union_ids):_} union nodes and {len(graph_info.edge_ids):_} edges.")

  graph = graph_tools.make_graph(graph_info.compute_node_ids(), graph_info.edge_ids)
  utils.log(f"Built graph with {len(graph.nodes):_} Nodes / {len(graph.edges):_} Edges")

  utils.log("Saving full graph")
  data_dir = utils.data_version_dir(args.version)
  filename = Path(data_dir, "bipartite.all.graph.adj.nx")
  graph_tools.write_graph(graph, filename)

  utils.log("Finding largest connected component")
  main_component = graph_tools.largest_component(graph)
  print(f"Main component size: {len(main_component.nodes):_} Nodes / {len(main_component.edges):_} Edges")

  utils.log("Saving main component")
  filename = Path(data_dir, "bipartite.main.graph.adj.nx")
  graph_tools.write_graph(main_component, filename)

  utils.log("Finished")


if __name__ == "__main__":
  main()
