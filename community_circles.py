"""
Show % of each circle containing given community.
"""

import argparse
import collections

import networkit as nk

import data_reader
import graph_tools
import utils


parser = argparse.ArgumentParser()
parser.add_argument("focus")
parser.add_argument("--community_index")
parser.add_argument("--graph", required=True)
parser.add_argument("--communities", required=True)
parser.add_argument("--num-circles", type=int, default=40)
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

if args.community_index == None:
  args.community_index = communities[focus_index]

utils.log(f"% of circles around {args.focus} in community {args.community_index}:")
circle_num = 0
num_inside = 0
num_total = 0
for node in bfs.getNodesSortedByDistance():
  if bfs.distance(node) != circle_num:
    print(f" - {circle_num:3d}  {num_inside / num_total:6.2%} = {num_inside:_} / {num_total:_}")
    circle_num += 1
    num_inside = 0
    num_total = 0
    if circle_num > args.num_circles:
      break

  comm = communities[node]
  num_total += 1
  if comm == args.community_index:
    num_inside += 1
