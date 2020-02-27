#include "hierarchy_graph.h"

std::unique_ptr<Graph> GenerateHierarchicalGraph(
    const Graph& old_graph,
    const std::map<Graph::Node, Label>& clusters) {
  auto new_graph = std::make_unique<Graph>();

  for (auto& [start_node, neighbors] : old_graph.edges()) {
    const auto& start_cluster = clusters.at(start_node);
    for (auto& [end_node, weight] : neighbors) {
      // Avoid double adding edges.
      if (end_node < start_node) {
        const auto& end_cluster = clusters.at(end_node);
        // Avoid self edges.
        if (start_cluster != end_cluster) {
          new_graph->AddEdge(start_cluster, end_cluster, weight);
        }
      }
    }
  }

  return new_graph;
}
