# Experiments with efficient graph code in C++.

cc_library(
  name = "chinese_whispers",
  srcs = ["chinese_whispers.cc"],
  hdrs = ["chinese_whispers.h"],
  deps = [
    "graph",
    "timer",
    "util",
  ]
)

cc_library(
  name = "hierarchy_graph",
  srcs = ["hierarchy_graph.cc"],
  hdrs = ["hierarchy_graph.h"],
  deps = [
    "graph",
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

cc_binary(
  name = "graph_experiment",
  srcs = ["graph_experiment.cc"],
  deps = [
    "chinese_whispers",
    "hierarchy_graph",
    "graph",
    "timer",
    "util",
  ],
)
