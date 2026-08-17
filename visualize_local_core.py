import networkx as nx
import graph_tools
import sqlite_reader
import csv
import argparse
from pathlib import Path
import os
import re
import subprocess
import pydot

def get_node_label(node_str, db):
    if node_str.startswith("Union/"):
        parts = node_str.split("/")[1:]
        names = []
        for p in parts:
            try:
                wt_id = db.num2id(int(p))
                name = db.name_of(int(p)) if wt_id else f"User_{p}"
                names.append(f"{name}\\n({wt_id})")
            except:
                names.append(f"User_{p}")
        return "Union of\\n" + "\\n&\\n".join(names)
    else:
        try:
            wt_id = db.num2id(int(node_str))
            name = db.name_of(int(node_str)) if wt_id else f"User_{node_str}"
            return f"{name}\\n({wt_id})"
        except:
            return node_str

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=True, help="WikiTree ID (e.g. Smith-1872)")
    parser.add_argument("--depth", type=int, default=2, help="BFS Depth")
    parser.add_argument("--core", default="fast_metric_core", help="Core name to use")
    args = parser.parse_args()

    print("Loading databases...")
    db = sqlite_reader.Database("default")
    
    try:
        user_num = db.id2num(args.id)
        user_num_str = str(user_num)
        print(f"UserNum for {args.id} is {user_num_str}")
    except Exception as e:
        print(f"Could not find WikiTree ID {args.id}: {e}")
        return

    # Look up in topo.collapse.csv
    print("Searching topo.collapse.csv for associated core nodes...")
    core_nodes = set()
    pattern = re.compile(rf'^(Union/\d+/{user_num_str}|Union/{user_num_str}/\d+|{user_num_str})$')
    
    with open('data/version/2026-07-26/graphs/family/topo.collapse.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader) # skip header
        for row in reader:
            if len(row) < 2: continue
            c_node, s_node = row[0], row[1]
            if pattern.match(s_node):
                core_nodes.add(c_node)

    if not core_nodes:
        print(f"No core nodes found. {args.id} completely evaporated before the topological core.")
        return
        
    print(f"Found {len(core_nodes)} associated core node(s):")
    for cn in core_nodes:
        print(f"  - {cn}")

    # Load core graph
    core_file = f'data/version/2026-07-26/graphs/family/{args.core}.multi.weight.edges.nx'
    if not os.path.exists(core_file):
        print(f"Core file not found: {core_file}")
        return
        
    print(f"Loading {args.core}...")
    G = graph_tools.load_graph(core_file)
    
    # Extract ego graphs
    print(f"Extracting ego graph of depth {args.depth}...")
    subgraphs = []
    for cn in core_nodes:
        if cn in G:
            subgraphs.append(nx.ego_graph(G, cn, radius=args.depth))
        else:
            print(f"  Warning: Node {cn} was in topo core but not found in {args.core}! (It may have been contracted further)")
            
    if not subgraphs:
        print("No subgraphs could be extracted.")
        return
        
    final_G = nx.compose_all(subgraphs)
    print(f"Local neighborhood size: {final_G.number_of_nodes()} nodes, {final_G.number_of_edges()} edges")

    # Generate Graphviz
    print("Generating visualization...")
    dot_graph = pydot.Dot("my_graph", graph_type="graph", rankdir="LR", overlap="false", splines="true", outputorder="edgesfirst")
    
    for n in final_G.nodes():
        label = get_node_label(n, db)
        if n in core_nodes:
            node = pydot.Node(f'"{n}"', label=f'"{label}"', shape="box", style="rounded,filled", fillcolor="lightgreen", penwidth=3, fontname="Arial", fontsize=10)
        else:
            node = pydot.Node(f'"{n}"', label=f'"{label}"', shape="box", style="rounded,filled", fillcolor="lightblue", fontname="Arial", fontsize=10)
        dot_graph.add_node(node)

    for u, v, k, d in final_G.edges(keys=True, data=True):
        w = d.get('weight', 1.0)
        label = f"{w:.1f}" if w != 1.0 else ""
        edge = pydot.Edge(f'"{u}"', f'"{v}"', label=f'"{label}"', penwidth=max(1, 4 - w), fontname="Arial", fontsize=8, color="gray40")
        dot_graph.add_edge(edge)

    dot_file = f"{args.id}_{args.core}_depth{args.depth}.dot"
    out_png = f"{args.id}_{args.core}_depth{args.depth}.png"
    
    print(f"Saving dot file to {dot_file}")
    dot_graph.write_raw(dot_file)
    
    print(f"Laying out graph using fdp...")
    subprocess.run(["fdp", "-Tpng", dot_file, "-o", out_png], check=True)
    
    print(f"Saved visualization to {out_png}")

if __name__ == "__main__":
    main()
