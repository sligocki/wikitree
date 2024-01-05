"""
Produce and analyze a graph consisting of members of a Shapinsay category.
"""

import argparse
import datetime
import json
import math
from pathlib import Path

import networkx as nx

import category_tools
import data_reader
import graph_tools
import utils


def id_or_num(db, num):
  id = db.num2id(num)
  if id:
    return id
  else:
    # Fallback to num if we can't find ID (should be rare).
    return str(num)

def UnionNodeName(db, parent_nums):
  """Name for node which represents the union (marriage or co-parentage)."""
  parent_ids = []
  for num in parent_nums:
    parent_ids.append(id_or_num(db, num))

  return "Union/" + "/".join(str(p) for p in sorted(parent_ids))

class BipartiteBuilder:
  def __init__(self, db):
    self.db = db
    self.people_ids = set()
    self.union_ids = set()
    self.edge_ids = set()

  def compute_union_ids(self):
    return list(self.people_ids) + list(self.union_ids)

  def add_person(self, self_num):
    # Add person node for self.
    self_id = id_or_num(self.db, self_num)
    self.people_ids.add(self_id)

    # Add union node for parents and connect to it.
    parent_nums = self.db.parents_of(self_num)
    if parent_nums:
      union_id = UnionNodeName(self.db, parent_nums)
      self.union_ids.add(union_id)
      self.edge_ids.add((self_id, union_id))
      # Make sure parents are connected ... this will generally happen
      # automatically below with the partners iteration (unless one parent is unknown).
      for parent_num in parent_nums:
        parent_id = id_or_num(self.db, parent_num)
        self.people_ids.add(parent_id)
        self.edge_ids.add((parent_id, union_id))

    # Add partner node for each partner and connect to it.
    for partner_num in self.db.partners_of(self_num):
      union_id = UnionNodeName(self.db, [self_num, partner_num])
      self.union_ids.add(union_id)
      self.edge_ids.add((self_id, union_id))
      # Explicitly add partner as well ... this shouldn't be necessary, but
      # some private partners may not be in the DB.
      partner_id = id_or_num(self.db, partner_num)
      self.people_ids.add(partner_id)
      self.edge_ids.add((partner_id, union_id))

def log_incompleteness_stats(db, cat_nums):
  num_born = 0
  num_no_parents = 0
  recent_no_parents = set()
  for user_num in cat_nums:
    birth_loc = db.get(user_num, "birth_location")
    if birth_loc and "Shapinsay" in birth_loc:
      num_born += 1
      if not db.parents_of(user_num):
        num_no_parents += 1
        if db.birth_date_of(user_num) >= datetime.date(1830, 1, 1):
          recent_no_parents.add(user_num)
  utils.log(f"Num Born in Shapinsay: {num_born:_} ({num_born / len(cat_nums):.0%})")
  utils.log(f"  Num w/o parents: {num_no_parents:_} ({num_no_parents / num_born:.0%})")
  utils.log(f"    Num born > 1830: {len(recent_no_parents):_} "
            f"({len(recent_no_parents) / num_no_parents:.0%})")

  print()
  for user_num in sorted(recent_no_parents,
                         key=lambda user_num: db.birth_date_of(user_num)):
    print(f"{db.num2id(user_num):20s} : {db.name_of(user_num):20s} "
          f"({db.birth_date_of(user_num)} - {db.death_date_of(user_num)})")
  print()

def build_person_graph(user_nums, db):
  graph = nx.Graph()
  num_stray_edges = 0
  for user_num in user_nums:
    graph.add_node(db.num2id(user_num))
    for neigh_num in db.neighbors_of(user_num):
      if neigh_num in user_nums:
        graph.add_edge(db.num2id(user_num), db.num2id(neigh_num))
      else:
        num_stray_edges += 1
  return graph, num_stray_edges

def build_bipartite_graph(user_nums, db):
  graph_info = BipartiteBuilder(db)
  for user_num in user_nums:
    graph_info.add_person(user_num)

  graph = nx.Graph()
  for id in graph_info.compute_node_ids():
    graph.add_node(id)
  for (id1, id2) in graph_info.edge_ids:
    graph.add_edge(id1, id2)
  return graph

def enum_circles(graph, node):
  prev_cum_circles = set()
  this_cum_circles = set([node])
  while len(prev_cum_circles) < len(this_cum_circles):
    yield this_cum_circles - prev_cum_circles

    prev_cum_circles = frozenset(this_cum_circles)
    for node in prev_cum_circles:
      this_cum_circles |= set(graph.neighbors(node))


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--incompleteness-stats", action="store_true")
  parser.add_argument("--version", help="Data version (defaults to most recent).")
  args = parser.parse_args()

  category_name = "Shapinsay_Parish,_Orkney"

  db = data_reader.Database(args.version)
  category_db = category_tools.CategoryDb(args.version)

  utils.log(f"Loading people in category {category_name}")
  cat_nums = category_db.list_people_in_category(category_name)
  utils.log(f"Loaded {len(cat_nums):_} people")

  if args.incompleteness_stats:
    log_incompleteness_stats(db, cat_nums)

  graph = build_bipartite_graph(cat_nums, db)
  utils.log(f"Computed graph with {len(graph.nodes):_} nodes and "
            f"{len(graph.edges):_} edges")

  graph_tools.write_graph(graph, "results/shapinsay/full.graph.adj.nx")
  utils.log("Wrote graph to results/shapinsay/full.graph.adj.nx")

  components = sorted(nx.connected_components(graph), key = len, reverse=True)

  print()
  utils.log(f"Number of components: {len(components):_}")
  for i in range(10):
    comp = graph.subgraph(components[i])

    # Find a central person in component.
    node_centrality = nx.current_flow_closeness_centrality(comp)
    center_id = max(node_centrality.keys(), key = lambda id: node_centrality[id])
    if i == 0:
      # Save this so we don't need to recompute below.
      main_centrality = node_centrality

    utils.log(f" * Component {i}: {len(comp.nodes):_} nodes and "
              f"{len(comp.edges):_} edges ({center_id})")

  print()
  utils.log("Main component central nodes")
  most_central = sorted(main_centrality.keys(),
                        key = lambda id: main_centrality[id],
                        reverse = True)
  focus = most_central[0]
  focus_dists = nx.single_source_shortest_path_length(graph, focus)
  max_log_c = math.log(max(main_centrality.values()))
  min_log_c = math.log(min(main_centrality.values()))
  # Normalize to a value between 0.0 (min_centrality) and 1.0 (max_centrality)
  norm_centrality = {
    node : (math.log(c) - min_log_c) / (max_log_c - min_log_c)
    for node, c in main_centrality.items()}
  for i in list(range(10)) + list(range(len(most_central) - 5, len(most_central))):
    node = most_central[i]
    utils.log(f" * Center {i:4}: {node:40} / {focus_dists[node]:3d} / {norm_centrality[node]:.3f}")

  print()
  main = graph.subgraph(components[0])
  graph_tools.write_graph(main, "results/shapinsay/main.graph.adj.nx")
  utils.log("Wrote main component to results/shapinsay/main.graph.adj.nx")

  bicomps = sorted(nx.biconnected_components(main), key = len, reverse=True)

  print()
  utils.log(f"Number of bicomponents in main component: {len(bicomps):_}")
  for i in range(10):
    bicomp = graph.subgraph(bicomps[i])

    # Find a central person in bi-component.
    node_centrality = nx.current_flow_closeness_centrality(bicomp)
    center_id = max(node_centrality.keys(), key = lambda id: node_centrality[id])
    if i == 0:
      # Save this so we don't need to recompute below.
      main_bi_centrality = node_centrality

    utils.log(f" * Component {i}: {len(bicomp.nodes):_} nodes and "
              f"{len(bicomp.edges):_} edges ({center_id})")

  print()
  utils.log("Main bi-component central nodes")
  most_central = sorted(main_bi_centrality.keys(),
                        key = lambda id: main_bi_centrality[id],
                        reverse = True)
  focus = most_central[0]
  focus_dists = nx.single_source_shortest_path_length(graph, focus)
  max_log_c = math.log(max(main_bi_centrality.values()))
  min_log_c = math.log(min(main_bi_centrality.values()))
  # Normalize to a value between 0.0 (min_centrality) and 1.0 (max_centrality)
  norm_centrality = {
    node : (math.log(c) - min_log_c) / (max_log_c - min_log_c)
    for node, c in main_bi_centrality.items()}
  for i in list(range(10)) + list(range(len(most_central) - 5, len(most_central))):
    node = most_central[i]
    utils.log(f" * Center {i:4}: {node:40} / {focus_dists[node]:3d} / {norm_centrality[node]:.3f}")

  print()
  main_bi = graph.subgraph(bicomps[0])
  graph_tools.write_graph(main_bi, "results/shapinsay/main_bi.graph.adj.nx")
  utils.log("Wrote main bi-component to results/shapinsay/main_bi.graph.adj.nx")

  print()
  utils.log(f"Circle sizes around {most_central[0]}:")
  circles = list(enum_circles(main_bi, most_central[0]))
  circle_sizes = [len(circle) for circle in circles]
  cum_size = 0
  for circle_num, circle_size in enumerate(circle_sizes):
    cum_size += circle_size
    most_central_ring = max(circles[circle_num],
                            key = lambda id: main_bi_centrality[id])
    utils.log(f" * Circle {circle_num:3d}: {circle_size:7_d} {cum_size:7_d} ({cum_size / len(main_bi.nodes):6.1%})    {most_central_ring} {norm_centrality[most_central_ring]:.3f}")
  utils.log("   - Furthest nodes:", " ".join(sorted(circles[-1])))

  santized_name = most_central[0].replace("/", "-")
  circles_filename = f"results/shapinsay/circles_{santized_name}.json"
  with open(circles_filename, "w") as f:
    json.dump({ most_central[0] : circle_sizes}, f)
  utils.log("Write circles to", circles_filename)


main()
