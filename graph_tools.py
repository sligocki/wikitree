from pathlib import Path

import networkx as nx


def load_graph(filename):
  """Load a graph from various formats depending on the extensions."""
  filename = Path(filename)
  if ".adj" in filename.suffixes:
    return nx.read_adjlist(filename)

  elif ".edgelist" in filename.suffixes:
    return nx.read_weighted_edgelist(filename)

  else:
    raise Exception(f"Invalid graph filename: {filename}")

def LargestComponent(graph):
  max_size, main_component = max(
    ((len(comp), comp) for comp in nx.connected_components(graph)),
    key = lambda x: x[0])
  return graph.subgraph(main_component)
