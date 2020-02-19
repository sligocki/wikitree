#ifndef WIKITREE_MAP_VECTOR_GRAPH_H_
#define WIKITREE_MAP_VECTOR_GRAPH_H_

#include <map>
#include <memory>
#include <string>
#include <vector>

// Undirected unweighted graph implementation using a std::map of std::vectors.
// Nodes are ints.
// Note: This graph class cannot represent nodes with degree 0. Only Nodes
// which have at least one edge.
class MapVectorGraph {
 public:
  using Node = int;

  MapVectorGraph() {}
  ~MapVectorGraph();

  void AddEdge(Node node_a, Node node_b);

  // List neighbors of a node.
  const std::vector<Node>& neighbors(Node node) const {
    return edges_.at(node);
  }

  // Create a vector copy of nodes.
  // TODO: Figure out a way to iterate over nodes for efficiency if don't need a copy of nodes.
  std::vector<Node> nodes() const;

  int num_nodes() const { return edges_.size(); }
  int num_edges() const { return num_edges_; }

  static std::unique_ptr<MapVectorGraph> LoadFromAdjList(
    const std::string& filename);

 private:
  void AddDirectedEdge(Node start_node, Node end_node);

  int num_edges_ = 0;
  std::map<Node, std::vector<Node> > edges_;
};

#endif  // WIKITREE_MAP_VECTOR_GRAPH_H_
