# Experiments with efficient graph code in C++.

# Libraries

cc_library(
  name = "clustering",
  srcs = ["clustering.cc"],
  hdrs = ["clustering.h"],
  deps = [
    ":graph",
    ":timer",
    ":util",
  ],
)

cc_library(
  name = "graph",
  srcs = ["graph.cc"],
  hdrs = ["graph.h"],
)

cc_library(
  name = "timer",
  srcs = ["timer.cc"],
  hdrs = ["timer.h"],
)

cc_library(
  name = "util",
  hdrs = ["util.h"]
)

# Binaries

cc_binary(
  name = "cluster_compare",
  srcs = ["cluster_compare.cc"],
  deps = [
    ":clustering",
    ":graph",
    ":timer",
    ":util",
  ],
)

cc_binary(
  name = "degree_distribution",
  srcs = ["degree_distribution.cc"],
  deps = [
    ":graph",
    ":timer",
    ":util",
  ],
)

cc_binary(
  name = "graph_experiment",
  srcs = ["graph_experiment.cc"],
  deps = [
    ":clustering",
    ":graph",
    ":timer",
    ":util",
  ],
)

cc_binary(
  name = "triconnectivity",
  srcs = ["triconnectivity.cc"],
  deps = [
    ":timer",
    ":util",
    "@ogdf//:all",
  ],
  copts = [
    "-Iexternal/ogdf/include/",
  ],
)
