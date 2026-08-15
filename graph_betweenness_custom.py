import argparse
import csv
import random
from collections import defaultdict
import time

import networkx as nx
import networkit as nk

import graph_tools
import utils

def main():
    parser = argparse.ArgumentParser(description="Monte Carlo Weighted Betweenness")
    parser.add_argument("in_graph", help="Input graph file")
    parser.add_argument("collapse_csv", help="topo.collapse.csv file")
    parser.add_argument("--out_nodes", default="top_weighted_nodes.csv")
    parser.add_argument("--out_edges", default="top_weighted_edges.csv")
    parser.add_argument("--samples", type=int, default=100000, help="Number of path samples")
    args = parser.parse_args()

    utils.log(f"Reading graph from {args.in_graph}")
    Gnx = graph_tools.load_graph(args.in_graph)
    
    utils.log("Creating node conversion mappings")
    name2index = {node: index for index, node in enumerate(Gnx.nodes())}
    index2name = {index: node for node, index in name2index.items()}
    
    utils.log("Converting graph to NetworKit")
    is_directed = Gnx.is_directed()
    is_weighted = graph_tools.is_weighted(Gnx)
    
    Gnk = nk.Graph(Gnx.number_of_nodes(), directed=is_directed, weighted=is_weighted)
    
    # Track edges
    added_edges = {}
    for u, v, data in Gnx.edges(data=True):
        u_idx, v_idx = name2index[u], name2index[v]
        if not is_directed and u_idx > v_idx:
            u_idx, v_idx = v_idx, u_idx
            
        weight = data.get('weight', 1.0)
        edge_key = (u_idx, v_idx)
        
        # Collapse parallel edges by taking minimum weight
        if edge_key not in added_edges or weight < added_edges[edge_key]:
            added_edges[edge_key] = weight

    for (u_idx, v_idx), weight in added_edges.items():
        if is_weighted:
            Gnk.addEdge(u_idx, v_idx, w=weight)
        else:
            Gnk.addEdge(u_idx, v_idx)
            
    utils.log("Loading node weights from " + args.collapse_csv)
    # Default weight is 1 (the core node itself)
    node_weights = {idx: 1 for idx in name2index.values()}
    
    with open(args.collapse_csv, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            core_name = row['core_node']
            if core_name in name2index:
                # Add 1 for every node that was collapsed into this core node
                node_weights[name2index[core_name]] += 1
                
    # Prepare arrays for fast weighted sampling
    nodes = list(node_weights.keys())
    weights = [node_weights[n] for n in nodes]
    
    utils.log(f"Starting Monte Carlo Weighted Betweenness ({args.samples:_} samples)...")
    
    node_scores = defaultdict(float)
    edge_scores = defaultdict(float)
    
    start_time = time.time()
    valid_paths = 0
    log_steps = args.samples // 20
    
    for i in range(args.samples):
        if i % log_steps == 0 and i > 0:
            elapsed = time.time() - start_time
            utils.log(f"  Processed {i:_} samples ({elapsed:.1f}s)")
            
        # Sample two nodes based on their exact collapsed mass
        s, t = random.choices(nodes, weights=weights, k=2)
        if s == t:
            continue
            
        # Find shortest path
        bd = nk.distance.BidirectionalDijkstra(Gnk, s, t, storePred=True)
        bd.run()
        path = bd.getPath()
        
        # If nodes are in different components, path will be empty and distance infinite
        # networkit getPath returns empty list if no path or if path is just one edge. 
        # But wait, if s and t are adjacent, getPath() is empty. 
        # Let's check distance to be sure.
        if bd.getDistance() >= 1e20:
            continue
            
        valid_paths += 1
        
        # getPath() returns intermediate nodes only. 
        # So we increment node_scores for them (Betweenness doesn't count endpoints).
        for node in path:
            node_scores[node] += 1.0
            
        # Edge betweenness counts the full path including endpoints
        full_path = [s] + path + [t]
        for u, v in zip(full_path[:-1], full_path[1:]):
            edge = tuple(sorted([u, v])) if not is_directed else (u, v)
            edge_scores[edge] += 1.0

    utils.log(f"Finished sampling. Valid paths found: {valid_paths:_}")
    
    # Sort and output nodes
    scored_nodes = [(index2name[n], score) for n, score in node_scores.items()]
    scored_nodes.sort(key=lambda x: x[1], reverse=True)
    
    with open(args.out_nodes, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["NodeName", "WeightedNodeBetweenness"])
        for node_name, score in scored_nodes[:100]:
            writer.writerow([node_name, score])

    # Sort and output edges
    scored_edges = [((index2name[u], index2name[v]), score) for (u, v), score in edge_scores.items()]
    scored_edges.sort(key=lambda x: x[1], reverse=True)
    
    with open(args.out_edges, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Node1", "Node2", "WeightedEdgeBetweenness"])
        for (u_idx, v_idx), score in scored_edges[:100]:
            writer.writerow([u_idx, v_idx, score])

    utils.log("Done! Top 5 Nodes:")
    for n, s in scored_nodes[:5]:
        utils.log(f"  {n}: {s}")
        
    utils.log("Top 5 Edges:")
    for (u, v), s in scored_edges[:5]:
        utils.log(f"  {u} <-> {v}: {s}")


if __name__ == "__main__":
    main()
