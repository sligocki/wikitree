// Attempt at efficient graph algorithms for giant graphs in C++.

#include <chrono>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <string>
#include <vector>

class Graph {
 public:
  Graph() {}
  ~Graph() {}

  void AddUndirectedEdge(int node_a, int node_b) {
    AddDirectedEdge(node_a, node_b);
    AddDirectedEdge(node_b, node_a);
  }

  void AddDirectedEdge(int start_node, int end_node) {
    edges_[start_node].push_back(end_node);
    num_edges_ += 1;
  }

  int num_nodes() const {
    return edges_.size();
  }
  int num_edges() const {
    return num_edges_;
  }

 private:
  int num_edges_ = 0;
  std::map<int, std::vector<int> > edges_;
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
          graph->AddUndirectedEdge(start_node, end_node);
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

int main(int argc, char* argv[]) {
  const auto start_time = std::chrono::high_resolution_clock::now();

  const std::string filename(argv[1]);

  std::cout << "Loading graph from " << filename
    << " (" << seconds_since(start_time) << "s)" << std::endl;
  auto graph = LoadGraphFromAdjList(filename);
  std::cout << "Graph loaded #Nodes = " << graph->num_nodes()
    << " #Edges = " << graph->num_edges()
    << " (" << seconds_since(start_time) << "s)" << std::endl;

  return 0;
}
