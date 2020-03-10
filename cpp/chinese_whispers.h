#ifndef WIKITREE_CHINESE_WHISPERS_H_
#define WIKITREE_CHINESE_WHISPERS_H_

#include "clustering.h"
#include "graph.h"

// Cluster using "Chinese Whispers" algorithm:
///  https://en.wikipedia.org/wiki/Chinese_Whispers_(clustering_method)
void ClusterChineseWhispers(const Graph& graph, int iterations,
                            Clustering* labels);

#endif  // WIKITREE_CHINESE_WHISPERS_H_
