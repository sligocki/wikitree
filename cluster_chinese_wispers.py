"""
Cluster WikiTree graph using the "Chinese Whispers" algorithm.

https://en.wikipedia.org/wiki/Chinese_Whispers_(clustering_method)
"""

import argparse
import time

import networkx as nx
import chinese_whispers as cw


parser = argparse.ArgumentParser()
parser.add_argument("--graph", default="data/connection_graph.adj.nx")
# Parameters from python package.
parser.add_argument("--iterations", type=int, default=20)
args = parser.parse_args()

print(" ... Loading graph", time.process_time())
g = nx.read_adjlist(args.graph)

print(" ... Clustering graph", time.process_time())
cw.chinese_whispers(g, iterations=args.iterations)

print(" ... Describing clusters", time.process_time())
clusters = cw.aggregate_clusters(g)
print("Number of clusters:", len(clusters))
cluster_sizes = sorted([len(clusters[name]) for name in clusters])
print("Community sizes:", cluster_sizes[0], "to", cluster_sizes[-1])
print("Median cluster size:", cluster_sizes[len(clusters) // 2])

print(" ... Done", time.process_time())
