# Experiments with efficient graph code in C++.

# Libraries

cc_library(
  name = "util",
  srcs = ["timer.cc"],
  hdrs = [
    "random.h",
    "timer.h",
    "util.h",
  ],
)

cc_library(
  name = "clustering",
  srcs = ["clustering.cc"],
  hdrs = ["clustering.h"],
  deps = [
    ":graph",
    ":util",
  ],
)

cc_library(
  name = "graph",
  srcs = ["graph.cc"],
  hdrs = ["graph.h"],
)

# Binaries

cc_binary(
  name = "cluster_compare",
  srcs = ["cluster_compare.cc"],
  deps = [
    ":clustering",
    ":graph",
    ":util",
  ],
)

cc_binary(
  name = "degree_distribution",
  srcs = ["degree_distribution.cc"],
  deps = [
    ":graph",
    ":util",
  ],
)

cc_binary(
  name = "graph_experiment",
  srcs = ["graph_experiment.cc"],
  deps = [
    ":clustering",
    ":graph",
    ":util",
  ],
)

# OGDF-based stuff

cc_binary(
  name = "graph_reformat",
  srcs = ["graph_reformat.cc"],
  deps = [
    ":util",
    "@ogdf//:all",
  ],
  copts = [
    "-Iexternal/ogdf/include/",
  ],
)

cc_binary(
  name = "graph_shrink",
  srcs = ["graph_shrink.cc"],
  deps = [
    ":util",
    "@ogdf//:all",
  ],
  copts = [
    "-Iexternal/ogdf/include/",
  ],
)

cc_binary(
  name = "triconnectivity",
  srcs = ["triconnectivity.cc"],
  deps = [
    ":util",
    "@ogdf//:all",
  ],
  copts = [
    "-Iexternal/ogdf/include/",
  ],
)
