import sys

import community
import networkx as nx
import matplotlib.pyplot as plt

filename = sys.argv[1]

g = nx.read_adjlist(filename)

partition = community.best_partition(g)

# Plot it
size = float(len(set(partition.values())))
pos = nx.spring_layout(g)
count = 0.
for com in set(partition.values()) :
  count += 1
  list_nodes = [nodes for nodes in partition if partition[nodes] == com]
  nx.draw_networkx_nodes(g, pos, list_nodes, node_size = 20,
                         node_color = str(count / size))


nx.draw_networkx_edges(g, pos, alpha=0.5)
plt.show()
