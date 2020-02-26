# Produces graph where each node represents a "Nuclear family unit".
#
# In the traditional connection graph, there are many highly connected blocks.
# For example, given 2 parents with 4 children, all 6 will be directly connected
# to each other. But does this really represent 15 different connections?
#
# Instead, in this representation there is a node for every pair of people who
# either: (1) had children together or (2) were married. The "members" of that
# node are the 2 parents and all their children together. Two nodes are
# connected by an edge if they share "members". In other words, the node
# representing me and my spouse would be connected to: (1) my parents' node,
# (2) my spouse's parents' node, (3) each of our children's nuclear nodes and
# (4) any previous spouse/partnership nodes of either me or my spouse.

import collections
import time

import networkx as nx

import csv_iterate
import graph_tools


def NodeName(parents):
  return "/".join(str(p) for p in sorted(parents))

print("Loading users", time.process_time())
# Map people -> nodes they are members of
nodes_of = collections.defaultdict(set)
for i, person in enumerate(csv_iterate.iterate_users()):
  parents = [p for p in (person.father_num(), person.mother_num()) if p]
  if parents:
    node = NodeName(parents)
    # Connect child and parents to this node.
    # Note: Parents will be double added, but it's a set, so that's fine.
    for member in parents + [person.user_num()]:
      nodes_of[member].add(node)
  if i % 1000000 == 0:
    print(f" ... {i:,}", time.process_time())
print("Loading marriages", time.process_time())
# Connect any spouses. Note: This is redundant for couples with children.
for marriage in csv_iterate.iterate_marriages():
  couple = marriage.user_nums()
  node = NodeName(couple)
  for member in couple:
    nodes_of[member].add(node)

print("Building graph", time.process_time())
graph = nx.Graph()
for member in nodes_of:
  for node_a in nodes_of[member]:
    for node_b in nodes_of[member]:
      # Don't double-add edges
      if node_a < node_b:
        graph.add_edge(node_a, node_b)
print(f"Total graph size: {len(graph.nodes):,} Nodes {len(graph.edges):,} Edges.")

print("Writing graph to file", time.process_time())
nx.write_adjlist(graph, "data/nuclear_family_graph.adj.nx")

print("Finding largest connected component", time.process_time())
main_component = graph_tools.LargestCombonent(graph)
print(f"Main component size: {len(main_component.nodes):,} Nodes {len(main_component.edges):,} Edges.")

print("Writing main component to file", time.process_time())
nx.write_adjlist(main_component, "data/nuclear_family_graph.main.adj.nx")
