// Attempt at efficient graph algorithms for giant graphs in C++.

#include <algorithm>
#include <fstream>
#include <iostream>
#include <string>

#include <ogdf/basic/Graph_d.h>
#include <ogdf/basic/extended_graph_alg.h>
#include <ogdf/basic/simple_graph_alg.h>
#include <ogdf/fileformats/GraphIO.h>
#include <ogdf/graphalg/Triconnectivity.h>

#include "timer.h"
#include "util.h"


int main(int argc, char* argv[]) {
  Timer timer;

  if (argc != 2) {
    throw std::invalid_argument("Usage: triconnectivity graph_in");
  }
  const std::string graph_filename = argv[1];

  std::cout << "Loading graph from " << graph_filename
    << " (" << timer.ElapsedSeconds() << "s)" << std::endl;
  ogdf::Graph graph;
  bool success = ogdf::GraphIO::read(graph, graph_filename, ogdf::GraphIO::read);
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
  int best_bicomp_index = -1;
  int max_bicomp_size = -1;
  for (int id = 0; id < bicomponents.size(); ++id) {
    const auto& comp = bicomponents[id];
    if ((int)comp.size() > max_bicomp_size) {
      max_bicomp_size = (int)comp.size();
      best_bicomp_index = id;
    }
  }
  std::cout << "# bi-connected components: " << num_bicomponents
            << " Max bi-component size: " << max_bicomp_size
            << " (" << timer.ElapsedSeconds() << "s)" << std::endl;

  std::cout << "Replacing graph with largest bi-component ("
            << timer.ElapsedSeconds() << "s)" << std::endl;
  ogdf::List<ogdf::node> subgraph_nodes;
  for (const ogdf::node v : bicomponents[best_bicomp_index]) {
    subgraph_nodes.pushBack(v);
  }
  ogdf::Graph big_bicomp;
  ogdf::inducedSubGraph(graph, subgraph_nodes.begin(), big_bicomp);
  std::cout << "Reduced graph to:  # Nodes: " << big_bicomp.numberOfNodes()
            << " # Edges: " << big_bicomp.numberOfEdges()
            << " (" << timer.ElapsedSeconds() << "s)" << std::endl;


  std::cout << "Finding Tri-connected Components (" << timer.ElapsedSeconds() << "s)" << std::endl;
  ogdf::Triconnectivity tri_conn(big_bicomp);
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
