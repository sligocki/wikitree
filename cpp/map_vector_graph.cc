#include "map_vector_graph.h"

#include <fstream>
#include <iostream>
#include <memory>
#include <sstream>

MapVectorGraph::~MapVectorGraph() {}

void MapVectorGraph::AddEdge(int node_a, int node_b) {
  AddDirectedEdge(node_a, node_b);
  AddDirectedEdge(node_b, node_a);
}

void MapVectorGraph::AddDirectedEdge(int start_node, int end_node) {
  edges_[start_node].push_back(end_node);
  num_edges_ += 1;
}

// static
std::unique_ptr<MapVectorGraph> MapVectorGraph::LoadFromAdjList(
    const std::string& filename) {
  auto graph = std::make_unique<MapVectorGraph>();

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
      int start_node = 0;
      std::string field;
      while (std::getline(line_stream, field, ' ')) {
        if (first_field) {
          // First number is start_node.
          start_node = std::stoi(field);
          first_field = false;
        } else {
          // Subsequent numbers are neighbors of start_node.
          const int end_node = std::stoi(field);
          graph->AddEdge(start_node, end_node);
        }
      }
    }
  }
  file.close();

  return graph;
}
