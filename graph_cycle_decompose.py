# Decompose a non-geodesic cycle into geodesic cycles.

import argparse
from collection.abc import Sequence
import itertools
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

import graph_tools
import utils


Node = str

def min_shortcut(graph : nx.Graph, cycle : Sequence[Node]) -> Sequence[Node] | None:
  """Find the shortest shortcut path between antipodes of the cycle.
  If cycle is geodesic (all antipodes are distance n//2) then returns None."""
  # Check antipodal distances
  # For even, there are n/2, for odd all n.
  n = len(cycle)
  k, r = divmod(n, 2)
  if r == 0:
    antipodes = [(i, i+k) for i in range(k)]
  else:
    antipodes = [(i, (i+k) % n) for i in range(n)]

  min_dist = k
  shortcut = None
  for a, b in antipodes:
    path = nx.shortest_path(graph, cycle[a], cycle[b])
    dist = len(path) - 1
    if dist < min_dist:
      min_dist = dist
      shortcut = path
  return shortcut

def simple_cut(graph : nx.Graph, cycle : Sequence[Node], path : Sequence[Node]
               ) -> Sequence[Node] | None:
  """Return a subpath of path such that only the first and last node are on
  cycle. We call this a cut of the cycle. If length one it is a chord."""
  cycle_nodes = frozenset(cycle)
  assert path[0] in cycle_nodes and path[-1] in cycle_nodes, (cycle, path)
  # Find first branch/cut along path.
  i = 1
  while i < len(path) and path[i] in cycle_nodes:
    i += 1
  if i >= len(path):
    return None
  # i just departed the cycle, so cut starts one node earlier
  start = i - 1
  while path[i] not in cycle_nodes:
    i += 1
  # i just returned to the cycle, so cut ends here
  end = i
  cut = path[start : end + 1]
  assert cut[0] in cycle_nodes and cut[-1] in cycle_nodes, (cycle, path, cut)
  assert all(n not in cycle_nodes for n in cut[1:-1]), (cycle, cut)
  return cut

def is_cycle(graph : nx.Graph, cycle : Sequence[Node]) -> bool:
  return nx.is_path(graph, cycle + [cycle[0]])

def split(graph : nx.Graph, cycle : Sequence[Node], cut : Sequence[Node]
          ) -> tuple[Sequence[Node], Sequence[Node]]:
  """Split a cycle into two using a cut path."""
  # Nodes on cycle where the cut branches off.
  a, b = cycle.index(cut[0]), cycle.index(cut[-1])
  # Nodes on cut that are not in cycle.
  branch = cut[1:-1]
  assert not (set(branch) & set(cycle)), (cycle, cut)
  # Canonical ordering
  if a > b:
    a, b = b, a
    branch = list(reversed(branch))
  assert a < b, (a, b)

  # Split cycle into two subcycles
  outside = cycle[:a+1] + branch + cycle[b:]
  inside = cycle[a:b+1] + list(reversed(branch))
  assert is_cycle(graph, outside), (cycle, cut, outside)
  assert is_cycle(graph, inside), (cycle, cut, inside)
  return outside, inside

def geodesic_decompose(graph : nx.Graph, cycle : Sequence[Node]
                       ) -> tuple[Sequence[Sequence[Node]], Sequence[Sequence[Node]]]:
  """Decompose cycle into geodesic cycles (which "add" up to the original cycle)."""
  todo = [cycle]
  done = []
  cuts = []
  while todo:
    new_todo : list[Sequence[Node]] = []
    for cycle in todo:
      shortcut = min_shortcut(graph, cycle)
      if not shortcut:
        # This cycle is already geodesic.
        done.append(cycle)
      else:
        cut = simple_cut(graph, cycle, shortcut)
        new_todo += split(graph, cycle, cut)
        cuts.append(cut)
    todo = new_todo
  return done, cuts

def cycle_from_nodes(graph : nx.Graph, nodes : Sequence[Node]) -> Sequence[Node]:
  cycle = []
  for i, a in enumerate(nodes):
    b = nodes[(i+1) % len(nodes)]
    path = nx.shortest_path(graph, a, b)
    cycle += path[:-1]
    # Remove nodes from interior of path (using subgraph mechanism so it does
    # not modify the original graph).
    graph = graph.subgraph(set(graph.nodes) - set(path[1:-1]))
  assert len(cycle) == len(set(cycle)), cycle
  return cycle

Edge = tuple[Node, Node]
def edge(e : Edge) -> Edge:
  return tuple(sorted(e))  # type: ignore[return-value]

def cycle_to_edges(graph : nx.Graph, cycle : Sequence[Node]) -> Sequence[Edge]:
  edges = []
  for a, b in zip(cycle, cycle[1:] + [cycle[0]]):
    edges.append(edge((a, b)))
  return edges

def draw(graph : nx.Graph, pos, filename : Path) -> None:
  fig, ax = plt.subplots()
  nx.draw(graph.subgraph(pos.keys()), pos, ax=ax, node_size=10)
  fig.set_size_inches(4, 4)
  fig.savefig(filename)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("graph", type=Path)
  parser.add_argument("nodes", nargs="+")
  parser.add_argument("--graph-out", type=Path, default="cycle_decomp")
  parser.add_argument("--version", help="Data version (defaults to most recent).")
  args = parser.parse_args()

  utils.log("Loading graph")
  graph = graph_tools.load_graph(args.graph)
  utils.log(f"Loaded graph:  # Nodes: {graph.number_of_nodes():_}  # Edges: {graph.number_of_edges():_}")

  start_cycle = cycle_from_nodes(graph, args.nodes)
  utils.log(f"Loaded cycle of length {len(start_cycle):_}")

  subcycles, cuts = geodesic_decompose(graph, start_cycle)
  utils.log(f"Decomposed cycle into {len(subcycles):_} geodesic subcycles")

  # Find all edges in all subcycles.
  # We do this instead of an induced subgraph on nodes b/c we don't want to
  # include incidental edges between nodes that were not part of the subcycles.
  sub_edges = set()
  for cycle in subcycles:
    sub_edges.update(cycle_to_edges(graph, cycle))
  lace = graph.edge_subgraph(sub_edges)
  utils.log(f"Subset to Lace:  # Nodes: {lace.number_of_nodes():_}  # Edges: {lace.number_of_edges():_}")

  filename = graph_tools.write_graph(lace, args.graph_out)
  utils.log(f"Wrote Lace to {filename}")

  # Layout and draw network in a custom way:
  #   1) Layout original cycle as a circle.
  theta = np.linspace(0, 1, len(start_cycle) + 1)[:-1] * 2 * np.pi
  theta = theta.astype(np.float32)
  locs = np.column_stack([np.cos(theta), np.sin(theta)])
  pos = dict(zip(start_cycle, locs))
  draw(lace, pos, Path("steps/base.png"))

  #   2) For each cut, draw it linearly between existing nodes.
  for i, cut in enumerate(cuts):
    # Existing locations of endpoints of cut.
    a, b = pos[cut[0]], pos[cut[-1]]
    locs = np.linspace(a, b, len(cut))
    pos.update(dict(zip(cut, locs)))
    draw(lace, pos, Path(f"steps/cut_{i}.png"))

  # node_colors = ["red" if n in args.nodes else "#1f78b4"
  #                for n in lace.nodes]
  # nx.draw_networkx_nodes(lace, pos, node_size=100, node_color=node_colors)
  # # nx.draw_networkx_labels(lace, pos)
  # edge_colors = ["red" if edge(e) in frozenset(cycle_to_edges(graph, start_cycle)) else "black"
  #                for e in lace.edges]
  # nx.draw_networkx_edges(lace, pos, edge_color=edge_colors)
  # plt.show()

if __name__ == "__main__":
  main()
