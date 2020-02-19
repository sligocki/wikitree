#ifndef WIKITREE_HIERARCHY_GRAPH_H_
#define WIKITREE_HIERARCHY_GRAPH_H_

#include <map>

#include "graph.h"

// Take a garph and partition (hard clustering) and produce a new smaller graph
// where every node is a cluster from the previous graph and edges between
// clusters are weighted by the sum of all weights of inter-edges between
// clusters.
std::unique_ptr<Graph> GenerateHierarchicalGraph(
  const Graph& graph,
  const std::map<Graph::Node, int> clusters);

#endif  // WIKITREE_HIERARCHY_GRAPH_H_
