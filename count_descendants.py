import collections
import time

import data_reader


def count_descendants(person_num):
  parents = set()
  parents.add(person_num)
  descendants = []
  while parents:
    descendants.append(len(parents))
    children = set()
    for parent in parents:
      children.update(db.children_of(parent))
    parents = children
  return descendants


def descendants_per_ancestor(db, start_num):
  todo = collections.deque()
  todo.append((0, 1, start_num))
  best_count = 0
  while todo:
    gen, ahnentafel, person_num = todo.popleft()
    descendants = count_descendants(person_num)
    count = sum(descendants)
    if count > best_count:
      print gen, ahnentafel, db.num2id(person_num), sum(descendants), descendants
      best_count = count
    # Add parents
    father_num = db.father_of(person_num)
    if father_num:
      todo.append((gen + 1, ahnentafel * 2, father_num))
    mother_num = db.mother_of(person_num)
    if mother_num:
      todo.append((gen + 1, ahnentafel * 2 + 1, mother_num))    


import sys

db = data_reader.Database()

wt_id = sys.argv[1]
start_num = db.id2num(wt_id)
descendants_per_ancestor(db, start_num)
