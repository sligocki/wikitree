"""
Identify communities of graph and save to file.
"""

import argparse

import networkit as nk

import graph_tools
import utils


parser = argparse.ArgumentParser()
parser.add_argument("graph")
parser.add_argument("out_communities")
args = parser.parse_args()

utils.log("Reading graph")
G, names_db = graph_tools.load_graph_nk(args.graph)
utils.log(f"Loaded graph with {G.numberOfNodes():_} nodes / {G.numberOfEdges():_} edges")

utils.log("Calculating communities")
communities = nk.community.detectCommunities(G)

utils.log("Sorting communities by size")
community_size_index = [(size, index)
                        for (index, size) in enumerate(communities.subsetSizes())]
community_size_index.sort(reverse=True)
# Convert from (arbitrary) starting community order to order descending by size.
index2order = {index: order for (order, (_, index)) in enumerate(community_size_index)}

utils.log("Writing communities to file")
with open(args.out_communities, "w") as f:
  for node in G.iterNodes():
    old_index = communities[node]
    new_order = index2order[old_index]
    f.write(f"{new_order}\n")

utils.log("Finished")
