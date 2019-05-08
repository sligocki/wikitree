import collections
import sys
import time

import community
import networkx as nx

filename = sys.argv[1]

print "Loading graph", time.clock()
g = nx.read_adjlist(filename)

print "Partitioning graph into communities", time.clock()
partition = community.best_partition(g)

print "Processing communities", time.clock()
print "Modularity", community.modularity(partition, g)
communities = collections.defaultdict(set)
for node in partition:
  comm = partition[node]
  communities[comm].add(node)

print "Num communities:", len(communities)
max_comm = max(len(communities[comm]) for comm in communities)
min_comm = min(len(communities[comm]) for comm in communities)
print "Community sizes:", min_comm, "to", max_comm
