"""https://xkcd.com/2040/"""

import argparse
import collections
import itertools

import data_reader
import enum_kin


def find_sibling_in_laws(start):
  todos = collections.deque()
  todos.append((0, start))
  visited = {start : 0}
  while todos:
    steps, person = todos.popleft()
    #print("*", steps, db.name_of(person))
    for neigh in itertools.chain(db.siblings_of(person),
                                 db.spouses_of(person)):
      if neigh not in visited:
        todos.append((steps + 1, neigh))
        visited[neigh] = steps + 1
        if len(visited) % 10000 == 0:
          print("...", db.name_of(start), steps, len(visited))
  return visited

parser = argparse.ArgumentParser()
parser.add_argument("--person")
parser.add_argument("--ancestors")
args = parser.parse_args()

db = data_reader.Database()

if args.person:
  start_num = db.id2num(args.person)
  sils = find_sibling_in_laws(start_num)
  print(db.name_of(start_num), "has", len(sils) - 1, "sibling-in-laws")

if args.ancestors:
  start_num = db.id2num(args.ancestors)
  visited = set()
  for ahn, anc in enum_kin.enum_ancestors(db, start_num):
    if anc not in visited:
      sils = find_sibling_in_laws(anc)
      visited.update(sils)
      print(ahn, len(sils), db.name_of(anc), sep="\t")
    else:
      print(ahn, "-", db.name_of(anc), sep="\t")
