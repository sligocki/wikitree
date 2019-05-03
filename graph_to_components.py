import math

import networkx as nx

class TopN:
  """Data structure which only keeps top N items."""
  def __init__(self, size):
    self.size = size
    self.items = []

  def add(self, measure, item):
    if len(self.items) < self.size or measure > self.items[-1][0]:
      self.items.append((measure, item))
      self.items.sort(key=lambda x: x[0], reverse=True)
      if len(self.items) > self.size:
        del self.items[-1]


g = nx.read_adjlist("graph.adj.nx")

# Get list of 5 biggest components and one component for each order of magnitude.
top_n = TopN(5)
comps_by_size = {}
num_comps_by_size = {}
for comp in nx.connected_components(g):
  sg = g.subgraph(comp)
  top_n.add(len(comp), sg)
  oom = int(math.log(len(comp), 10))
  if oom not in comps_by_size:
    comps_by_size[oom] = (len(comp), sg)
    num_comps_by_size[oom] = 0
  num_comps_by_size[oom] += 1


print "Top components"
for num_nodes, sg in top_n.items:
  print num_nodes
  filename = "comp-%d.adj.nx" % num_nodes
  nx.write_adjlist(sg, filename)
sizes_written = {num_nodes for num_nodes, _ in top_n.items}

print "Num of components by size"
for oom in sorted(num_comps_by_size.keys()):
  print "10^%d %d (ex: %d)" % (oom, num_comps_by_size[oom], comps_by_size[oom][0])
  num_nodes, sg = comps_by_size[oom]
  if num_nodes not in sizes_written:
    filename = "comp-%d.adj.nx" % num_nodes
    nx.write_adjlist(sg, filename)
