#include "hierarchy_graph.h"

std::unique_ptr<Graph> GenerateHierarchicalGraph(
    const Graph& old_graph,
    const std::map<Graph::Node, int> clusters) {
  auto new_graph = std::make_unique<Graph>();

  for (Graph::Node node : old_graph.nodes()) {
    node ++;
  }

  // TODO
  return nullptr;
}
