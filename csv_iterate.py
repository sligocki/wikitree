import csv
import datetime

def ParseUnicode(s):
  try:
    return unicode(s, encoding="utf-8", errors="strict")
  except UnicodeDecodeError:
    print s
    raise

def LoadMin(s):
  """Convert s to an integer defaulting to 1 if it is None or <= 0"""
  if not s:
    return 1
  num = int(s)
  return max(num, 1)

def ParseDate(date_str):
  if not date_str or date_str == "0":
    return None
  year = int(date_str[:4])
  # TODO: What do we want to do with month/day not specified?
  month = LoadMin(date_str[4:6])
  day = LoadMin(date_str[6:])
  try:
    return datetime.date(year, month, day)
  except:
    print date_str, year, month, day
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

  def birth_name(self):
    first_name = self.row[self.key["First Name"]]
    if not first_name:
      first_name = self.row[self.key["Preferred Name"]]
    if not first_name:
      first_name = "(Unlisted)"
    return ParseUnicode(first_name) + " " + ParseUnicode(self.row[self.key["Last Name at Birth"]])

  def birth_date(self):
    return ParseDate(self.row[self.key["Birth Date"]])

  def death_date(self):
    return ParseDate(self.row[self.key["Death Date"]])


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
  for user in iterate_users_file("data/dump_people_users.csv"):
    yield user
  for user in iterate_users_file("data/custom_users.csv"):
    yield user


class MarriageRow(object):
  def __init__(self, row, key):
    self.row = row
    self.key = key

  def user_nums(self):
    return set([int(self.row[self.key["User ID1"]]),
                int(self.row[self.key["UserID2"]])])

  def marriage_date(self):
    return ParseDate(self.row[self.key["Marriage Date"]])


def iterate_marriages_file(filename):
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
      yield MarriageRow(row, key)


def iterate_marriages():
  for marriage in iterate_marriages_file("data/dump_people_marriages.csv"):
    yield marriage
  for marriage in iterate_marriages_file("data/custom_marriages.csv"):
    yield marriage


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
