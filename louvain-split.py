# Louvain method for splitting network into communities.

import collections
import copy
import random

def calc_Q(graph, community_of):
  k = dict()
  for node in graph:
    k[node] = sum(graph[node].values())
  m = sum(k.values())

  Q = 0.
  for i in graph:
    for j, A_ij in graph[i].items():
      if (community_of[i] == community_of[j]):
        Q += (A_ij - k[i] * k[j] / (2. * m))
  Q /= (2. * m)
  return Q

def calc_dQ(graph, community_of, node, new_comm):
  Q0 = calc_Q(graph, community_of)
  new_comm_of = copy.copy(community_of)
  new_comm_of[node] = new_comm
  Q1 = calc_Q(graph, new_comm_of)
  return Q1 - Q0

def louvain_split(graph, level=0):
  print "Level", level, len(graph)
  for node in graph:
    for neighbor, weight in graph[node].items():
      assert neighbor in graph, (node, neighbor, graph[node], graph)

  # Initialize everyone to their own community of 1.
  # Maps node -> community
  community_of = {node : node for node in graph}

  # Greedily try to consolidate communities.
  # Repeatedly iterate over all nodes until no progress is made.
  progress = True
  while progress:
    progress = False

    nodes = graph.keys()
    #random.shuffle(nodes)
    for node in nodes:
      # For each node, see which comminity gives it the max modularity.
      best_dQ = 0
      best_comm = community_of[node]
      for neighbor in graph[node]:
        #print community_of, neighbor
        dQ = calc_dQ(graph, community_of, node, community_of[neighbor])
        if dQ > best_dQ:
          best_dQ = dQ
          best_comm = community_of[neighbor]
      if best_dQ > 0:
        progress = True
        # Move node to the best community.
        community_of[node] = best_comm

  print "Q =", calc_Q(graph, community_of)

  communities = collections.defaultdict(list)
  for node in community_of:
    communities[community_of[node]].append(node)

  # If there was no change in communities, then we're done.
  if len(communities) == len(graph):
    return graph, {node : [node] for node in graph}

  # Meta step: Build a new graph where each community becomes a node.
  meta_graph = dict()
  for comm in communities:
    meta_graph[comm] = collections.defaultdict(int)
    for node in communities[comm]:
      for neighbor, weight in graph[node].items():
        meta_graph[comm][community_of[neighbor]] += weight

  top_graph, mapping = louvain_split(meta_graph, level + 1)
  return top_graph, {node : (mapping[community_of[node]] + [community_of[node]])
                     for node in graph}


def load_graph(filename):
  graph = dict()
  with file(filename, "rb") as f:
    for line in f:
      parts = line.strip().split()
      # Every edge has an initial weight of 1.
      graph[parts[0]] = {neighbor : 1 for neighbor in parts[1:]}
  return graph

def load_tsv(filename):
  graph = collections.defaultdict(dict)
  with file(filename, "rb") as f:
    for line in f:
      if line[0] == "%":
        continue
      a, b = line.strip().split()
      # Every edge has an initial weight of 1.
      graph[a][b] = 1
      graph[b][a] = 1
  return graph


if __name__ == "__main__":
  import pprint
  import sys

  #graph = load_graph(sys.argv[1])
  graph = load_tsv(sys.argv[1])
  top_graph, partition = louvain_split(graph)

  pprint.pprint(top_graph)
  pprint.pprint(partition)
  print "Q =", calc_Q(graph, {node: comm[0] for node, comm in partition.items()})
