import argparse
import collections
import json

import networkit as nk

import graph_tools
import utils


parser = argparse.ArgumentParser()
parser.add_argument("focus")
parser.add_argument("graph")
parser.add_argument("communities")
parser.add_argument("out_circles")
parser.add_argument("--min-community-size", type=int, default=1000)
args = parser.parse_args()

utils.log("Reading graph")
G, names_db = graph_tools.load_graph_nk(args.graph)
utils.log(f"Loaded graph with {G.numberOfNodes():_} nodes / {G.numberOfEdges():_} edges")

utils.log("Reading communities")
communities = nk.community.readCommunities(args.communities)

community_size_index = [(size, index)
                        for (index, size) in enumerate(communities.subsetSizes())]
community_size_index.sort(reverse=True)
sorted_comms = [index for (size, index) in community_size_index
               if size >= args.min_community_size]

utils.log("Find distances to all nodes from focus")
comm_circles = {index: collections.Counter()
                for index in sorted_comms}
comm_circles["all"] = collections.Counter()

focus_index = names_db.name2index(args.focus)
bfs = nk.distance.BFS(G, focus_index)
bfs.run()

for dest in G.iterNodes():
  dest_comm = communities[dest]
  dist = int(bfs.distance(dest))
  if dest_comm in comm_circles:
    comm_circles[dest_comm][dist] += 1
  comm_circles["all"][dist] += 1

utils.log("Analyzing largest communities")
for comm in ["all"] + sorted_comms[:20]:
  size = sum(count for (dist, count) in comm_circles[comm].items())
  mean_dist = sum(dist * count for (dist, count) in comm_circles[comm].items()) / size
  mode_count, mode_dist = max((count, dist)
                              for (dist, count) in comm_circles[comm].items())
  print(f"Community {str(comm):>6s} {size=:10_d}  /  {mode_dist=:3d}  {mode_count=:9_d}  /  {mean_dist=:5.1f}")

utils.log("Writing circles to file")
circles_json = {}
for comm in ["all"] + sorted_comms:
  name = f"{args.focus}/Community_{comm}"
  circles_json[name] = [comm_circles[comm][i]
                        for i in range(max(comm_circles[comm].keys()) + 1)]

with open(args.out_circles, "w") as f:
  json.dump(circles_json, f)

utils.log("Finished")
