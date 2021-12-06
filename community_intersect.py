"""
Intersect multiple community partitions into a single partition.
Communities in this "intersection partition" are the collections of people who
were categorized into the same community in all input partitions.
"""

import argparse
import collections

import networkit as nk

import graph_tools
import utils


parser = argparse.ArgumentParser()
parser.add_argument("graph")
parser.add_argument("in_communities", nargs="+")
parser.add_argument("--out-communities")
args = parser.parse_args()

utils.log("Reading graph")
G, names_db = graph_tools.load_graph_nk(args.graph)
utils.log(f"Loaded graph with {G.numberOfNodes():_} nodes / {G.numberOfEdges():_} edges")

utils.log(f"Reading {len(args.in_communities)} partitions")
partitions = [nk.community.readCommunities(community_file)
              for community_file in args.in_communities]

utils.log("Calculating the intersection of all partitions")
intersect_partition = collections.defaultdict(list)
node2comm = {}
for node in G.iterNodes():
  all_comms = [partition[node] for partition in partitions]
  intersect_name = ",".join(str(comm) for comm in all_comms)
  node2comm[node] = intersect_name
  intersect_partition[intersect_name].append(node)
utils.log(f"Found {len(intersect_partition)} partition intersections")

utils.log("Sorting intersections by size")
size_part = [(len(nodes), name) for (name, nodes) in intersect_partition.items()]
size_part.sort(reverse=True)
name2index = {name: index for (index, (_, name)) in enumerate(size_part)}

utils.log("Writing intersections")
with open(args.out_communities, "w") as f:
  for node in G.iterNodes():
    comm_name = node2comm[node]
    comm_index = name2index[comm_name]
    f.write(f"{comm_index}\n")

utils.log("Finished")
