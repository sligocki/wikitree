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


def UnionNodeName(db, parent_nums):
  """Name for node which represents the union (marriage or co-parentage)."""
  parent_ids = []
  for num in parent_nums:
    id = db.num2id(num)
    if id:
      parent_ids.append(id)
    else:
      # Fallback to num if we can't find ID (should be rare).
      #print(" Warning: No ID found for", num)
      parent_ids.append(str(num))

  return "Union/" + "/".join(str(p) for p in sorted(parent_ids))


parser = argparse.ArgumentParser()
parser.add_argument("--version", help="Data version (defaults to most recent).")
args = parser.parse_args()

db = data_reader.Database(args.version)


utils.log("Building list of all nodes and edges")
people_ids = []
union_ids = set()
edge_ids = []
for index, self_num in enumerate(db.enum_people()):
  # Add person node for self.
  self_id = db.num2id(self_num)
  people_ids.append(self_id)

  # Add union node for parents and connect to it.
  parent_nums = db.parents_of(self_num)
  if parent_nums:
    union_id = UnionNodeName(db, parent_nums)
    union_ids.add(union_id)
    edge_ids.append((self_id, union_id))

  # Add partner node for each partner and connect to it.
  for partner_num in db.partners_of(self_num):
    union_id = UnionNodeName(db, [self_num, partner_num])
    union_ids.add(union_id)
    edge_ids.append((self_id, union_id))

  if index % 1_000_000 == 0:
    utils.log(f" ... {len(people_ids):_}  {len(union_ids):_}")
utils.log(f"Found {len(people_ids):_} people nodes, {len(union_ids):_} union nodes and {len(edge_ids):_} edges.")

utils.log("Extracting id2index mapping")
ids = people_ids + list(union_ids)
id2index = {}
for node_index, wikitree_id in enumerate(ids):
  id2index[wikitree_id] = node_index


graph = nk.Graph(len(ids))
utils.log("Building graph")
for (id1, id2) in edge_ids:
  graph.addEdge(id2index[id1], id2index[id2])
utils.log(f"Built graph with {graph.numberOfNodes():_} Nodes / {graph.numberOfEdges():_} Edges")


utils.log("Saving full graph")
data_dir = utils.data_version_dir(args.version)
filename = Path(data_dir, "fam_bipartite.all.graph")
graph_tools.write_graph_nk(graph, ids, filename)

utils.log("Finding largest connected component")
main_component = graph_tools.largest_component_nk(graph)
print(f"Main component size: {main_component.numberOfNodes():,} Nodes / {main_component.numberOfEdges():,} Edges")

utils.log("Saving main component")
filename = Path(data_dir, "fam_bipartite.main.graph")
# Subset ids to those in main_component ... hopefully this order is correct/consistent ...
component_ids = [ids[index] for index in main_component.iterNodes()]
graph_tools.write_graph_nk(main_component, component_ids, filename)

utils.log("Finished")
