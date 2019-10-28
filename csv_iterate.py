import csv

def ParseUnicode(s):
  try:
    return unicode(s, encoding="utf-8", errors="strict")
  except UnicodeDecodeError:
    print s
    raise

class UserRow(object):
  def __init__(self, row, key):
    self.row = row
    self.key = key

  def user_num(self):
    return int(self.row[self.key["User ID"]])

  def wikitree_id(self):
    return ParseUnicode(self.row[self.key["WikiTree ID"]])

  def father_num(self):
    return int(self.row[self.key["Father"]])

  def mother_num(self):
    return int(self.row[self.key["Mother"]])


def iterate_users_file(filename):
  with open(filename, "rb") as f:
    reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)

    # First, figure out the order of column names. These change
    # over time as new columns are added, so we cannot hardcode values.
    header = reader.next()
    key = {}
    for index, name in enumerate(header):
      key[name] = index

    # Now iterate through all data rows.
    for row in reader:
      yield UserRow(row, key)


def iterate_users():
  for user in iterate_users_file("dump_people_users.csv"):
    yield user
  for user in iterate_users_file("custom_user.csv"):
    yield user


if __name__ == "__main__":
  import sys
  import time

  id = sys.argv[1]
  i = 0
  for user in iterate_users():
    i += 1
    if (i % 1000000) == 0:
      print "... Read", i, "records", time.clock()
    if user.wikitree_id() == id:
      print user.wikitree_id(), user.user_num(), user.father_num(), user.mother_num()
