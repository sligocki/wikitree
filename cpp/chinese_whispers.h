#ifndef WIKITREE_CHINESE_WHISPERS_H_
#define WIKITREE_CHINESE_WHISPERS_H_

#include <fstream>
#include <map>

#include "graph.h"

using CWLabel = Graph::Node;

// Cluster using "Chinese Whispers" algorithm:
///  https://en.wikipedia.org/wiki/Chinese_Whispers_(clustering_method)
void ClusterChineseWhispers(const Graph& graph,
                            int iterations,
                            std::map<Graph::Node, CWLabel>* labels);

void WriteCluster(
  int level,
  const std::map<Graph::Node, CWLabel> labels,
  std::ofstream* outifle);

#endif  // WIKITREE_CHINESE_WHISPERS_H_
