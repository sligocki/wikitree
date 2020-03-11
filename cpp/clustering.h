#ifndef WIKITREE_CLUSTERING_H_
#define WIKITREE_CLUSTERING_H_

#include <fstream>
#include <map>
#include <set>

#include "graph.h"


class Clustering {
 public:
  using Label = Graph::Node;

  void LabelNode(const Graph::Node& node, const Label& label);

  Label label(const Graph::Node& node) const;
  const std::map<Label, std::set<Graph::Node> >& clusters() const;

  int num_nodes() const;
  int num_clusters() const;

 private:
  // Map: Node -> cluster it's in.
  std::map<Graph::Node, Label> labels_;
  // Map: cluster name -> nodes in that cluster.
  mutable std::map<Label, std::set<Graph::Node> > clusters_;
  mutable bool clusters_need_update_ = true;
};

// Measure of how good a clustering is.
// https://en.wikipedia.org/wiki/Modularity_(networks)
double Modularity(const Graph& graph, const Clustering& clustering);

// Measures of how similar two clusterings are.
// https://en.wikipedia.org/wiki/Adjusted_mutual_information
double Entropy(const Clustering& clustering);
double MutualInformation(const Clustering& clustering1,
                         const Clustering& clustering2);
// TODO: Implement:
// double AdjustedMutualInformation(const Clustering& clustering1,
//                                  const Clustering& clustering2);

// Returns P( X~Y in clustering2 | X~Y in clustering1 )
double ConditionalProbabilitySimlarity(const Clustering& clustering1,
                                       const Clustering& clustering2);

void WriteCluster(int level, const Clustering& clustering,
                  std::ofstream* outifle);

#endif  // WIKITREE_CLUSTERING_H_
