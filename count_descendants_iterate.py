import time

import csv_iterate


def id_to_num(wt_id):
  """Find the user_number for a given wt_id."""
  for person in csv_iterate.iterate_users():
    if person.wikitree_id() == wt_id:
      return person.user_num()
  raise Exception, "No person found with WikiTree ID: %s" % wt_id


def find_children(parents):
  """Find all children (nums) of people listed in parents (nums)."""
  children = set()
  for person in csv_iterate.iterate_users():
    if (person.father_num() in parents or
        person.mother_num() in parents):
      children.add(person.user_num())
  return children


def count_descendants(wt_id):
  parents = set()
  parents.add(id_to_num(wt_id))
  gen_num = 0
  total_descendants = 0
  while parents:
    total_descendants += len(parents)
    print gen_num, len(parents), total_descendants, time.clock()
    children = find_children(parents)
    gen_num += 1
    parents = children
  print gen_num, len(parents), total_descendants, time.clock()


import sys

wt_id = sys.argv[1]
count_descendants(wt_id)
