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
  MapVectorGraph() {}
  ~MapVectorGraph();

  void AddEdge(int node_a, int node_b);

  // List neighbors of a node.
  const std::vector<int>& neighbors(int node) const {
    return edges_[node];
  }

  int num_nodes() const { return edges_.size(); }
  int num_edges() const { return num_edges_; }

  static std::unique_ptr<MapVectorGraph> LoadFromAdjList(
    const std::string& filename);

 private:
  void AddDirectedEdge(int start_node, int end_node);

  int num_edges_ = 0;
  std::map<int, std::vector<int> > edges_;
};

#endif  // WIKITREE_MAP_VECTOR_GRAPH_H_
