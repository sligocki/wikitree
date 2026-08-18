import pandas as pd
import numpy as np
import time
from pathlib import Path
import csv

def get_bipartite_edges(data_dir):
    print("Loading people...", flush=True)
    people = pd.read_parquet(data_dir / "people.parquet",
                             columns=["user_num", "mother_num", "father_num"],
                             dtype_backend="numpy_nullable")
    
    print("Processing families...", flush=True)
    def pack_union(p1, p2):
        p1 = p1.fillna(-1).astype(np.int64)
        p2 = p2.fillna(-1).astype(np.int64)
        min_p = np.minimum(p1, p2)
        max_p = np.maximum(p1, p2)
        return min_p * 4294967296 + (max_p & 0xFFFFFFFF)

    complete = people[people.mother_num.notna() & people.father_num.notna()]
    f_complete = pack_union(complete.mother_num, complete.father_num)
    
    mother_only = people[people.mother_num.notna() & people.father_num.isna()]
    f_mother_only = pack_union(mother_only.mother_num, pd.Series(-1, index=mother_only.index))
    
    father_only = people[people.mother_num.isna() & people.father_num.notna()]
    f_father_only = pack_union(pd.Series(-1, index=father_only.index), father_only.father_num)
    
    child_person = pd.concat([complete.user_num, mother_only.user_num, father_only.user_num]).astype(np.int64)
    child_family = pd.concat([f_complete, f_mother_only, f_father_only])
    
    parent_person = pd.concat([mother_only.mother_num, father_only.father_num]).astype(np.int64)
    parent_family = pd.concat([f_mother_only, f_father_only])
    
    print("Loading couples...", flush=True)
    couples = pd.read_parquet(data_dir / "rel_couples.parquet")
    couple_person = couples.user_num.astype(np.int64)
    couple_family = pack_union(couples.user_num, couples.relative_num)
    
    all_person = pd.concat([child_person, parent_person, couple_person])
    all_family = pd.concat([child_family, parent_family, couple_family])
    
    print(f"Total edges raw: {len(all_person)}", flush=True)
    
    valid_mask = (all_person.values >= 0) & (all_family.values >= 0)
    all_person = all_person[valid_mask]
    all_family = all_family[valid_mask]
    
    print(f"Total edges after valid filter: {len(all_person)}", flush=True)
    
    print("Factorizing families...", flush=True)
    family_codes, family_uniques = pd.factorize(all_family)
    
    max_person = all_person.max()
    family_codes += (max_person + 1)
    
    edges = np.column_stack((all_person.values, family_codes))
    num_nodes = max_person + 1 + len(family_uniques)
    
    return edges, num_nodes, max_person, family_uniques

def compute_topo_core(edges, num_nodes, max_person, family_uniques):
    print("Building adjacency list...", flush=True)
    head = np.zeros(num_nodes + 1, dtype=np.int64)
    for i in range(len(edges)):
        u, v = edges[i]
        head[u+1] += 1
        head[v+1] += 1
    
    np.cumsum(head, out=head)
    
    adj = np.zeros(head[-1], dtype=np.int32)
    cur_head = head[:-1].copy()
    for i in range(len(edges)):
        u, v = edges[i]
        adj[cur_head[u]] = v
        cur_head[u] += 1
        adj[cur_head[v]] = u
        cur_head[v] += 1
        
    print("Pruning leaves...", flush=True)
    degree = np.zeros(num_nodes, dtype=np.int32)
    for i in range(num_nodes):
        degree[i] = head[i+1] - head[i]
        
    leaf_parent = np.full(num_nodes, -1, dtype=np.int32)
    path_end1 = np.full(num_nodes, -1, dtype=np.int32)
    path_end2 = np.full(num_nodes, -1, dtype=np.int32)
        
    queue = np.zeros(num_nodes, dtype=np.int32)
    front, back = 0, 0
    for i in range(num_nodes):
        if degree[i] <= 1:
            queue[back] = i
            back += 1
            
    while front < back:
        u = queue[front]
        front += 1
        degree[u] = 0
        
        for idx in range(head[u], head[u+1]):
            v = adj[idx]
            if degree[v] > 0:
                leaf_parent[u] = v
                degree[v] -= 1
                if degree[v] == 1:
                    queue[back] = v
                    back += 1

    print("Collapsing paths (tracing from degree >= 3)...", flush=True)
    core_edges = []
    visited = np.zeros(num_nodes, dtype=bool)
    
    for u in range(num_nodes):
        if degree[u] >= 3:
            for idx in range(head[u], head[u+1]):
                v = adj[idx]
                if degree[v] == 0:
                    continue
                
                if degree[v] >= 3:
                    if u <= v:
                        core_edges.append((u, v, 1))
                        
                elif degree[v] == 2:
                    if visited[v]:
                        continue
                    
                    prev = u
                    curr = v
                    path_len = 1
                    path_nodes = []
                    
                    while degree[curr] == 2:
                        visited[curr] = True
                        path_nodes.append(curr)
                        next_node = -1
                        for i_idx in range(head[curr], head[curr+1]):
                            n = adj[i_idx]
                            if n != prev and degree[n] > 0:
                                next_node = n
                                break
                                
                        if next_node == -1:
                            break
                        prev = curr
                        curr = next_node
                        path_len += 1
                        
                    if degree[curr] >= 3:
                        w = curr
                        core_edges.append((u, w, path_len))
                        for x in path_nodes:
                            path_end1[x] = u
                            path_end2[x] = w
                        
    print(f"Topological Core Edges Found: {len(core_edges)}")
    return core_edges, leaf_parent, path_end1, path_end2, degree

def node_to_str(node_id, max_person, family_uniques):
    if node_id <= max_person:
        return str(node_id)
    else:
        packed = family_uniques[node_id - max_person - 1]
        min_p = packed >> 32
        max_p = packed & 0xFFFFFFFF
        if max_p == 0xFFFFFFFF:
            return f"Union/{min_p}"
        else:
            return f"Union/{min_p}/{max_p}"

def main():
    t0 = time.time()
    data_dir = Path("data/version/default")
    edges, num_nodes, max_person, family_uniques = get_bipartite_edges(data_dir)
    print(f"Bipartite Graph: {num_nodes} nodes, {len(edges)} edges", flush=True)
    print(f"Time to parse edges: {time.time()-t0:.2f}s", flush=True)
    
    t1 = time.time()
    core_edges, leaf_parent, path_end1, path_end2, degree = compute_topo_core(edges, num_nodes, max_person, family_uniques)
    print(f"Time to compute core: {time.time()-t1:.2f}s", flush=True)
    
    out_dir = data_dir / "graphs" / "bipartite"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Write the multi weight edge list for networkx compatibility
    nx_file = out_dir / "topo_core.multi.weight.edges.nx"
    print(f"Writing {nx_file}...", flush=True)
    with open(nx_file, "w") as f:
        for u, v, w in core_edges:
            u_str = node_to_str(u, max_person, family_uniques)
            v_str = node_to_str(v, max_person, family_uniques)
            f.write(f"{u_str} {v_str} {w}\n")

    # 2. Generate collapse info
    print("Resolving collapse info...", flush=True)
    
    collapse_file = out_dir / "topo.collapse.csv"
    print(f"Writing {collapse_file}...", flush=True)
    
    # To efficiently write collapse info, we can just trace each node's parents
    # We use memoization/path compression for leaf_parent resolution to be O(N)
    resolved = np.full(num_nodes, -1, dtype=np.int32)
    
    def resolve_root(u):
        if resolved[u] != -1:
            return resolved[u]
        
        p = leaf_parent[u]
        if p == -1:
            resolved[u] = u
            return u
        
        root = resolve_root(p)
        resolved[u] = root
        return root

    with open(collapse_file, "w") as f:
        writer = csv.writer(f)
        writer.writerow(["core_node", "sub_node"])
        
        for i in range(num_nodes):
            if degree[i] >= 3:
                continue # Core node, absorbs itself (can write if needed, graph_core.py writes self?)
                
            root = resolve_root(i)
            if root == -1 or degree[root] == 0:
                continue # Part of isolated pruned component
                
            sub_str = node_to_str(i, max_person, family_uniques)
            
            if degree[root] >= 3:
                # Absorbed by a single core node
                core_str = node_to_str(root, max_person, family_uniques)
                writer.writerow([core_str, sub_str])
                
            elif degree[root] == 2:
                # Absorbed by two endpoints
                e1 = path_end1[root]
                e2 = path_end2[root]
                if e1 != -1 and e2 != -1:
                    e1_str = node_to_str(e1, max_person, family_uniques)
                    e2_str = node_to_str(e2, max_person, family_uniques)
                    writer.writerow([e1_str, sub_str])
                    writer.writerow([e2_str, sub_str])
                    
        # Also write the core nodes absorbing themselves to match graph_core.py
        for i in range(num_nodes):
            if degree[i] >= 3:
                core_str = node_to_str(i, max_person, family_uniques)
                writer.writerow([core_str, core_str])

    print(f"Total time: {time.time()-t0:.2f}s")

if __name__ == "__main__":
    main()
