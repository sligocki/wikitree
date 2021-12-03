import argparse

import networkit as nk

import collections
import data_reader
import graph_tools
import utils


parser = argparse.ArgumentParser()
parser.add_argument("graph")
parser.add_argument("--version", help="Data version (defaults to most recent).")
args = parser.parse_args()

db = data_reader.Database(args.version)

utils.log("Reading graph")
G, names_db = graph_tools.load_graph_nk(args.graph)
utils.log(f"Loaded graph with {G.numberOfNodes():_} nodes / {G.numberOfEdges():_} edges")

utils.log("Calculating communities")
communities = nk.community.detectCommunities(G)

utils.log("Community info")
community_size_index = [(size, index)
                        for (index, size) in enumerate(communities.subsetSizes())]
community_size_index.sort(reverse=True)
large_sizes = [size for (size, _) in community_size_index[:20]]
print("Largest Community sizes:", large_sizes)
total_nodes = G.numberOfNodes()
percent_sizes = [size / total_nodes for size in large_sizes]
print("Largest Community sizes (percent of network):", percent_sizes)

utils.log("Writing Communities to file")
nk.community.writeCommunities(communities, f"{args.graph}.communities")


def get_locations(node_name):
  """Return set of locations referenced by """
  if node_name.startswith("Union/"):
    user_nums = node_name.split("/")[1:]
  else:
    user_nums = [node_name]
  
  locs = set()
  for user_num in user_nums:
    for attribute in ["birth_location", "death_location"]:
      loc = db.get(user_num, attribute)
      # Note: occationally loc is an int ... skip
      if loc and isinstance(loc, str):
        locs.update(section.strip() for section in loc.split(","))
  return locs

print()
for order, (size, index) in enumerate(community_size_index[0:100]):
  utils.log("Collecting locations community", order, size)
  subset = communities.getMembers(index)
  loc_counts = collections.Counter()
  for node_index in subset:
    node_name = names_db.index2name(node_index)
    loc_counts.update(get_locations(node_name))
  utils.log("Most common locations")
  for (loc, count) in loc_counts.most_common(10):
    print(f" - {count / size:.2%} {loc}")
  print()


utils.log("Finished")
