// Load degree distribution of a graph.

#include <iostream>
#include <fstream>
#include <map>
#include <string>

#include "graph.h"
#include "timer.h"
#include "util.h"

int main(int argc, char* argv[]) {
  Timer timer;

  if (argc < 2) {
    throw std::invalid_argument("Parameter required.");
  }
  const std::string filename = argv[1];

  std::cout << "Loading graph from " << filename
    << " (" << timer.ElapsedSeconds() << "s)" << std::endl;
  auto graph = Graph::LoadFromAdjList(filename);

  std::cout << "Calculating degree distribution"
    << " (" << timer.ElapsedSeconds() << "s)" << std::endl;
  // degree_counts[d] = #{node : degree(node) == d}
  std::map<int, int> degree_counts;
  for (const auto& [node, neighbors] : graph->edges()) {
    const int degree = neighbors.size();
    if (degree_counts.find(degree) == degree_counts.end()) {
      degree_counts[degree] = 1;
    } else {
      degree_counts[degree] += 1;
    }
  }

  for (const auto& [degree, count] : degree_counts) {
    std::cout << "Degree\t" << degree << "\t" << count << std::endl;
  }

  std::cout << "Done (" << timer.ElapsedSeconds() << "s)" << std::endl;
  return 0;
}
