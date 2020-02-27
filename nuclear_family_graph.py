# Produces graph where each node represents a "Nuclear family unit".
#
# In the traditional connection graph, there are many highly connected blocks.
# For example, given 2 parents with 4 children, all 6 will be directly connected
# to each other. But does this really represent 15 different connections?
#
# Instead, in this representation there is a node for every pair of people who
# either: (1) had children together or (2) were married. There are edges
# connecting that node to the node representing each of those people's parents
# and conversely to each child's partnership nodes.

import collections
import time

import networkx as nx

import csv_iterate
import graph_tools


def NodeName(parents):
  return "/".join(str(p) for p in sorted(parents))

print("Loading users", time.process_time())
# Map: person -> node in which they are a child
parent_node = {}
# Map: person -> nodes in which they are parents
spouse_nodes = collections.defaultdict(set)
for i, person_obj in enumerate(csv_iterate.iterate_users()):
  parents = [p for p in (person_obj.father_num(), person_obj.mother_num()) if p]
  person_num = person_obj.user_num()
  if parents:
    node = NodeName(parents)
    parent_node[person_num] = node
    # Note: Parents will be double added, but it's a set, so that's fine.
    for parent in parents:
      spouse_nodes[parent].add(node)
  if i % 1000000 == 0:
    print(f" ... {i:,}  {len(parent_node):,}  {len(spouse_nodes):,}", time.process_time())
print("Loading marriages", time.process_time())
# Connect any spouses. Note: This is redundant for couples with children.
for marriage in csv_iterate.iterate_marriages():
  couple = marriage.user_nums()
  node = NodeName(couple)
  for spouse in couple:
    spouse_nodes[spouse].add(node)
print(f"Finished loading {len(parent_node):,} {len(spouse_nodes):,}", time.process_time())

print("Building graph", time.process_time())
graph = nx.Graph()
for person in spouse_nodes:
  if person not in parent_node and len(spouse_nodes[person]) > 1:
    # We add a dummy parent node if this person was married multiple times
    # but has no parents listed. If we did not, their two families would
    # be unconnected.
    parent_node[person] = f"Parent/{person}"
  if person in parent_node:
    par_node = parent_node[person]
    for child_node in spouse_nodes[person]:
      graph.add_edge(child_node, par_node)
print(f"Total graph size: {len(graph.nodes):,} Nodes {len(graph.edges):,} Edges.")

print("Writing graph to file", time.process_time())
nx.write_adjlist(graph, "data/nuclear_family_graph.adj.nx")

print("Finding largest connected component", time.process_time())
main_component = graph_tools.LargestCombonent(graph)
print(f"Main component size: {len(main_component.nodes):,} Nodes {len(main_component.edges):,} Edges.")

print("Writing main component to file", time.process_time())
nx.write_adjlist(main_component, "data/nuclear_family_graph.main.adj.nx")
