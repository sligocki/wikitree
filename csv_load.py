import collections
import csv
import datetime
import time

class CsvLoad(object):
  def __init__(self):
    self.parents = collections.defaultdict(set)
    self.children = collections.defaultdict(set)
    self.siblings = collections.defaultdict(set)
    self.spouses = collections.defaultdict(set)

    self.death_date = {}  # Death datetime.date

    self._id2num = {}
    self._num2id = {}

  def neighbors_of(self, person):
    """Return set of all people adjacent to |person|."""
    return (self.parents[person] | self.children[person] |
            self.siblings[person] | self.spouses[person])

  def id2num(self, wikitree_id):
    return self._id2num[wikitree_id]

  def num2id(self, user_num):
    return self._num2id[user_num]

  def load_min(self, s):
    if not s:
      return 1
    num = int(s)
    return max(num, 1)

  def parse_date(self, date_str):
    year = int(date_str[:4])
    # TODO: What do we want to do with month/day not specified?
    month = self.load_min(date_str[4:6])
    day = self.load_min(date_str[6:])
    return datetime.date(year, month, day)

  def load_user(self, filename):
    """Load mappings from people->parents and ->children."""
    with open(filename, "rb") as f:
      reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)

      # First, figure out the index for various columns. These change
      # over time as new columns are added, so we cannot hardcode values.
      header = reader.next()
      print "Header:", "|".join(header)
      USER_NUM = header.index("User ID")
      WT_ID = header.index("WikiTree ID")
      FATHER_NUM = header.index("Father")
      MOTHER_NUM = header.index("Mother")
      BIRTH_DATE = header.index("Birth Date")
      DEATH_DATE = header.index("Death Date")

      i = 0
      start = time.time()
      for row in reader:
        person = row[USER_NUM]
        person_id = row[WT_ID]
        self._id2num[person_id] = person
        self._num2id[person] = person_id

        death_date = row[DEATH_DATE]
        if death_date and death_date != "0":
          self.death_date[person] = self.parse_date(death_date)

        this_sibs = set()
        # Create connections to and from parents.
        for parent in row[FATHER_NUM], row[MOTHER_NUM]:
          if parent and parent != "0":
            this_sibs.update(self.children[parent])
            self.parents[person].add(parent)
            self.children[parent].add(person)

        # Create connections to and from siblings (both full and half).
        for sibling in this_sibs:
          if sibling != person:
            self.siblings[person].add(sibling)
            self.siblings[sibling].add(person)

        if i % 1000000 == 0:
          print " ... {:,}".format(i), \
                "{:,}".format(len(self.parents)), \
                "{:,}".format(len(self.children)), \
                "{:,}".format(len(self.siblings)), \
                time.time() - start
        i += 1
      print " ... {:,}".format(i), \
            "{:,}".format(len(self.parents)), \
            "{:,}".format(len(self.children)), \
            "{:,}".format(len(self.siblings)), \
            time.time() - start

  def load_marriages(self, filename):
    """Load mappings from people->spouses."""
    with open(filename, "rb") as f:
      reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)

      header = reader.next()
      print "Header:", "|".join(header)
      assert header[0] == "User ID1", header[0]
      assert header[1] == "UserID2", header[1]

      i = 0
      start = time.time()
      for row in reader:
        person_1, person_2 = row[0], row[1]
        self.spouses[person_1].add(person_2)
        self.spouses[person_2].add(person_1)
        i += 1

      print " ... {:,}".format(i), \
            "{:,}".format(len(self.spouses)), \
            time.time() - start

  def load_all(self):
    print "Loading parent/child/sibling data", time.clock()
    self.load_user("data/dump_people_users.csv")
    print "Loading marriages data", time.clock()
    self.load_marriages("data/dump_people_marriages.csv")

    print "Loading custom data", time.clock()
    self.load_user("data/custom_users.csv")
    self.load_marriages("data/custom_marriages.csv")
    print "Loaded all connections", time.clock()
