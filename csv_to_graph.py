import collections
import csv
import time

import networkx as nx

# dump_people_user.csv example:
# Fields: User ID|WikiTree ID|Prefix|First Name|Preferred Name
#        |Middle Name|Last Name at Birth|Last Name Current|Suffix|Gender
#        |Birth Date|Death Date|Birth Location|Death Location|Father
#        |Mother|Privacy|Is Guest|Connected
# Example: 334|Gilbert-6||John|John
#         ||Gilbert|Gilbert||1
#         |17750925|18370214|Hebron, Connecticut|Mansfield, Connecticut|335
#         |347|60|0|1

def load_genetic(graph, filename="dump_people_user.csv"):
  """Load mappings from people->parents and ->children."""
  USER_NUM = 0
  USER_ID = 1
  FATHER_NUM = 14
  MOTHER_NUM = 15

  with open(filename, "rb") as f:
    reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)

    header = reader.next()
    assert header[USER_NUM] == "User ID"
    assert header[USER_ID] == "WikiTree ID"
    assert header[FATHER_NUM] == "Father"
    assert header[MOTHER_NUM] == "Mother"

    i = 0
    id2num = {}
    num2id = {}
    # parents = collections.defaultdict(set)
    children = collections.defaultdict(set)
    # siblings = collections.defaultdict(set)
    start = time.time()
    for row in reader:
      person = row[USER_NUM]
      person_id = row[USER_ID]
      id2num[person_id] = person
      num2id[person] = person_id

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
        print " ... {:,}".format(i), \
              "{:,}".format(len(graph)), \
              time.time() - start
      i += 1
    print " ... {:,}".format(i), \
          "{:,}".format(len(graph)), \
          time.time() - start

    return id2num, num2id

def load_marriages(graph, filename="dump_people_marriages.csv"):
  """Load mappings from people->spouses."""
  with open(filename, "rb") as f:
    reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)

    header = reader.next()
    assert header[0] == "User ID1"
    assert header[1] == "UserID2"

    i = 0
    start = time.time()
    print " ... {:,}".format(i), \
          "{:,}".format(len(graph)), \
          time.time() - start
    for row in reader:
      person_1, person_2 = row[0], row[1]
      graph.add_edge(person_1, person_2)
      i += 1

    print " ... {:,}".format(i), \
          "{:,}".format(len(graph)), \
          time.time() - start

def build_graph():
  graph = nx.Graph()

  print "Loading parent/child/sibling data", time.clock()
  id2num, num2id = load_genetic(graph)
  # TODO: Use id2num, num2id as well.

  print "Loading marriages data", time.clock()
  load_marriages(graph)

  print "Loaded all graph", time.clock()
  return graph

if __name__ == "__main__":
  g = build_graph()

  print "Writing graph to file", time.clock()
  nx.write_adjlist(g, "graph.adj.nx")

  print "Done", time.clock()
