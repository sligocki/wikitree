// Attempt at efficient graph algorithms for giant graphs in C++.

#include <iostream>

#include "map_vector_graph.h"
#include "timer.h"

int main(int argc, char* argv[]) {
  Timer timer;

  const std::string filename(argv[1]);

  std::cout << "Loading graph from " << filename
    << " (" << timer.ElapsedSeconds() << "s)" << std::endl;
  auto graph = MapVectorGraph::LoadFromAdjList(filename);

  std::cout << "Graph loaded #Nodes = " << graph->num_nodes()
    << " #Edges = " << graph->num_edges()
    << " (" << timer.ElapsedSeconds() << "s)" << std::endl;

  return 0;
}
