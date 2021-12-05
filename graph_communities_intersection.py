import argparse
import math
import re

import networkit as nk
from unidecode import unidecode

import category_tools
import collections
import data_reader
import graph_tools
import utils


parser = argparse.ArgumentParser()
parser.add_argument("graph")
parser.add_argument("num_partitions", type=int)
parser.add_argument("--version", help="Data version (defaults to most recent).")
args = parser.parse_args()

db = data_reader.Database(args.version)
category_db = category_tools.CategoryDb(args.version)

utils.log("Reading graph")
G, names_db = graph_tools.load_graph_nk(args.graph)
utils.log(f"Loaded graph with {G.numberOfNodes():_} nodes / {G.numberOfEdges():_} edges")

utils.log(f"Calculating {args.num_partitions} partitions")
partitions = [nk.community.detectCommunities(G) for _ in range(args.num_partitions)]

utils.log("Calculating the intersection of all partitions")
intersect_partition = collections.defaultdict(list)
for node in G.iterNodes():
  all_comms = [partition[node] for partition in partitions]
  intersect_name = ",".join(str(comm) for comm in all_comms)
  intersect_partition[intersect_name].append(node)
utils.log(f"Found {len(intersect_partition)} partition intersections")

utils.log("Finding the largest intersections")
size_part = [(len(nodes), name) for (name, nodes) in intersect_partition.items()]
size_part.sort(reverse=True)

large_sizes = [size for (size, _) in size_part[:20]]
print("Largest Community sizes:", large_sizes)
total_nodes = G.numberOfNodes()
percent_sizes = [size / total_nodes for size in large_sizes]
print("Largest Community sizes (percent of network):", percent_sizes)

print("Count of communities by magnitude:")
com_size_hist_mag = collections.Counter()
com_size_mag_cum = collections.defaultdict(int)
for (size, _) in size_part:
  magnitude = math.floor(math.log10(size))
  com_size_hist_mag[magnitude] += 1
  com_size_mag_cum[magnitude] += size
for k in range(max(com_size_hist_mag.keys()) + 1):
  print(f" - {10**k:9_d} - {10**(k+1) - 1:9_d} : {com_size_hist_mag[k]:7_d} {com_size_mag_cum[k]:11_d}")


def name2users(node_name):
  if node_name.startswith("Union/") or node_name.startswith("Parents/"):
    # For Union, return all parents.
    names = node_name.split("/")[1:]
  else:
    # For person node, just return that person.
    names = [node_name]
  
  return [db.get_person_num(id_or_num) for id_or_num in names]

def get_locations(user_num):
  """Return set of locations referenced by user's birth and death fields."""
  locs = set()
  for attribute in ["birth_location", "death_location"]:
    loc = db.get(user_num, attribute)
    # Note: occationally loc is an int ... skip
    if loc and isinstance(loc, str):
      # Break loc up into sections so that we can count country, state, county, etc.
      # , is most common separtor, but I've see () and [] as well
      # (for Mexico sepcifically).
      for section in re.split(r"[,()\[\]]", loc):
        # Replace all accented chars with ASCII to standardize
        # Otherwise we end up with Mexico and México as sep locs.
        section = unidecode(section.strip())
        if section:
          locs.add(section)
  return locs

def summarize_community(subset):
  # TODO: Ignoring Union nodes for Bijective graph.
  size = len(subset)
  utils.log(f"Collecting metadata for community of size {size:_}")
  # Note: Count is per-person, not per-node.
  counts = {
    "category": collections.Counter(),
    "location": collections.Counter(),
    "manager": collections.Counter(),
  }
  birth_years = []
  for node_index in subset:
    node_name = names_db.index2name(node_index)
    for user_num in name2users(node_name):
      counts["category"].update(category_db.list_categories_for_preson(user_num))
      counts["location"].update(get_locations(user_num))
      counts["manager"][db.get(user_num, "manager_num")] += 1
      birth_date = db.birth_date_of(user_num)
      if birth_date:
        birth_years.append(birth_date.year)

  for type in counts.keys():
    utils.log(f"Most common {type}:")
    for (thing, count) in counts[type].most_common(10):
      # Since count is per-person, not per-node, we can end up with up to 200%
      # for family graphs (2 people / node).
      print(f" - {count / size:6.2%}  {thing}")
  birth_years.sort()
  utils.log("Birth Year Stats:")
  for i in range(5):
    percentile = i / 4.0
    by_index = round(percentile * (len(birth_years) - 1))
    print(f" - {percentile:4.0%}-ile:  {birth_years[by_index]}")
  
  utils.log("Central nodes:")
  subG = nk.graphtools.subgraphFromNodes(G, subset)
  if size <= 50_000:
    closeness = nk.centrality.Closeness(subG, False, nk.centrality.ClosenessVariant.Generalized)
  else:
    # If we have too many nodes, excact closeness is too slow.
    closeness = nk.centrality.ApproxCloseness(subG, 100)
  closeness.run()
  for node_index, score in closeness.ranking()[:10]:
    node_name = names_db.index2name(node_index)
    user_nums = name2users(node_name)
    id_str = "/".join(db.num2id(user_num) for user_num in user_nums)
    print(f" - {1/score:6.2f}  {id_str}")
  

print()
utils.log("Examine Large Communities")
print()
for order, (_, part_name) in enumerate(size_part[:20]):
  print("Community", order)
  summarize_community(intersect_partition[part_name])
  print()

# utils.log("Examine Particular Communities")
# for node_name in [
#     "Ligocki-7",
#     "Gardahaut-1",
#     "Vatant-5",
#     "Andersson-5056",
#     # "Mars-121",
#     # "Lothrop-29",
#     # "Windsor-1",
#   ]:
#   node_index = names_db.name2index(node_name)
#   community_index = communities[node_index]
#   summarize_community(community_index)
#   print()


utils.log("Finished")
