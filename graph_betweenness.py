import argparse
import csv

import networkx as nx
import networkit as nk

import graph_tools
import utils

def main():
  parser = argparse.ArgumentParser(description="Compute Approximate Betweenness for a graph.")
  parser.add_argument("in_graph", help="Input graph file")
  parser.add_argument("--out_csv", help="Optional output CSV for top nodes", default=None)
  parser.add_argument("--top_n", type=int, default=100, help="Number of top nodes to print/save")
  parser.add_argument("--epsilon", type=float, default=0.01, help="Maximum error (smaller = more accurate but slower)")
  args = parser.parse_args()

  utils.log(f"Reading graph from {args.in_graph}")
  
  Gnx = graph_tools.load_graph(args.in_graph)
  
  utils.log("Creating node id -> num conversion")
  name2index = {node: index for index, node in enumerate(Gnx.nodes())}
  index2name = {index: node for node, index in name2index.items()}
  
  utils.log("Converting graph to NetworKit")
  is_directed = Gnx.is_directed()
  is_weighted = graph_tools.is_weighted(Gnx)
  
  # networkit does not support multigraphs for standard betweenness. 
  # We will collapse parallel edges by taking the minimum weight (shortest path).
  Gnk = nk.Graph(Gnx.number_of_nodes(), directed=is_directed, weighted=is_weighted)
  
  added_edges = {}
  
  for u, v, data in Gnx.edges(data=True):
      u_idx, v_idx = name2index[u], name2index[v]
      if not is_directed and u_idx > v_idx:
          u_idx, v_idx = v_idx, u_idx
          
      weight = data.get('weight', 1.0)
      edge_key = (u_idx, v_idx)
      
      if edge_key not in added_edges:
          added_edges[edge_key] = weight
      else:
          if weight < added_edges[edge_key]:
              added_edges[edge_key] = weight

  for (u_idx, v_idx), weight in added_edges.items():
      if is_weighted:
          Gnk.addEdge(u_idx, v_idx, w=weight)
      else:
          Gnk.addEdge(u_idx, v_idx)

  utils.log(f"Running Approximate Betweenness algorithm (epsilon={args.epsilon}, delta=0.1)...")
  
  # For ApproxBetweenness, epsilon is maximum error, delta is probability of exceeding it.
  bc = nk.centrality.ApproxBetweenness(Gnk, epsilon=args.epsilon, delta=0.1)
  bc.run()

  utils.log("Betweenness finished. Sorting results...")
  scores = bc.scores()
  
  scored_nodes = [(index2name[i], score) for i, score in enumerate(scores)]
  scored_nodes.sort(key=lambda x: x[1], reverse=True)
  
  top_nodes = scored_nodes[:args.top_n]
  
  print(f"\nTop {args.top_n} nodes by Approximate Betweenness:")
  for rank, (node_name, score) in enumerate(top_nodes, 1):
      print(f"{rank:3d}: {node_name} (Score: {score:.6f})")

  if args.out_csv:
      utils.log(f"Writing top {args.top_n} to {args.out_csv}...")
      with open(args.out_csv, 'w', newline='') as f:
          writer = csv.writer(f)
          writer.writerow(["Rank", "NodeName", "BetweennessScore"])
          for rank, (node_name, score) in enumerate(top_nodes, 1):
              writer.writerow([rank, node_name, score])

  utils.log("Finished")

if __name__ == "__main__":
  main()
