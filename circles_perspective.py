import argparse
import collections

import networkit as nk

import graph_tools
import utils


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("focus_a")
  parser.add_argument("circle_num", type=int)
  parser.add_argument("focus_b")
  parser.add_argument("--graph")
  args = parser.parse_args()

  utils.log("Reading graph")
  G, names_db = graph_tools.load_graph_nk(args.graph)
  utils.log(f"Loaded graph with {G.numberOfNodes():_} nodes / {G.numberOfEdges():_} edges")

  utils.log("Computing BFS around focus_a")
  focus_index = names_db.name2index(args.focus_a)
  bfs = nk.distance.BFS(G, focus_index)
  bfs.run()

  utils.log(f"Identifying all nodes in circle {args.circle_num}")
  circle = set()
  for node in G.iterNodes():
    if int(bfs.distance(node)) == args.circle_num:
      circle.add(node)
  utils.log(f"Found {len(circle):_} nodes at dist {args.circle_num}")


  utils.log("Computing BFS around focus_b")
  focus_index = names_db.name2index(args.focus_b)
  bfs = nk.distance.BFS(G, focus_index)
  bfs.run()

  utils.log("Collecting distances to identified circle")
  dists = collections.Counter()
  for node in circle:
    dists[int(bfs.distance(node))] += 1
  print("Distances: ", [dists[i] for i in range(max(dists.keys()) + 1)])

  utils.log("Analyzing distribution")
  size = sum(count for (dist, count) in dists.items())
  mean_dist = sum(dist * count for (dist, count) in dists.items()) / size
  mode_count, mode_dist = max((count, dist)
                              for (dist, count) in dists.items())
  print(f"Summary:  {size=:10_d}  /  {mode_dist=:3d}  {mode_count=:9_d}  /  {mean_dist=:5.1f}")

  utils.log("Finished")

main()
