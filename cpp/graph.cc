#include "graph.h"

#include <fstream>
#include <iostream>
#include <memory>
#include <sstream>

Graph::~Graph() {}

void Graph::AddEdge(Node node_a, Node node_b, double weight) {
  AddDirectedEdge(node_a, node_b, weight);
  AddDirectedEdge(node_b, node_a, weight);
  num_edges_ += 1;
}

void Graph::AddDirectedEdge(Node start_node, Node end_node, double weight) {
  std::map<Node, double>& neighbors = edges_[start_node];
  // If this is the first time this edge was added, initialize it.
  neighbors.emplace(end_node, 0.0);
  neighbors[end_node] += weight;
}

bool Graph::HasEdge(Node node_a, Node node_b) const {
  const std::map<Node, double>& neighbors = edges_.at(node_a);
  return neighbors.find(node_b) != neighbors.end();
}

std::vector<Graph::Node> Graph::nodes() const {
  std::vector<int> nodes;
  for (const auto& [node, value] : edges_) {
    nodes.push_back(node);
  }
  return nodes;
}

// static
std::unique_ptr<Graph> Graph::LoadFromAdjList(
    const std::string& filename) {
  auto graph = std::make_unique<Graph>();

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
      Graph::Node start_node = 0;
      std::string field;
      while (std::getline(line_stream, field, ' ')) {
        if (first_field) {
          // First number is start_node.
          start_node = std::stoi(field);
          first_field = false;
        } else {
          // Subsequent numbers are neighbors of start_node.
          const Graph::Node end_node = std::stoi(field);
          // Unweighted edges.
          graph->AddEdge(start_node, end_node);
        }
      }
    }
  }
  file.close();

  return graph;
}
