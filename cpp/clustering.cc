#include "clustering.h"

#include <iostream>
#include <math.h>

#include "util.h"

void Clustering::LabelNode(const Graph::Node& node, const Label& label) {
  labels_[node] = label;
  clusters_need_update_ = true;
}

Clustering::Label Clustering::label(const Graph::Node& node) const {
  return labels_.at(node);
}

const std::map<Clustering::Label, std::set<Graph::Node> >& Clustering::clusters() const {
  if (clusters_need_update_) {
    // Lazy update clusters_
    clusters_.clear();
    for (const auto& [node, label] : labels_) {
      clusters_[label].insert(node);
    }
    clusters_need_update_ = false;
  }
  return clusters_;
}

int Clustering::num_nodes() const {
  return labels_.size();
}

int Clustering::num_clusters() const {
  return clusters().size();
}

double Modularity(const Graph& graph, const Clustering& clustering) {
  // Q = 1/(2m) * \sum_vw (A_vw - k_v k_w / (2m)) \delta(c_v, c_w)
  double Q = 0.0;
  const double m2 = 2.0 * graph.num_edges();
  for (const auto& [label, nodes] : clustering.clusters()) {
    // Sum of degress of all nodes in cluster.
    double sum_deg = 0.0;
    for (const Graph::Node& node : nodes) {
      // TODO: Should this sum the weighted degree instead?
      sum_deg += graph.degree(node);
      for (const auto& [neigh, weight] : graph.neighbors(node)) {
        if (nodes.find(neigh) != nodes.end()) {
          // TODO: Should this add up weights instead?
          Q += 1.0;
        }
      }
    }
    // \sum_vw k_v k_w = \sum_v [k_v (\sum_w k_w)] = \sum_v [k_v sum_deg] = sum_deg^2
    Q -= sum_deg * sum_deg / m2;
  }

  return Q / m2;
}


double Entropy(const Clustering& clustering) {
  double entropy = 0.0;
  const double num_nodes = clustering.num_nodes();
  for (const auto& [label, nodes] : clustering.clusters()) {
    // Probability of randomly picking a node in this cluster.
    const double p = nodes.size() / num_nodes;
    // H(U) = - sum P * log(P)
    entropy -= p * log2(p);
  }
  return entropy;
}

double MutualInformation(const Clustering& clustering1,
                         const Clustering& clustering2) {
  double information = 0.0;
  const double num_nodes = clustering1.num_nodes();
  if (clustering2.num_nodes() != num_nodes) {
    throw std::invalid_argument("Clusterings are not compatible.");
  }
  for (const auto& [label1, nodes1] : clustering1.clusters()) {
    const double p1 = nodes1.size() / num_nodes;

    // Collect labels from clustring2 for the nodes in this cluster1.
    Clustering sub_clustering2;
    for (const Graph::Node& node : nodes1) {
      sub_clustering2.LabelNode(node, clustering2.label(node));
    }

    // Only iterate through clusters2 that overlap this cluster1.
    for (const auto& [label2, intersection_nodes] : sub_clustering2.clusters()) {
      // Prob of choosing a node with label2 in the *entire* clustering2.
      const double p2 = clustering2.clusters().at(label2).size() / num_nodes;
      const double p12 = intersection_nodes.size() / num_nodes;
      information += p12 * log2(p12 / (p1 * p2));
    }
  }
  return information;
}

double ConditionalProbabilitySimlarity(const Clustering& clustering1,
                                       const Clustering& clustering2) {
  // P(X~Y in clustering1 & X~Y in clustering2)
  double sim12 = 0.0;
  // P(X~Y in clustering1)
  double sim1 = 0.0;
  double overlap = 0.0;
  const double num_nodes = clustering1.num_nodes();
  if (clustering2.num_nodes() != num_nodes) {
    throw std::invalid_argument("Clusterings are not compatible.");
  }
  for (const auto& [label1, nodes1] : clustering1.clusters()) {
    // P(X in cluster1)
    const double p1 = nodes1.size() / num_nodes;
    // P(X,Y in cluster1)
    sim1 += p1 * p1;

    // Collect labels from clustring2 for the nodes in this cluster1.
    Clustering sub_clustering2;
    for (const Graph::Node& node : nodes1) {
      sub_clustering2.LabelNode(node, clustering2.label(node));
    }

    // Only iterate through clusters2 that overlap this cluster1.
    int max_size = 0;
    for (const auto& [label2, intersection_nodes] : sub_clustering2.clusters()) {
      const double p12 = intersection_nodes.size() / num_nodes;
      sim12 += p12 * p12;
      max_size = std::max(max_size, (int)intersection_nodes.size());
    }
    overlap += max_size;
  }
  std::cout << "Overlap: " << (overlap / num_nodes) << std::endl
            << "Conditional probability " << sim12 / sim1 << std::endl;
  return sim12 / sim1;
}


void WriteCluster(int level, const Clustering& clustering,
                  std::ofstream* outfile) {
  *outfile << "== Clustering Level " << level << " ==" << std::endl;

  // Output one cluster per line.
  for (const auto& [cluster_name, nodes] : clustering.clusters()) {
    *outfile << "Cluster:" << cluster_name;
    for (const Graph::Node& node : nodes) {
      *outfile << " " << node;
    }
    *outfile << std::endl;
  }

  // Extra newline for visual separation.
  *outfile << std::endl;
}
