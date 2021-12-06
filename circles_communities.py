import argparse
import collections

import networkit as nk

import graph_tools
import utils


parser = argparse.ArgumentParser()
parser.add_argument("focus")
parser.add_argument("graph")
parser.add_argument("communities")
parser.add_argument("--min-community-size", type=int, default=50_000)
args = parser.parse_args()

utils.log("Reading graph")
G, names_db = graph_tools.load_graph_nk(args.graph)
utils.log(f"Loaded graph with {G.numberOfNodes():_} nodes / {G.numberOfEdges():_} edges")

utils.log("Reading communities")
communities = nk.community.readCommunities(args.communities)

community_size_index = [(size, index)
                        for (index, size) in enumerate(communities.subsetSizes())
                        if size >= args.min_community_size]
community_size_index.sort(reverse=True)
large_communities = [index for (_, index) in community_size_index]

utils.log("Find distances to all nodes from focus")
comm_circles = {index: collections.Counter()
                for index in large_communities}
comm_circles["other"] = collections.Counter()
comm_circles["all"] = collections.Counter()

focus_index = names_db.name2index(args.focus)
bfs = nk.distance.BFS(G, focus_index)
bfs.run()

for dest in G.iterNodes():
  dest_comm = communities[dest]
  if dest_comm not in comm_circles:
    dest_comm = "other"
  dist = int(bfs.distance(dest))
  comm_circles[dest_comm][dist] += 1
  comm_circles["all"][dist] += 1

utils.log("Analyzing each community")
for comm in ["all"] + large_communities + ["other"]:
  size = sum(count for (dist, count) in comm_circles[comm].items())
  mean_dist = sum(dist * count for (dist, count) in comm_circles[comm].items()) / size
  mode_count, mode_dist = max((count, dist)
                              for (dist, count) in comm_circles[comm].items())
  print(f"Community {str(comm):>6s} {size=:10_d}  /  {mode_dist=:3d}  {mode_count=:9_d}  /  {mean_dist=:5.1f}")

utils.log("Finished")
