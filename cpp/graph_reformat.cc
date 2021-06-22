// Convert from Adjacency list (networkx format) to GML.

#include <algorithm>
#include <fstream>
#include <iostream>
#include <string>

#include <ogdf/basic/Graph_d.h>
#include <ogdf/fileformats/GraphIO.h>

#include "timer.h"
#include "util.h"


ogdf::node get_or_add_node(ogdf::Graph* graph,
                           std::map<std::string, ogdf::node>* label2id,
                           const std::string& label) {
  if (label2id->find(label) == label2id->end()) {
    (*label2id)[label] = graph->newNode();
  }
  return (*label2id)[label];
}

void load_graph_from_adj_list(
    const std::string& filename,
    ogdf::Graph* graph) {
  // Map: node label/name -> index.
  std::map<std::string, ogdf::node> label2id;

  std::ifstream file;
  file.open(filename);
  if (!file.is_open()) {
    throw std::runtime_error("File does not exist.");
  }
  std::string line;
  while (std::getline(file, line)) {
    if (line.size() > 0 && line[0] != '#') {
      std::istringstream line_stream(line);
      bool first_field = true;
      ogdf::node start_node;
      std::string field;
      while (std::getline(line_stream, field, ' ')) {
        if (first_field) {
          // First number is start_node.
          start_node = get_or_add_node(graph, &label2id, field);
          first_field = false;
        } else {
          // Subsequent numbers are neighbors of start_node.
          const ogdf::node end_node = get_or_add_node(graph, &label2id, field);
          // Unweighted edges.
          graph->newEdge(start_node, end_node);
        }
      }
    }
  }
  file.close();
}


int main(int argc, char* argv[]) {
  Timer timer;

  if (argc != 3) {
    throw std::invalid_argument("Usage: graph_reformat graph_in graph_out");
  }
  const std::string infilename = argv[1];
  const std::string outfilename = argv[2];

  std::cout << "Loading graph from " << infilename
    << " (" << timer.ElapsedSeconds() << "s)" << std::endl;
  ogdf::Graph graph;
  load_graph_from_adj_list(infilename, &graph);
  std::cout << "Loaded graph:  # Nodes: " << graph.numberOfNodes()
            << " # Edges: " << graph.numberOfEdges()
            << " (" << timer.ElapsedSeconds() << "s)" << std::endl;

  std::cout << "Writing graph to " << outfilename
    << " (" << timer.ElapsedSeconds() << "s)" << std::endl;
  if (!ogdf::GraphIO::write(graph, outfilename)) {
    std::cerr << "ERROR writing graph" << std::endl;
    return 1;
  }

  std::cout << "Done (" << timer.ElapsedSeconds() << "s)" << std::endl;
  return 0;
}
