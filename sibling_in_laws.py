"""https://xkcd.com/2040/"""

import argparse
import collections
import itertools
import time

import csv_to_partitions
import data_reader
import enum_kin
import partition_tools


def find_sibling_in_laws(start, sib_spos_of):
  todos = collections.deque()
  todos.append((0, start))
  visited = {start : 0}
  while todos:
    steps, person = todos.popleft()
    for neigh in sib_spos_of(person):
      if neigh not in visited:
        todos.append((steps + 1, neigh))
        visited[neigh] = steps + 1
  return visited

parser = argparse.ArgumentParser()
parser.add_argument("--no-precompute", action="store_true",
                    help="Preload all relationships into memory. "
                         "[Onetime cost: ~200s / Lookup speedup: 100x]")
parser.add_argument("--write-db", action="store_true",
                    help="Write results to a DB.")
parser.add_argument("--person",
                    help="Find all sibling-in-laws for a specific person.")
parser.add_argument("--ancestors", metavar="PERSON",
                    help="Find sibling-in-laws for all ancestors of a person.")
parser.add_argument("--all", action="store_true",
                    help="Compute all sibling-in-law partitions for entire tree.")
args = parser.parse_args()

db = data_reader.Database()

if args.no_precompute:
  def sib_spos_of(person):
    return itertools.chain(db.siblings_of(person),
                           db.spouses_of(person))
else:
  connections = data_reader.load_connections(include_parents=False,
                                             include_children=False,
                                             include_siblings=True,
                                             include_spouses=True)
  def sib_spos_of(person):
    return connections[person]

if args.person:
  start_num = db.id2num(args.person)
  sils = find_sibling_in_laws(start_num, sib_spos_of)
  print(db.name_of(start_num), "has", len(sils) - 1, "sibling-in-laws")

if args.ancestors:
  start_num = db.id2num(args.ancestors)
  visited = set()
  total = 0
  for ahn, anc in enum_kin.enum_ancestors(db, start_num):
    if anc not in visited:
      sils = find_sibling_in_laws(anc, sib_spos_of)
      visited.update(sils)
      total += len(sils)
      if len(sils) > 10:
        print(ahn, len(sils), db.name_of(anc), total, sep="\t")

if args.all:
  partitions = csv_to_partitions.get_connection_partitions(connections)

  # Summarize
  print("# Partitions:", len(partitions))
  ord_reps = [(len(partitions[rep]), rep) for rep in partitions]
  ord_reps.sort(key=lambda x: x[0], reverse=True)

  print("Largest partitions:")
  for i in range(10):
    size, rep = ord_reps[i]
    print("  %d-th largest partition: %d (rep: %s)" % (i + 1, size, db.num2id(rep)))

  print("%-iles by partitions:")
  for x in (99.999, 99.99, 99.9, 99, 90, 50):
    size, _ = ord_reps[int(len(ord_reps) * (100-x) // 100)]
    print("  %s%%-ile partition size: %d" % (x, size))

  print("%-ile by people:")
  for x in (99, 90, 75, 50, 25, 10):
    person_num = int(num_people * (100-x) // 100)
    total = 0
    i = 0
    while total < person_num:
      size, _ = ord_reps[i]
      total += size
      i += 1
    print("  %s%%-ile # sibling-in-laws: %d" % (x, size))

  if args.write_db:
    partition_db = partition_tools.PartitionDb()
    partition_db.write_partition("sibling_in_law", partitions)
