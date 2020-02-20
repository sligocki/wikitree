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

  if (argc < 4) {
    throw std::invalid_argument("Parameter required.");
  }
  const std::string filename = argv[1];
  const int iterations = std::stoi(argv[2]);
  const std::string output_filename = argv[3];

  std::ofstream outfile;
  outfile.open(output_filename);
  if (!outfile.is_open()) {
    throw std::runtime_error("Could not create outfile.");
  }

  std::cout << "Loading graph from " << filename
    << " (" << timer.ElapsedSeconds() << "s)" << std::endl;
  auto graph = Graph::LoadFromAdjList(filename);

  for (int level = 0; graph->num_edges() > 0; ++level) {
    std::cout << "Computing clusters [Level " << level << "]"
      << " #Nodes=" << graph->num_nodes()
      << " #Edges=" << graph->num_edges()
      << " (" << timer.ElapsedSeconds() << "s)" << std::endl;
    std::map<Graph::Node, CWLabel> labels;
    ClusterChineseWhispers(*graph, iterations, &labels);

    std::map<CWLabel, int> cluster_sizes;
    for (const auto& [node, label] : labels) {
      cluster_sizes[label] += 1;
    }
    auto [max_label, max_size] = ArgMax(cluster_sizes);
    std::cout << "Cluster stats: # Clusters = " << cluster_sizes.size()
      << " Max cluster size = " << max_size
      << " (" << timer.ElapsedSeconds() << "s)" << std::endl;

    std::cout << "Writing cluster to disk"
      << " (" << timer.ElapsedSeconds() << "s)" << std::endl;
    WriteCluster(level, labels, &outfile);

    std::cout << "Producing hierarical graph"
      << " (" << timer.ElapsedSeconds() << "s)" << std::endl;
    graph = GenerateHierarchicalGraph(*graph, labels);
  }

  outfile.close();
  std::cout << "Done (" << timer.ElapsedSeconds() << "s)" << std::endl;
  return 0;
}
