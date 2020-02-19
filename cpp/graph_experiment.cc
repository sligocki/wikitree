// Attempt at efficient graph algorithms for giant graphs in C++.

#include <iostream>
#include <string>

#include "chinese_whispers.h"
#include "map_vector_graph.h"
#include "timer.h"
#include "util.h"

int main(int argc, char* argv[]) {
  Timer timer;

  if (argc < 3) {
    throw std::invalid_argument("Parameter required.");
  }
  const std::string filename(argv[1]);
  const int iterations = std::stoi(argv[2]);

  std::cout << "Loading graph from " << filename
    << " (" << timer.ElapsedSeconds() << "s)" << std::endl;
  auto graph = MapVectorGraph::LoadFromAdjList(filename);

  std::cout << "Graph loaded #Nodes=" << graph->num_nodes()
    << " #Edges=" << graph->num_edges()
    << " (" << timer.ElapsedSeconds() << "s)" << std::endl;

  std::cout << "Computing clusters"
    << " (" << timer.ElapsedSeconds() << "s)" << std::endl;
  std::map<MapVectorGraph::Node, CWLabel> labels;
  ClusterChineseWhispers(*graph, iterations, &labels);

  std::map<CWLabel, int> cluster_sizes;
  for (const auto& [node, label] : labels) {
    cluster_sizes[label] += 1;
  }
  auto [max_label, max_size] = ArgMax(cluster_sizes);
  std::cout << "Cluster stats: # Clusters = " << cluster_sizes.size()
    << " Max cluster size = " << max_size
    << " (" << timer.ElapsedSeconds() << "s)" << std::endl;

  std::cout << "Done (" << timer.ElapsedSeconds() << "s)" << std::endl;
  return 0;
}
