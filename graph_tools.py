from pathlib import Path

import networkx as nx


def load_graph(filename):
  """Load a graph from various formats depending on the extensions."""
  filename = Path(filename)
  if ".adj" in filename.suffixes:
    return nx.read_adjlist(filename)

  elif ".edgelist" in filename.suffixes:
    return nx.read_weighted_edgelist(filename)

  elif ".gml" in filename.suffixes:
    return nx.read_gml(filename)

  else:
    raise Exception(f"Invalid graph filename: {filename}")

def write_graph(graph, filename):
  """Write a graph into various formats depending on the extension."""
  filename = Path(filename)
  if ".adj" in filename.suffixes:
    nx.write_adjlist(graph, filename)

  elif ".edgelist" in filename.suffixes:
    nx.write_weighted_edgelist(graph, filename)

  elif ".gml" in filename.suffixes:
    nx.write_gml(graph, filename)

  else:
    raise Exception(f"Invalid graph filename: {filename}")

def LargestComponent(graph):
  max_size, main_component = max(
    ((len(comp), comp) for comp in nx.connected_components(graph)),
    key = lambda x: x[0])
  return graph.subgraph(main_component)
