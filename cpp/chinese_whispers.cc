#include "chinese_whispers.h"

#include <algorithm>
#include <chrono>
#include <iostream>
#include <random>

#include "timer.h"
#include "util.h"

void ClusterChineseWhispers(const Graph& graph,
                            int iterations,
                            std::map<Graph::Node, CWLabel>* labels) {
  auto seed = std::chrono::system_clock::now().time_since_epoch().count();
  std::default_random_engine rand_engine(seed);

  // Initialize labels
  std::vector<int> nodes = graph.nodes();
  for (Graph::Node node : nodes) {
    (*labels)[node] = node;
  }

  // Run algorithm # iterations.
  for (int i = 0; i < iterations; ++i) {
    Timer timer;

    // Randomize order of nodes.
    std::shuffle(nodes.begin(), nodes.end(), rand_engine);
    std::cout << "  CW[" << i << "] Shuffle finished"
      << " (" << timer.ElapsedSeconds() << "s)" << std::endl;

    // Greedily optimize the label of all nodes.
    for (Graph::Node node : nodes) {
      // Count # of neighbors with each label.
      std::map<CWLabel, double> counts;
      for (auto& [neigh, weight] : graph.neighbors(node)) {
        counts[(*labels)[neigh]] += weight;
      }

      // Find max label count
      // NOTE: In case of tie we arbitrarily choose the first one. In the
      // official algorithm, you are supposed to randomly choose one...
      auto [best_label, max_count] = ArgMax(counts);

      // Update label to the optimal one.
      (*labels)[node] = best_label;
    }
    std::cout << "  CW[" << i << "] Label re-assignment finished"
      << " (" << timer.ElapsedSeconds() << "s)" << std::endl;

    std::map<CWLabel, int> cluster_sizes;
    for (const auto& [node, label] : *labels) {
      cluster_sizes[label] += 1;
    }
    auto [max_label, max_size] = ArgMax(cluster_sizes);
    std::cout << "  CW[" << i << "] Stats:"
      << " # Clusters = " << cluster_sizes.size()
      << " Max cluster size = " << max_size
      << " (" << timer.ElapsedSeconds() << "s)" << std::endl;
  }
}


void WriteCluster(
    int level,
    const std::map<Graph::Node, CWLabel> labels,
    std::ofstream* outfile) {
  *outfile << "== Clustering Level " << level << " ==" << std::endl;
  // Collect all clusters.
  std::map<CWLabel, std::vector<Graph::Node> > clusters;
  for (const auto& [node, label] : labels) {
    clusters[label].push_back(node);
  }

  // Output one cluster per line.
  for (const auto& [cluster_name, nodes] : clusters) {
    *outfile << "Cluster:" << cluster_name;
    for (const Graph::Node& node : nodes) {
      *outfile << " " << node;
    }
    *outfile << std::endl;
  }

  // Extra newline for visual separation.
  *outfile << std::endl;
}
