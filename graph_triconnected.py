from sage.all import *
import networkx as nx
import time
import json
import csv

def main():
    print("Loading fast_metric_core...")
    t0 = time.time()
    G_multi = nx.read_weighted_edgelist('data/version/2026-07-26/graphs/family/fast_metric_core.multi.weight.edges.nx', create_using=nx.MultiGraph)
    print(f"Loaded multigraph in {time.time() - t0:.2f}s")
    
    print("Converting to simple graph...")
    G = nx.Graph(G_multi)
    G.remove_edges_from(nx.selfloop_edges(G))
    print(f"Simple graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    
    print("Finding biconnected components...")
    t0 = time.time()
    bicomps = list(nx.biconnected_components(G))
    print(f"Found {len(bicomps)} biconnected components in {time.time() - t0:.2f}s")
    
    triconnected_comps = []
    
    print("Building SPQR trees...")
    t0 = time.time()
    
    for i, comp in enumerate(bicomps):
        if len(comp) < 4:
            continue
            
        if i % 1000 == 0:
            print(f"Processed {i}/{len(bicomps)} components...")
            
        # Extract subgraph edges
        subgraph = G.subgraph(comp)
        edges = list(subgraph.edges())
        
        # Map nodes to integers
        node_to_int = {}
        int_to_node = {}
        int_edges = []
        for u, v in edges:
            if u not in node_to_int:
                idx = len(node_to_int)
                node_to_int[u] = idx
                int_to_node[idx] = u
            if v not in node_to_int:
                idx = len(node_to_int)
                node_to_int[v] = idx
                int_to_node[idx] = v
            int_edges.append((node_to_int[u], node_to_int[v]))
        
        # Build Sage Graph
        print(f"  [{time.time()-t0:.2f}s] Building Sage Graph for component {i} (size {len(comp)})...")
        t_sg = time.time()
        sg = Graph(int_edges)
        print(f"  [{time.time()-t0:.2f}s] Built Sage Graph in {time.time()-t_sg:.2f}s")
        
        try:
            # Build SPQR tree
            print(f"  [{time.time()-t0:.2f}s] Calling sg.spqr_tree()...")
            t_spqr = time.time()
            tree = sg.spqr_tree()
            print(f"  [{time.time()-t0:.2f}s] SPQR tree built in {time.time()-t_spqr:.2f}s")
            
            for v in tree.vertices():
                if v[0] == 'R':
                    r_nodes = [int_to_node[n] for n in v[1].vertices()]
                    if len(r_nodes) >= 4:
                        triconnected_comps.append(r_nodes)
        except Exception as e:
            print(f"Error processing component of size {len(comp)}: {e}")
            
    print(f"Found {len(triconnected_comps)} triconnected components in {time.time() - t0:.2f}s")
    
    triconnected_comps.sort(key=len, reverse=True)
    
    out_file = 'data/version/2026-07-26/graphs/family/triconnected_fast_metric_core.json'
    print(f"Writing results to {out_file}...")
    with open(out_file, 'w') as f:
        json.dump(triconnected_comps, f)
        
    print("Done!")
    
    print("\nTop 10 largest triconnected islands:")
    for i, comp in enumerate(triconnected_comps[:10]):
        print(f"  {i+1}. Size: {len(comp)} nodes")

if __name__ == "__main__":
    main()
