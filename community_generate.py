"""
Identify communities of graph and save to file.
"""

import argparse

import networkit as nk

import graph_tools
import utils


parser = argparse.ArgumentParser()
parser.add_argument("graph")
parser.add_argument("out_communities")
args = parser.parse_args()

utils.log("Reading graph")
G, names_db = graph_tools.load_graph_nk(args.graph)
utils.log(f"Loaded graph with {G.numberOfNodes():_} nodes / {G.numberOfEdges():_} edges")

utils.log("Calculating communities")
communities = nk.community.detectCommunities(G)

utils.log("Writing Communities to file")
nk.community.writeCommunities(communities, args.out_communities)

utils.log("Finished")
