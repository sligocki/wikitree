import os
from pathlib import Path
import sqlite3

import networkit as nk
import networkx as nx


class NamesDb:
  def __init__(self, db_filename):
    try:
      self.conn = sqlite3.connect(db_filename)
    except sqlite3.OperationalError:
      raise sqlite3.OperationalError(f"Unable to open DB file {db_filename}")
    self.conn.row_factory = sqlite3.Row

  def create_table(self):
    cursor = self.conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS nodes")
    cursor.execute("""CREATE TABLE nodes (
      graph_index INT,
      node_name STRING,
      PRIMARY KEY (graph_index))""")

  def insert(self, graph_index, node_name):
    cursor = self.conn.cursor()
    cursor.execute("INSERT INTO nodes VALUES (?,?)", (graph_index, node_name))

  def commit(self):
    self.conn.commit()

  def index2name(self, graph_index):
    cursor = self.conn.cursor()
    cursor.execute("SELECT node_name FROM nodes WHERE graph_index=?",
                   (graph_index,))
    rows = cursor.fetchall()
    assert len(rows) == 1, (graph_index, rows)
    return rows[0]["node_name"]

  def name2index(self, node_name):
    cursor = self.conn.cursor()
    cursor.execute("SELECT graph_index FROM nodes WHERE node_name=?",
                   (node_name,))
    rows = cursor.fetchall()
    assert len(rows) == 1, (node_name, rows)
    return rows[0]["graph_index"]

  def all_index2names(self):
    cursor = self.conn.cursor()
    cursor.execute("SELECT graph_index, node_name FROM nodes")
    rows = cursor.fetchall()
    return {row["graph_index"]: row["node_name"] for row in rows}


def load_graph_nk(filename):
  """Returns pair (G, names_db) of graph and the tool for converting
  node indexes to names."""
  filename = Path(filename)
  if ".graph" in filename.suffixes:
    # TODO: Submit bug to nk team about accepting Path as arg.
    return (nk.graphio.readGraph(str(filename), nk.Format.METIS),
            NamesDb(f"{filename}.names.db"))

  else:
    raise Exception(f"Invalid graph filename: {filename}")

def load_graph(filename : Path) -> nx.Graph:
  """Load a graph from various formats depending on the extensions."""
  filename = Path(filename)

  g_type : type
  if ".multi" in filename.suffixes:
    if ".di" in filename.suffixes:
      g_type = nx.MultiDiGraph
    else:
      g_type = nx.MultiGraph
  else:
    if ".di" in filename.suffixes:
      g_type = nx.DiGraph
    else:
      g_type = nx.Graph

  if ".adj" in filename.suffixes:
    return nx.read_adjlist(filename, create_using=g_type)

  elif ".edges" in filename.suffixes:
    return nx.read_weighted_edgelist(filename, create_using=g_type)

  else:
    raise Exception(f"Invalid graph filename: {filename}")

def write_graph(graph : nx.Graph, basename_path : Path) -> Path:
  """Write a graph into various formats depending on Type."""
  basename = str(basename_path)

  if graph.is_directed():
    basename += ".di"

  if graph.is_multigraph():
    basename += ".multi"

  if is_weighted(graph):
    filename = Path(basename + ".weight.edges.nx")
    nx.write_weighted_edgelist(graph, filename)

  else:  # Non-weighted
    filename = Path(basename + ".adj.nx")
    nx.write_adjlist(graph, filename)

  return filename

def write_graph_nk(graph, names, filename):
  filename = Path(filename)
  if ".graph" in filename.suffixes:
    # TODO: Submit bug to nk team about accepting Path as arg.
    nk.graphio.writeGraph(graph, str(filename), nk.Format.METIS)
    # Write names into sibling db file.
    names_db = NamesDb(f"{filename}.names.db")
    names_db.create_table()
    for index, node_name in enumerate(names):
      names_db.insert(index, node_name)
    names_db.commit()

  else:
    raise Exception(f"Invalid graph filename: {filename}")

def make_graph(nodes, edges):
  graph = nx.Graph()
  for node in nodes:
    graph.add_node(node)
  for (a, b) in edges:
    graph.add_edge(a, b)
  return graph

def make_graph_nk(node_ids, edges):
  id2index = {}
  for node_index, wikitree_id in enumerate(node_ids):
    id2index[wikitree_id] = node_index

  graph = nk.Graph(len(node_ids))
  for (id1, id2) in graph_info.edge_ids:
    try:
      graph.addEdge(id2index[id1], id2index[id2])
    except KeyError:
      print("Unexpected ID among:", id1, id2)
      raise
  return graph

def is_weighted(graph):
  """If any edge is weighted, the entire graph is considered weighted.
  NOTE: This is different than nx.is_weighted() which requires all edges to be weighted ...
  but for some reason none of my dist 1 edges end up weighted, sigh.
  """
  return any("weight" in data for u, v, data in graph.edges(data=True))


def largest_component(graph):
  main_comp = max(nx.connected_components(graph), key = len)
  return graph.subgraph(main_comp)

def largest_bicomponent(graph):
  main_comp = max(nx.biconnected_components(graph), key = len)
  return graph.subgraph(main_comp)


def largest_component_nk(graph):
  assert isinstance(graph, nk.Graph), graph
  cc = nk.components.ConnectedComponents(graph)
  return cc.extractLargestConnectedComponent(graph)
