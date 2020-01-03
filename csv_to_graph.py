import collections
import csv
import time

import networkx as nx

def load_genetic(graph, filename="dump_people_users.csv"):
  """Load mappings from people->parents and ->children."""
  with open(filename, "rb") as f:
    reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)

    header = next(reader)
    USER_NUM = header.index("User ID")
    WT_ID = header.index("WikiTree ID")
    FATHER_NUM = header.index("Father")
    MOTHER_NUM = header.index("Mother")

    i = 0
    # parents = collections.defaultdict(set)
    children = collections.defaultdict(set)
    # siblings = collections.defaultdict(set)
    start = time.time()
    for row in reader:
      person = row[USER_NUM]

      this_sibs = set()
      # Create connections to and from parents.
      for parent in row[FATHER_NUM], row[MOTHER_NUM]:
        if parent and parent != "0":
          this_sibs.update(children[parent])
          graph.add_edge(person, parent)
          # Keep track of children separately so that siblings can be computed.
          children[parent].add(person)

      # Create connections to and from siblings (both full and half).
      for sibling in this_sibs:
        if sibling != person:
          graph.add_edge(person, sibling)

      if i % 1000000 == 0:
        print(" ... {:,}".format(i), \
              "{:,}".format(len(graph)), \
              time.time() - start)
      i += 1
    print(" ... {:,}".format(i), \
          "{:,}".format(len(graph)), \
          time.time() - start)

def load_marriages(graph, filename="dump_people_marriages.csv"):
  """Load mappings from people->spouses."""
  with open(filename, "rb") as f:
    reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)

    header = next(reader)
    assert header[0] == "User ID1"
    assert header[1] == "UserID2"

    i = 0
    start = time.time()
    print(" ... {:,}".format(i), \
          "{:,}".format(len(graph)), \
          time.time() - start)
    for row in reader:
      person_1, person_2 = row[0], row[1]
      graph.add_edge(person_1, person_2)
      i += 1

    print(" ... {:,}".format(i), \
          "{:,}".format(len(graph)), \
          time.time() - start)

def build_graph():
  graph = nx.Graph()

  print("Loading parent/child/sibling data", time.process_time())
  load_genetic(graph)

  print("Loading marriages data", time.process_time())
  load_marriages(graph)

  print("Loaded all graph", time.process_time())
  return graph

if __name__ == "__main__":
  g = build_graph()

  print("Writing graph to file", time.process_time())
  nx.write_adjlist(g, "graph.adj.nx")

  print("Done", time.process_time())
