import collections
import csv
import time

# dump_people_user.csv example:
# Fields: User ID|WikiTree ID|Touched|Prefix|First Name|
#         Preferred Name|Middle Name|Last Name at Birth|Last Name Current|Last Name Other|
#         Suffix|Gender|Birth Date|Death Date|Birth Location|
#         Death Location|Father|Mother|Privacy|Is Guest|
#         Connected
# Example: 334|Gilbert-6||John|John
#         ||Gilbert|Gilbert||1
#         |17750925|18370214|Hebron, Connecticut|Mansfield, Connecticut|335
#         |347|60|0|1

def load_genetic(connections, id2num, num2id, filename="dump_people_user.csv",
                 include_siblings=True):
  """Load mappings from people->parents and ->children."""
  USER_NUM = 0
  USER_ID = 1
  FATHER_NUM = 16
  MOTHER_NUM = 17

  with open(filename, "rb") as f:
    reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)

    header = reader.next()
    print "Header:", "|".join(header)
    assert header[USER_NUM] == "User ID", header[USER_NUM]
    assert header[USER_ID] == "WikiTree ID", header[USER_ID]
    assert header[FATHER_NUM] == "Father", header[FATHER_NUM]
    assert header[MOTHER_NUM] == "Mother", header[MOTHER_NUM]

    i = 0
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
          connections[person].add(parent)
          connections[parent].add(person)
          children[parent].add(person)

      # Create connections to and from siblings (both full and half).
      if include_siblings:
        for sibling in this_sibs:
          if sibling != person:
            connections[person].add(sibling)
            connections[sibling].add(person)

      if i % 1000000 == 0:
        print " ... {:,}".format(i), \
              "{:,}".format(len(connections)), \
              time.time() - start
      i += 1
    print " ... {:,}".format(i), \
          "{:,}".format(len(connections)), \
          time.time() - start

    return id2num, num2id

def load_marriages(connections, filename="dump_people_marriages.csv"):
  """Load mappings from people->spouses."""
  with open(filename, "rb") as f:
    reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)

    header = reader.next()
    print "Header:", "|".join(header)
    assert header[0] == "User ID1", header[0]
    assert header[1] == "UserID2", header[1]

    i = 0
    start = time.time()
    print " ... {:,}".format(i), \
          "{:,}".format(len(connections)), \
          time.time() - start
    for row in reader:
      person_1, person_2 = row[0], row[1]
      connections[person_1].add(person_2)
      connections[person_2].add(person_1)
      i += 1

    print " ... {:,}".format(i), \
          "{:,}".format(len(connections)), \
          time.time() - start

def load_connections(include_siblings=True):
  connections = collections.defaultdict(set)
  id2num = {}
  num2id = {}

  print "Loading parent/child/sibling data", time.clock()
  load_genetic(connections, id2num, num2id)

  print "Loading marriages data", time.clock()
  load_marriages(connections)

  print "Loading custom data", time.clock()
  load_genetic(connections, id2num, num2id, filename="custom_user.csv",
               include_siblings=include_siblings)
  load_marriages(connections, filename="custom_marriages.csv")

  print "Loaded all connections", time.clock()
  return connections, id2num, num2id
