import networkx as nx

def LargestCombonent(graph):
  max_size, main_component = max(
    ((len(comp), comp) for comp in nx.connected_components(graph)),
    key = lambda x: x[0])
  main_subgraph = graph.subgraph(main_component)
