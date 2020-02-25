#ifndef WIKITREE_GRAPH_H_
#define WIKITREE_GRAPH_H_

#include <map>
#include <memory>
#include <string>
#include <vector>

// Undirected weighted graph implementation using a std containers.
//
// Nodes are ints. Weights are doubles.
//
// Note: This graph class cannot represent nodes with degree 0. Only Nodes
// which have at least one edge.
class Graph {
 public:
  using Node = int;

  Graph() {}
  ~Graph();

  // Represents unweighted graphs with default weight = 1.0.
  // There can be at most one edge between any two nodes. If the same edges
  // is added multiple times, we represent that by one edges with weight
  // equal to the sum of all weights of the added edges.
  void AddEdge(Node node_a, Node node_b, double weight = 1.0);

  bool HasEdge(Node node_a, Node node_b) const;

  // List neighbors of a node and their weights.
  const std::map<Node, double>& neighbors(Node node) const {
    return edges_.at(node);
  }
  // TODO: Convert this to work as sum of weights?
  int degree(Node node) const {
    return neighbors(node).size();
  }

  // Create a vector copy of nodes.
  // TODO: Figure out a way to iterate over nodes for efficiency if don't need a copy of nodes.
  std::vector<Node> nodes() const;

  const std::map<Node, std::map<Node, double> >& edges() const { return edges_; }

  int num_nodes() const { return edges_.size(); }
  int num_edges() const { return num_edges_; }

  static std::unique_ptr<Graph> LoadFromAdjList(
    const std::string& filename);

 private:
  void AddDirectedEdge(Node start_node, Node end_node, double weight);

  int num_edges_ = 0;
  std::map<Node, std::map<Node, double> > edges_;
};

#endif  // WIKITREE_GRAPH_H_
