// Attempt at efficient graph algorithms for giant graphs in C++.

#include <algorithm>
#include <fstream>
#include <iostream>
#include <string>

#include <ogdf/basic/Graph_d.h>
#include <ogdf/basic/simple_graph_alg.h>
#include <ogdf/fileformats/GraphIO.h>
#include <ogdf/graphalg/Triconnectivity.h>

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

bool load_graph_from_adj_list(
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

  return graph;
}


int main(int argc, char* argv[]) {
  Timer timer;

  if (argc != 2) {
    throw std::invalid_argument("Parameter required.");
  }
  const std::string graph_filename = argv[1];

  std::cout << "Loading graph from " << graph_filename
    << " (" << timer.ElapsedSeconds() << "s)" << std::endl;
  ogdf::Graph graph;
  bool success = load_graph_from_adj_list(graph_filename, &graph);
  if (!success) {
    std::cout << "Error loading file" << std::endl;
    return 1;
  }
  std::cout << "Loaded graph:  # Nodes: " << graph.numberOfNodes()
            << " # Edges: " << graph.numberOfEdges()
            << " (" << timer.ElapsedSeconds() << "s)" << std::endl;


  std::cout << "Finding Connected Components (" << timer.ElapsedSeconds() << "s)" << std::endl;
  ogdf::NodeArray<int> component_id(graph);
  const int num_components = ogdf::connectedComponents(graph, component_id);
  std::vector<int> component_sizes(num_components, 0);
  for (const ogdf::node v : graph.nodes) {
    component_sizes.at(component_id[v]) += 1;
  }
  const int max_comp_size = *std::max_element(component_sizes.begin(), component_sizes.end());
  std::cout << "# connected components: " << num_components
            << " Max component size: " << max_comp_size
            << " (" << timer.ElapsedSeconds() << "s)" << std::endl;


  std::cout << "Finding Bi-connected Components (" << timer.ElapsedSeconds() << "s)" << std::endl;
  ogdf::EdgeArray<int> bicomponent_id(graph);
  const int num_bicomponents = ogdf::biconnectedComponents(graph, bicomponent_id);
  // Map: bicomponent_id -> set of all nodes in that bicomponent.
  std::vector<std::set<ogdf::node>> bicomponents(num_bicomponents);
  for (const ogdf::edge e : graph.edges) {
    const int id = bicomponent_id[e];
    for (const ogdf::node v : e->nodes()) {
      bicomponents.at(id).insert(v);
    }
  }
  int max_bicomp_size = -1;
  for (const auto& comp : bicomponents) {
    max_bicomp_size = std::max(max_bicomp_size, (int)comp.size());
  }
  std::cout << "# bi-connected components: " << num_bicomponents
            << " Max bi-component size: " << max_bicomp_size
            << " (" << timer.ElapsedSeconds() << "s)" << std::endl;


  std::cout << "Finding Tri-connected Components (" << timer.ElapsedSeconds() << "s)" << std::endl;
  ogdf::Triconnectivity tri_conn(graph);
  std::vector<std::set<ogdf::node>> tricomponents(tri_conn.m_numComp);
  for (int id = 0; id < tri_conn.m_numComp; ++id) {
    const ogdf::Triconnectivity::CompStruct& comp = tri_conn.m_component[id];
    if (comp.m_type == ogdf::Triconnectivity::CompType::triconnected) {
      for (const ogdf::edge e : comp.m_edges) {
        for (const ogdf::node v : e->nodes()) {
          tricomponents.at(id).insert(v);
        }
      }
    }
  }
  int num_tricomponents = 0;
  int max_tricomp_size = 0;
  for (const auto& comp : tricomponents) {
    if (!comp.empty()) {
      num_tricomponents += 1;
      max_tricomp_size = std::max(max_tricomp_size, (int)comp.size());
    }
  }
  std::cout << "# tri-connected components: " << num_tricomponents
            << " Max tri-component size: " << max_tricomp_size
            << " (" << timer.ElapsedSeconds() << "s)" << std::endl;

  std::cout << "Done (" << timer.ElapsedSeconds() << "s)" << std::endl;
  return 0;
}
