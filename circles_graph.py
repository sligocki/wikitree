"""
Produce graph for circles around a focus person.
"""

import argparse
from pathlib import Path

import networkx as nx

import circles_tools
import data_reader
import graph_tools
import utils


def make_bipartite(db, people):
  # Like graph_make_bipartite ... but only for a subset of people.
  people_nodes = frozenset(people)
  union_nodes = set()
  edges = set()

  for person in people:
    # Add union node for parents if they are known.
    parents = db.parents_of(person)
    if parents:
      union = "Union/" + "/".join(str(p) for p in sorted(parents))
      union_nodes.add(union)
      edges.add((person, union))
      # Make sure parents are also connected to the union.
      for parent in parents:
        if parent in people_nodes:
          edges.add((parent, union))

    # Add union node for all "partners" (spouses / coparents).
    for partner in db.partners_of(person):
      if partner in people_nodes:
        union = "Union/" + "/".join(str(p) for p in sorted([person, partner]))
        union_nodes.add(union)
        edges.add((person, union))
        edges.add((partner, union))
        # Note: We don't explicitly connect all children here.
        # If they are in `people`, they will be connected above.

  return (sorted(people_nodes) + sorted(union_nodes),
          sorted(edges))


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("focus_id")
  parser.add_argument("--num-circles", "-n", type=int, default=7)
  parser.add_argument("--version", help="Data version (defaults to most recent).")
  args = parser.parse_args()

  utils.log("Starting")
  db = data_reader.Database(args.version)
  circles = circles_tools.load_circles(db, args.focus_id, args.num_circles)
  # Flat to set of people in all circles.
  people = frozenset(x for ring in circles for x in ring)
  utils.log(f"Loaded {args.num_circles} circles around {args.focus_id}: {len(people):_} people total")

  nodes, edges = make_bipartite(db, people)
  graph = graph_tools.make_graph(nodes, edges)
  utils.log(f"Created graph with {graph.number_of_nodes():_} nodes and {graph.number_of_edges():_} edges")

  graph_file = Path("results", "circles", "graph", f"{args.focus_id}.{args.num_circles}")
  graph_file.parent.mkdir(parents=True, exist_ok=True)
  filename = graph_tools.write_graph(graph, graph_file)
  utils.log(f"Wrote: {str(filename)}")

  # print("Cycles:")
  # for i, cycle in enumerate(nx.simple_cycles(graph)):
  #   print(f"Cycle {i:4d}  {len(cycle):4d}")
  #   for x in cycle:
  #     if isinstance(x, int):
  #       print(" *", db.num2id(x))

main()
