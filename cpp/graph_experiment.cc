// Attempt at efficient graph algorithms for giant graphs in C++.

#include <iostream>
#include <fstream>
#include <string>

#include "chinese_whispers.h"
#include "graph.h"
#include "hierarchy_graph.h"
#include "timer.h"
#include "util.h"

int main(int argc, char* argv[]) {
  Timer timer;

  if (argc < 3) {
    throw std::invalid_argument("Parameter required.");
  }
  const std::string filename = argv[1];
  const int iterations = std::stoi(argv[2]);

  std::cout << "Loading graph from " << filename
    << " (" << timer.ElapsedSeconds() << "s)" << std::endl;
  auto graph = Graph::LoadFromAdjList(filename);

  for (int level = 0; graph->num_edges() > 0; ++level) {
    std::cout << "Computing clusters [Level " << level << "]"
      << " #Nodes=" << graph->num_nodes()
      << " #Edges=" << graph->num_edges()
      << " (" << timer.ElapsedSeconds() << "s)" << std::endl;
    Clustering clustering;
    ClusterChineseWhispers(*graph, iterations, &clustering);

    std::cout << "Calculating modularity "
      << " (" << timer.ElapsedSeconds() << "s)" << std::endl;
    const double modularity = Modularity(*graph, clustering);
    std::cout << "Cluster stats: # Clusters = " << clustering.num_clusters()
      // TODO: << " Max cluster size = " << max_size
      << " Modularity = " << modularity
      << " (" << timer.ElapsedSeconds() << "s)" << std::endl;

    std::cout << "Producing hierarical graph"
      << " (" << timer.ElapsedSeconds() << "s)" << std::endl;
    graph = GenerateHierarchicalGraph(*graph, clustering);
  }

  std::cout << "Done (" << timer.ElapsedSeconds() << "s)" << std::endl;
  return 0;
}
