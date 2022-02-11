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

# Deprecated: Switch to NetoworKit!
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

def LargestComponent(graph):
  max_size, main_component = max(
    ((len(comp), comp) for comp in nx.connected_components(graph)),
    key = lambda x: x[0])
  return graph.subgraph(main_component)

def largest_component_nk(graph):
  assert isinstance(graph, nk.Graph), graph
  cc = nk.components.ConnectedComponents(graph)
  return cc.extractLargestConnectedComponent(graph)
