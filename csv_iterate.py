import csv
import datetime


def LoadMin(s):
  """Convert s to an integer defaulting to 1 if it is None or <= 0"""
  if not s:
    return 1
  num = int(s)
  return max(num, 1)


def ParseInt(int_str):
  if not int_str:
    return None
  return int(int_str)


def ParseBool(bool_str):
  if bool_str == "1":
    return True
  elif bool_str == "0":
    return False
  else:
    return None


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
    print(date_str, year, month, day)
    raise


def ParseTimestamp(timestamp_str):
  if not timestamp_str or timestamp_str == "0":
    return None
  year = int(timestamp_str[:4])
  month = int(timestamp_str[4:6])
  day = int(timestamp_str[6:8])
  hour = int(timestamp_str[8:10])
  min = int(timestamp_str[10:12])
  sec = int(timestamp_str[12:])
  try:
    return datetime.datetime(year, month, day, hour, min, sec)
  except:
    print(timestamp_str, year, month, day, hour, min, sec)
    raise


class Row:
  def __init__(self, row, key):
    self.row = row
    self.key = key

  def lookup(self, col_name):
    try:
      return self.row[self.key[col_name]]
    except (IndexError, KeyError):
      return None


class UserRow(Row):
  def user_num(self):
    return ParseInt(self.lookup("User ID"))

  def wikitree_id(self):
    return self.lookup("WikiTree ID")

  def father_num(self):
    return ParseInt(self.lookup("Father"))

  def mother_num(self):
    return ParseInt(self.lookup("Mother"))

  def birth_name(self):
    first_name = self.lookup("First Name")
    if not first_name:
      first_name = self.lookup("Preferred Name")
    if not first_name:
      first_name = "(Unlisted)"
    return first_name + " " + self.lookup("Last Name at Birth")

  def gender_code(self):
    # Note: Gender is stored as 0 = Blank, 1 = Male, 2 = Female.
    # Also possible is "" which might mean private info?
    return ParseInt(self.lookup("Gender"))

  def birth_date(self):
    return ParseDate(self.lookup("Birth Date"))

  def death_date(self):
    return ParseDate(self.lookup("Death Date"))

  def no_more_children(self):
    return ParseBool(self.lookup("No Children"))

  def registered_time(self):
    return ParseTimestamp(self.lookup("Registered"))

  def touched_time(self):
    return ParseTimestamp(self.lookup("Touched"))

  def edit_count(self):
    return ParseInt(self.lookup("Edit Count"))


def iterate_users_file(filename):
  with open(filename, "r") as f:
    reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)

    # First, figure out the order of column names. These change
    # over time as new columns are added, so we cannot hardcode values.
    header = next(reader)
    key = {}
    for index, name in enumerate(header):
      key[name] = index

    # Now iterate through all data rows.
    for row in reader:
      yield UserRow(row, key)


def iterate_users(only_custom=False):
  if not only_custom:
    for user in iterate_users_file("data/dump_people_users.csv"):
      yield user
  for user in iterate_users_file("data/custom_users.csv"):
    yield user


class MarriageRow(Row):
  def user_nums(self):
    return set([int(self.lookup("User ID1")),
                int(self.lookup("UserID2"))])

  def marriage_date(self):
    return ParseDate(self.lookup("Marriage Date"))


def iterate_marriages_file(filename):
  with open(filename, "r") as f:
    reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)

    # First, figure out the order of column names. These change
    # over time as new columns are added, so we cannot hardcode values.
    header = next(reader)
    key = {}
    for index, name in enumerate(header):
      key[name] = index

    # Now iterate through all data rows.
    for row in reader:
      yield MarriageRow(row, key)


def iterate_marriages(only_custom=False):
  if not only_custom:
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
      print("... Read", i, "records", time.process_time())
    if user.wikitree_id() == id:
      print(user.wikitree_id(), user.user_num(), user.father_num(), user.mother_num())
