#include "chinese_whispers.h"

#include <algorithm>
#include <chrono>
#include <iostream>
#include <random>
#include <set>

#include "timer.h"
#include "util.h"

void ClusterChineseWhispers(const Graph& graph, int iterations,
                            Clustering* clustering) {
  auto seed = std::chrono::system_clock::now().time_since_epoch().count();
  std::default_random_engine rand_engine(seed);

  // Initialize labels (each node is labeled with it's own name).
  std::vector<Graph::Node> nodes = graph.nodes();
  for (const Graph::Node& node : nodes) {
    clustering->LabelNode(node, node);
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
      std::map<Clustering::Label, double> counts;
      for (auto& [neigh, weight] : graph.neighbors(node)) {
        counts[clustering->label(neigh)] += weight;
      }

      // Find max label count
      // NOTE: In case of tie we arbitrarily choose the first one. In the
      // official algorithm, you are supposed to randomly choose one...
      // TODO: choose randomly among best labels.
      auto [best_label, max_count] = ArgMax(counts);

      // Update label to the optimal one.
      clustering->LabelNode(node, best_label);
    }
    std::cout << "  CW[" << i << "] Label re-assignment finished"
      << " (" << timer.ElapsedSeconds() << "s)" << std::endl;

    std::cout << "  CW[" << i << "] Stats:"
      << " # Clusters = " << clustering->num_clusters()
      // TODO: << " Max cluster size = " << max_size
      << " (" << timer.ElapsedSeconds() << "s)" << std::endl;
  }
}
