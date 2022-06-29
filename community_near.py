"""
List communities near the focus person.
"""

import argparse
import collections

import networkit as nk

import data_reader
import graph_tools
import utils


parser = argparse.ArgumentParser()
parser.add_argument("focus")
parser.add_argument("graph")
parser.add_argument("communities")
parser.add_argument("--num-communities", type=int, default=40)
parser.add_argument("--min-community-size", type=int, default=1000)
args = parser.parse_args()

utils.log("Reading graph")
G, names_db = graph_tools.load_graph_nk(args.graph)
utils.log(f"Loaded graph with {G.numberOfNodes():_} nodes / {G.numberOfEdges():_} edges")

utils.log("Reading communities")
communities = nk.community.readCommunities(args.communities)

utils.log("Computing Single-Source Shortest Paths")
focus_index = names_db.name2index(args.focus)
bfs = nk.distance.BFS(G, focus_index, storeNodesSortedByDistance=True)
bfs.run()

utils.log("Nearest communities:")
visited = set()
num_communities_printed = 0
for node in bfs.getNodesSortedByDistance():
  comm = communities[node]
  if comm not in visited:
    visited.add(comm)
    comm_size = communities.subsetSizes()[comm]
    if comm_size >= args.min_community_size:
      print(f" - {int(bfs.distance(node)):3d}  /  Community {comm:7_d} (size: {comm_size:7_d})  /  {names_db.index2name(node)}")
      num_communities_printed += 1
      if num_communities_printed >= args.num_communities:
        break
