import argparse
import time

import networkx as nx

import connection
import data_reader


parser = argparse.ArgumentParser()
parser.add_argument("wikitree_id")
parser.add_argument("--version", help="Data version (defaults to most recent).")
parser.add_argument("--graph", default="data/version/default/nuclear.core.adj.nx")
parser.add_argument("--plot", action="store_true",
                    help="Produce a DOT plot of connections.")
parser.add_argument("--distance-only", action="store_true",
                    help="Only print the distance (not connection sequence).")
args = parser.parse_args()

print("Loading graph", time.process_time())
graph = nx.read_adjlist(args.graph)
print(f"Initial graph:  # Nodes: {len(graph.nodes):,}  # Edges: {len(graph.edges):,}", time.process_time())

print("Extracting core people", time.process_time())
core_people = set()
for node in graph.nodes:
  for person in node.split("/"):
    try:
      core_people.add(int(person))
    except ValueError:
      # Ignore non integer "person" values. Ex: "Parent"
      pass

db = data_reader.Database(args.version)
print(f"Connections from {args.wikitree_id} to core (size {len(core_people):,})", time.process_time())
connections = connection.find_connections_group(
  db=db, start=db.id2num(args.wikitree_id), group=core_people)
connection.print_connections(args, db, connections)

print("Done", time.process_time())
