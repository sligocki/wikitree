// Drop random vertices to shrink graph.

#include <algorithm>
#include <fstream>
#include <iostream>
#include <string>

#include <ogdf/basic/Graph_d.h>
#include <ogdf/basic/extended_graph_alg.h>
#include <ogdf/basic/simple_graph_alg.h>
#include <ogdf/fileformats/GraphIO.h>

#include "random.h"
#include "timer.h"
#include "util.h"


int main(int argc, char* argv[]) {
  Timer timer;
  Random random;

  if (argc != 4) {
    throw std::invalid_argument("Usage: graph_reformat graph_in frac_keep graph_out");
  }
  const std::string infilename = argv[1];
  const double frac_keep = std::stod(argv[2]);
  const std::string outfilename = argv[3];

  std::cout << "Loading graph from " << infilename
    << " (" << timer.ElapsedSeconds() << "s)" << std::endl;
  ogdf::Graph graph;
  bool success = ogdf::GraphIO::read(graph, infilename, ogdf::GraphIO::read);
  if (!success) {
    std::cout << "Error loading file" << std::endl;
    return 1;
  }
  std::cout << "Loaded graph:  # Nodes: " << graph.numberOfNodes()
            << " # Edges: " << graph.numberOfEdges()
            << " (" << timer.ElapsedSeconds() << "s)" << std::endl;

  std::cout << "Dropping half the nodes (" << timer.ElapsedSeconds() << "s)" << std::endl;
  ogdf::List<ogdf::node> subgraph_nodes;
  for (const ogdf::node v : graph.nodes) {
    if (random.UniformReal(0, 1) < frac_keep) {
      subgraph_nodes.pushBack(v);
    }
  }
  ogdf::Graph subgraph;
  ogdf::inducedSubGraph(graph, subgraph_nodes.begin(), subgraph);
  std::cout << "Reduced graph to:  # Nodes: " << subgraph.numberOfNodes()
            << " # Edges: " << subgraph.numberOfEdges()
            << " (" << timer.ElapsedSeconds() << "s)" << std::endl;

  std::cout << "Writing subgraph to " << outfilename
    << " (" << timer.ElapsedSeconds() << "s)" << std::endl;
  if (!ogdf::GraphIO::write(subgraph, outfilename)) {
    std::cerr << "ERROR writing graph" << std::endl;
    return 1;
  }

  std::cout << "Done (" << timer.ElapsedSeconds() << "s)" << std::endl;
  return 0;
}
