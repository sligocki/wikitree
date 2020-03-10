// Compare 2 clusterings for similarity.

#include <iostream>
#include <fstream>
#include <string>

#include "chinese_whispers.h"
#include "clustering.h"
#include "graph.h"
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
  std::cout << "Loaded graph"
    << " #Nodes=" << graph->num_nodes()
    << " #Edges=" << graph->num_edges()
    << " (" << timer.ElapsedSeconds() << "s)" << std::endl;

  Clustering clustering[2];
  for (int i = 0; i < 2; ++i) {
    std::cout << "Computing clustering " << i
      << " (" << timer.ElapsedSeconds() << "s)" << std::endl;
    ClusterChineseWhispers(*graph, iterations, &clustering[i]);
    std::cout << "Computing entropy " << i
      << " (" << timer.ElapsedSeconds() << "s)" << std::endl;
    std::cout << "Entropy of clustering " << i << ": " << Entropy(clustering[i])
      << " (" << timer.ElapsedSeconds() << "s)" << std::endl;
  }

  std::cout << "Mutual information of two clusterings: "
    << MutualInformation(clustering[0], clustering[1])
    << " (" << timer.ElapsedSeconds() << "s)" << std::endl;

  std::cout << "Conditional probabilities of two clusterings: "
    << ConditionalProbabilitySimlarity(clustering[0], clustering[1])
    << " " << ConditionalProbabilitySimlarity(clustering[1], clustering[0])
    << " " << ConditionalProbabilitySimlarity(clustering[0], clustering[0])
    << " " << ConditionalProbabilitySimlarity(clustering[1], clustering[1])
    << " (" << timer.ElapsedSeconds() << "s)" << std::endl;

  std::cout << "Done (" << timer.ElapsedSeconds() << "s)" << std::endl;
  return 0;
}
