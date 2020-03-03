# Produces a graph representing "Nuclear family units".
#
# Represented as a bipartite graph where each node is either:
#  * a person or
#  * a family unit (representing 2 parents and all their children
#                   or a married couple with no children)
# Every person is connected to every family unit they are a member of.
#
# In the traditional connection graph, there are many highly connected blocks.
# For example, given 2 parents with 4 children, all 6 will be directly connected
# to each other. But does this really represent 15 different connections?
#
# Instead, in this representation it would be represented as a star of 6 person
# nodes attached to a central family node.
#
# The resulting graph will have drastically fewer cliques and running through
# graph_core.py will be much more effective.

import collections
import time

import networkx as nx

import csv_iterate
import graph_tools


def UnionNodeName(parents):
  """Name for node which represents the union (marriage or co-parentage)."""
  return "Union/" + "/".join(str(p) for p in sorted(parents))


graph = nx.Graph()
print("Loading users", time.process_time())
for i, person_obj in enumerate(csv_iterate.iterate_users()):
  parents = [p for p in (person_obj.father_num(), person_obj.mother_num()) if p]
  person_num = person_obj.user_num()
  if parents:
    union_node = UnionNodeName(parents)
    graph.add_edge(person_num, union_node)
    # Note: Parents will be double added, Graph ignores redundant edges.
    for parent in parents:
      graph.add_edge(parent, union_node)
  if i % 1000000 == 0:
    print(f" ... {i:,}  {len(graph.nodes):,}  {len(graph.edges):,}", time.process_time())

print("Loading marriages", time.process_time())
# Connect any spouses. Note: This is redundant for couples with children.
for marriage in csv_iterate.iterate_marriages():
  couple = marriage.user_nums()
  union_node = UnionNodeName(couple)
  for spouse in couple:
    graph.add_edge(spouse, union_node)

print(f"Total graph size: {len(graph.nodes):,} Nodes {len(graph.edges):,} Edges.")

print("Writing graph to file", time.process_time())
nx.write_adjlist(graph, "data/nuclear.all.adj.nx")

print("Finding largest connected component", time.process_time())
main_component = graph_tools.LargestCombonent(graph)
print(f"Main component size: {len(main_component.nodes):,} Nodes {len(main_component.edges):,} Edges.")

print("Writing main component to file", time.process_time())
nx.write_adjlist(main_component, "data/nuclear.main.adj.nx")
