// Attempt at efficient graph algorithms for giant graphs in C++.

#include <chrono>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <string>
#include <vector>

#include <lemon/lgf_reader.h>
#include <lemon/lgf_writer.h>
#include <lemon/list_graph.h>

class Graph {
 public:
  Graph() {}
  ~Graph() {}

  const lemon::ListGraph::Node& GetNode(int label) {
    if (nodes_.count(label) == 0) {
      nodes_[label] = graph_.addNode();
    }
    return nodes_[label];
  }

  void AddEdge(int start_label, int end_label) {
    auto& start_node = GetNode(start_label);
    auto& end_node = GetNode(end_label);
    graph_.addEdge(start_node, end_node);
  }

  int num_nodes() const {
    return lemon::countNodes(graph_);
  }
  int num_edges() const {
    return lemon::countEdges(graph_);
  }

  lemon::ListGraph& lemon_graph() {
    return graph_;
  }

 private:
  std::map<int, lemon::ListGraph::Node> nodes_;
  lemon::ListGraph graph_;
};

std::unique_ptr<Graph> LoadGraphFromAdjList(const std::string& filename) {
  auto graph = std::make_unique<Graph>();

  std::ifstream file;
  file.open(filename);
  std::string line;
  int num_edges = 0;
  while (std::getline(file, line)) {
    if (line.size() > 0 && line[0] != '#') {
      std::istringstream line_stream(line);
      bool first_field = true;
      int start_label = 0;
      std::string field;
      while (std::getline(line_stream, field, ' ')) {
        if (first_field) {
          // First number is start_label.
          start_label = std::stoi(field);
          first_field = false;
        } else {
          // Subsequent numbers are neighbors of start_label.
          const int end_label = std::stoi(field);
          graph->AddEdge(start_label, end_label);
          num_edges += 1;
          if (num_edges % 1000000 == 0) {
            std::cout << " ... " << graph->num_nodes() << " nodes & "
              << num_edges << " edges." << std::endl;
          }
        }
      }
    }
  }

  return graph;
}

double seconds_since(const std::chrono::high_resolution_clock::time_point start_time) {
  const auto end_time = std::chrono::high_resolution_clock::now();
  const std::chrono::duration<double> time_diff = end_time - start_time;
  return time_diff.count();
}

using namespace lemon;

int main(int argc, char* argv[]) {
  const auto start_time = std::chrono::high_resolution_clock::now();

  const std::string filename(argv[1]);

  std::cout << "Loading graph from " << filename
    << " (" << seconds_since(start_time) << "s)" << std::endl;
  auto graph = LoadGraphFromAdjList(filename);
  std::cout << "Graph loaded #Nodes=" << graph->num_nodes()
    << " #Edges=" << graph->num_edges()
    << " (" << seconds_since(start_time) << "s)" << std::endl;

  std::cout << "Writing graph to file"
    << " (" << seconds_since(start_time) << "s)" << std::endl;
  graphWriter(graph->lemon_graph(), "main_component.lgf")
    .run();

  std::cout << "Reading graph from file"
    << " (" << seconds_since(start_time) << "s)" << std::endl;
  lemon::ListGraph g;
  graphReader(g, "main_component.lgf")
    .run();
  std::cout << "Loaded graph #Nodes=" << lemon::countNodes(g)
    << " #Edges=" << lemon::countEdges(g)
    << " (" << seconds_since(start_time) << "s)" << std::endl;

  std::cout << "Done (" << seconds_since(start_time) << "s)" << std::endl;
  return 0;
}
