# Experiments with efficient graph code in C++.

cc_library(
  name = "chinese_whispers",
  srcs = ["chinese_whispers.cc"],
  hdrs = ["chinese_whispers.h"],
  deps = [
    "map_vector_graph",
    "timer",
    "util",
  ]
)

cc_library(
  name = "map_vector_graph",
  srcs = ["map_vector_graph.cc"],
  hdrs = ["map_vector_graph.h"],
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

cc_binary(
  name = "graph_experiment",
  srcs = ["graph_experiment.cc"],
  deps = [
    "chinese_whispers",
    "map_vector_graph",
    "timer",
    "util",
  ],
)
