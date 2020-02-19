#ifndef WIKITREE_CHINESE_WHISPERS_H_
#define WIKITREE_CHINESE_WHISPERS_H_

#include <map>

#include "map_vector_graph.h"

using CWLabel = MapVectorGraph::Node;

// Cluster using "Chinese Whispers" algorithm:
///  https://en.wikipedia.org/wiki/Chinese_Whispers_(clustering_method)
void ClusterChineseWhispers(const MapVectorGraph& graph,
                            int iterations,
                            std::map<MapVectorGraph::Node, CWLabel>* labels);

#endif  // WIKITREE_CHINESE_WHISPERS_H_
