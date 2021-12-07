"""
Make person graph.
"""

import argparse
from pathlib import Path

import networkit as nk

import data_reader
import graph_tools
import utils


parser = argparse.ArgumentParser()
parser.add_argument("--version", help="Data version (defaults to most recent).")
args = parser.parse_args()

utils.log("Loading DB")
db = data_reader.Database(args.version)

utils.log("Building list of all nodes and edges")
people_ids = set()
edge_ids = set()
i = 0
for person, neigh, rel_type in db.enum_connections():
  # Make sure to avoid "coparent" which is not considered a connection by connection-finder.
  if person < neigh and rel_type in ["child", "parent", "sibling", "spouse"]:
    person_id = db.num2id(person)
    neigh_id = db.num2id(neigh)
    people_ids.update([person_id, neigh_id])
    edge_ids.add((person_id, neigh_id))
    i += 1
    if i % 1000000 == 0:
      utils.log(f" ... {i:,} connections loaded")
utils.log(f"Loaded {len(people_ids):_} nodes / {len(edge_ids):_} edges")

utils.log("Index nodes")
ids = list(people_ids)
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
filename = Path(data_dir, "person.all.graph")
graph_tools.write_graph_nk(graph, ids, filename)

utils.log("Finding largest connected component")
main_component = graph_tools.largest_component_nk(graph)
print(f"Main component size: {main_component.numberOfNodes():,} Nodes / {main_component.numberOfEdges():,} Edges")

utils.log("Saving main component")
filename = Path(data_dir, "person.main.graph")
# Subset ids to those in main_component ... hopefully this order is correct/consistent ...
component_ids = [ids[index] for index in main_component.iterNodes()]
graph_tools.write_graph_nk(main_component, component_ids, filename)

utils.log("Finished")
