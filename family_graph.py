# Produces a graph where each node is a "nuclear family unit" (representing
# 2 parents and all their children or a married couple with no children).
#
# Each family is connected to the childhood family of each of the parents.
#
# Note: This is similar to the graph created by family_bipartite_graph.py, but
# without having person nodes. It is close, but not quite the same as the
# "bipartite graph projection" from the family_bipartite onto the family nodes.
# The difference there is that that projection includes edges between
# re-marriage families (two families sharing one parent in common) of the
# same person whereas this family graph does not include an edge between
# re-marriage families.
#
# This graph will have drastically fewer cliques and running through
# graph_core.py will be much more effective.

import argparse
from pathlib import Path

import networkx as nx

import data_reader
import graph_tools
import utils


def UnionNodeName(parents):
  """Name for node which represents the union (marriage or co-parentage)."""
  return "Union/" + "/".join(str(p) for p in sorted(parents))


parser = argparse.ArgumentParser()
parser.add_argument("--version", help="Data version (defaults to most recent).")
args = parser.parse_args()

db = data_reader.Database(args.version)

graph = nx.Graph()
utils.log("Loading families")
for i, person in enumerate(db.enum_people()):
  parents = db.parents_of(person)
  if parents:
    parent_node = UnionNodeName(parents)
    for partner in db.partners_of(person):
      partner_node = UnionNodeName([person, partner])
      if partner_node != parent_node:
        # Avoid self-loops ... this shouldn't happen because a couple cannot
        # be their own parent ... but mistakes happen in WikiTree ...
        graph.add_edge(partner_node, parent_node)
  if i % 1_000_000 == 0:
    utils.log(f" ... {i:_}  {len(graph.nodes):_}  {len(graph.edges):_}")

utils.log(f"Total graph size: {len(graph.nodes):_} Nodes / {len(graph.edges):_} Edges.")

utils.log("Writing graph to file")
data_dir = utils.data_version_dir(args.version)
nx.write_adjlist(graph, Path(data_dir, "family.all.adj.nx"))

utils.log("Finding largest connected component")
main_component = graph_tools.LargestComponent(graph)
utils.log(f"Main component size: {len(main_component.nodes):_} Nodes {len(main_component.edges):_} Edges.")

utils.log("Writing main component to file")
nx.write_adjlist(main_component, Path(data_dir, "family.main.adj.nx"))

utils.log("Finished")
