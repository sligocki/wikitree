import time

import sqlite_reader


def count_descendants(wt_id):
  db = sqlite_reader.Database()
  parents = set()
  parents.add(db.id2num(wt_id))
  gen_num = 0
  total_descendants = 0
  while parents:
    total_descendants += len(parents)
    print gen_num, len(parents), total_descendants, time.clock()
    children = set()
    for parent in parents:
      children.update(db.children_of(parent))
    gen_num += 1
    parents = children
  print gen_num, len(parents), total_descendants, time.clock()


import sys

wt_id = sys.argv[1]
count_descendants(wt_id)
