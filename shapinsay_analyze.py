"""
Produce and analyze a subgraph consisting of members of a Shapinsay category.
"""

import argparse
import datetime
from pathlib import Path

import networkx as nx

import category_tools
import data_reader
import graph_tools
import utils


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--version", help="Data version (defaults to most recent).")
  args = parser.parse_args()

  category_name = "Shapinsay_Parish,_Orkney"

  db = data_reader.Database(args.version)
  category_db = category_tools.CategoryDb(args.version)

  utils.log(f"Loading people in category {category_name}")
  cat_nums = category_db.list_people_in_category(category_name)
  utils.log(f"Loaded {len(cat_nums):_} people")

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

  subgraph = nx.Graph()
  num_stray_edges = 0
  for user_num in cat_nums:
    subgraph.add_node(db.num2id(user_num))
    for neigh_num in db.neighbors_of(user_num):
      if neigh_num in cat_nums:
        subgraph.add_edge(db.num2id(user_num), db.num2id(neigh_num))
      else:
        num_stray_edges += 1
  utils.log(f"Computed subgraph with {len(subgraph.nodes):_} nodes and "
            f"{len(subgraph.edges):_} edges "
            f"({num_stray_edges:_} edges had node outside graph)")

  main_component = graph_tools.LargestComponent(subgraph)
  utils.log(f"Main component: {len(main_component.nodes):_} nodes and "
            f"{len(main_component.edges):_} edges")

  utils.log("Finished")


main()
