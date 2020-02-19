# Experiments with efficient graph code in C++.

cc_library(
  name = "map_vector_graph",
  srcs = ["map_vector_graph.cc"],
  hdrs = ["map_vector_graph.h"],
)

cc_library(
  name = "timer",
  hdrs = ["timer.h"],
)

cc_binary(
  name = "graph_experiment",
  srcs = ["graph_experiment.cc"],
  deps = [
    "map_vector_graph",
    "timer",
  ],
)
