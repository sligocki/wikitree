"""
Produces a graph where each node is a "nuclear family unit" (representing
2 parents and all their children or a married couple with no children).

Each family is connected to the childhood family of each of the parents.

Note: This is similar to the graph created by graph_make_family_bipartite.py,
but without having person nodes. It is close, but not quite the same as the
"bipartite graph projection" from the family_bipartite onto the family nodes.
The difference there is that that projection includes edges between
re-marriage families (two families sharing one parent in common) of the
same person whereas this family graph does not include an edge between
re-marriage families.

This graph will have drastically fewer cliques and running through
graph_core.py will be much more effective.
"""

import argparse
from pathlib import Path

import networkit as nk

import data_reader
import graph_tools
import utils


def try_num2id(db, num):
  id = db.num2id(num)
  if id:
    return id
  else:
    # Fallback to num if we can't find ID (should be rare).
    return str(num)

def UnionNodeName(db, parent_nums):
  """Name for node which represents the union (marriage or co-parentage)."""
  parent_ids = [try_num2id(db, num) for num in parent_nums]
  return "Union/" + "/".join(str(p) for p in sorted(parent_ids))

def VirtualParentNodeName(person):
  return f"Parents/{person}"


parser = argparse.ArgumentParser()
parser.add_argument("--version", help="Data version (defaults to most recent).")
args = parser.parse_args()

db = data_reader.Database(args.version)

utils.log("Building list of all nodes and edges")
node_ids = set()
edge_ids = []
for i, person in enumerate(db.enum_people()):
  parents = db.parents_of(person)
  partners = db.partners_of(person)

  if parents:
    parent_node = UnionNodeName(db, parents)
  elif len(partners) > 1:
    # If no parents are listed, but this person has multiple unions, then we
    # create a virtual node for this person's birth family. We do this so that
    # the multiple unions of person will all be connected together.
    parent_node = VirtualParentNodeName(try_num2id(db, person))
  else:
    parent_node = None

  if parent_node:
    for partner in partners:
      partner_node = UnionNodeName(db, [person, partner])
      if partner_node != parent_node:
        node_ids.update([partner_node, parent_node])
        # Avoid self-loops ... this shouldn't happen in reality because a
        # couple cannot be their own parent ... but mistakes happen in WikiTree ...
        edge_ids.append((partner_node, parent_node))

  if i % 1_000_000 == 0:
    utils.log(f" ... {i:_}  {len(node_ids):_}  {len(edge_ids):_}")
utils.log(f"Loaded {len(node_ids):_} nodes / {len(edge_ids):_} edges")

utils.log("Index nodes")
ids = list(node_ids)
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
filename = Path(data_dir, "family.all.graph")
graph_tools.write_graph_nk(graph, ids, filename)

utils.log("Finding largest connected component")
main_component = graph_tools.largest_component_nk(graph)
print(f"Main component size: {main_component.numberOfNodes():,} Nodes / {main_component.numberOfEdges():,} Edges")

utils.log("Saving main component")
filename = Path(data_dir, "family.main.graph")
# Subset ids to those in main_component ... hopefully this order is correct/consistent ...
component_ids = [ids[index] for index in main_component.iterNodes()]
graph_tools.write_graph_nk(main_component, component_ids, filename)

utils.log("Finished")
