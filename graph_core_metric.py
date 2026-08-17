import networkx as nx
import graph_tools
import time
from pathlib import Path
from collections import defaultdict

def remove_parallel_edges(G):
    """Globally remove all parallel edges, keeping only the minimum weight edge."""
    count_removed = 0
    edge_dict = {}
    for u, v, k, d in G.edges(keys=True, data=True):
        edge_id = tuple(sorted([u, v]))
        w = d.get('weight', 1.0)
        if edge_id not in edge_dict:
            edge_dict[edge_id] = []
        edge_dict[edge_id].append((w, u, v, k))
        
    for edge_id, edge_list in edge_dict.items():
        if len(edge_list) > 1:
            edge_list.sort(key=lambda x: x[0])
            for w, u, v, k in edge_list[1:]:
                G.remove_edge(u, v, key=k)
                count_removed += 1
                
    return count_removed

def contract_metric_graph(G, new_edges_queue):
    to_delete = set()
    for n in list(G.nodes):
        if G.degree[n] <= 2:
            to_delete.add(n)
            
    if not to_delete:
        return False, 0
        
    contracted_count = 0
    for node in to_delete:
        if node not in G: 
            continue
            
        deg = G.degree[node]
        if deg == 0:
            G.remove_node(node)
            contracted_count += 1
        elif deg == 1:
            G.remove_node(node)
            contracted_count += 1
        elif deg == 2:
            neighbors = list(G.adj[node].keys())
            if len(neighbors) == 1:
                G.remove_node(node)
                contracted_count += 1
            else:
                a, b = neighbors
                wa = list(G[node][a].values())[0].get('weight', 1.0)
                wb = list(G[node][b].values())[0].get('weight', 1.0)
                
                G.remove_node(node)
                new_w = wa + wb
                k = G.add_edge(a, b, weight=new_w)
                
                if new_w > 1.0:
                    new_edges_queue.append((a, b, k, new_w))
                
                contracted_count += 1
                
    return True, contracted_count

def main():
    print("Loading initial topological core...", flush=True)
    t0 = time.time()
    G = graph_tools.load_graph('data/version/2026-07-26/graphs/family/topo.multi.weight.edges.nx')
    print(f"Loaded in {time.time() - t0:.2f}s", flush=True)
    
    total_pruned = 0
    total_contracted = 0
    
    print("\n=== Pre-processing ===", flush=True)
    t_start = time.time()
    parallel_removed = remove_parallel_edges(G)
    print(f"Removed {parallel_removed} parallel edges globally in {time.time() - t_start:.2f}s.", flush=True)
    total_pruned += parallel_removed
    
    new_edges_queue = []
    for u, v, k, d in G.edges(keys=True, data=True):
        w = d.get('weight', 1.0)
        if w > 1.0:
            new_edges_queue.append((u, v, k, w))
            
    iteration = 1
    
    while True:
        print(f"\n=== Iteration {iteration} ===", flush=True)
        print(f"Graph size: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges", flush=True)
        
        edges_to_check = new_edges_queue
        new_edges_queue = [] 
        
        pruned_this_round = 0
        t_start = time.time()
        
        # Optimization: Group edges by source node to minimize Dijkstra calls
        source_groups = defaultdict(list)
        for u, v, k, w in edges_to_check:
            if G.has_edge(u, v, key=k):
                source_groups[u].append((v, k, w))
                
        nodes_checked = 0
        for u, targets in source_groups.items():
            nodes_checked += 1
            if nodes_checked % 5000 == 0:
                print(f"  Processed {nodes_checked}/{len(source_groups)} sources...", flush=True)
                
            # Temporarily remove all target edges from this source
            removed_edges = []
            for v, k, w in targets:
                if G.has_edge(u, v, key=k):
                    edge_data = G.get_edge_data(u, v, k)
                    G.remove_edge(u, v, key=k)
                    removed_edges.append((v, k, w, edge_data))
            
            if not removed_edges:
                continue
                
            max_cutoff = max([w for _, _, w, _ in removed_edges]) - 0.001
            try:
                reachable = nx.single_source_dijkstra_path_length(G, u, cutoff=max_cutoff, weight='weight')
                for v, k, w, edge_data in removed_edges:
                    if v in reachable and reachable[v] < w:
                        pruned_this_round += 1
                    else:
                        G.add_edge(u, v, key=k, **edge_data)
            except Exception:
                for v, k, w, edge_data in removed_edges:
                    G.add_edge(u, v, key=k, **edge_data)
                    
        print(f"Pruned {pruned_this_round} triangle-violating edges in {time.time() - t_start:.2f}s.", flush=True)
        total_pruned += pruned_this_round
        
        contracted_this_round = 0
        while True:
            changed, count = contract_metric_graph(G, new_edges_queue)
            if not changed:
                break
            contracted_this_round += count
            
        print(f"Contracted {contracted_this_round} degree-1 or degree-2 nodes.", flush=True)
        total_contracted += contracted_this_round
        
        if pruned_this_round == 0 and contracted_this_round == 0 and len(new_edges_queue) == 0:
            print("Stable metric core reached! No more changes.", flush=True)
            break
            
        iteration += 1

    print("\n=== FINAL RESULTS ===", flush=True)
    print(f"Total edges pruned: {total_pruned}", flush=True)
    print(f"Total nodes contracted: {total_contracted}", flush=True)
    print(f"Final Metric Core: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges", flush=True)
    
    out_file = 'data/version/2026-07-26/graphs/family/fast_metric_core'
    print(f"Saving Metric Core to {out_file} ...", flush=True)
    graph_tools.write_graph(G, Path(out_file))
    print("Saved.", flush=True)

if __name__ == "__main__":
    main()
