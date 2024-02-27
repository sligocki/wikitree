"""
Describe details about the profiles near a focus profile.
"""

import argparse
import collections
from collections.abc import Collection, Set
import itertools
from pathlib import Path
import re
from typing import Iterator

from unidecode import unidecode

import bfs_tools
import category_tools
import circles_tools
import data_reader
from data_reader import UserNum
import utils


def try_id(db, person_num : UserNum) -> str:
  id = db.num2id(person_num)
  if id:
    return id
  else:
    return str(person_num)


def get_locations(db, user_num : UserNum) -> set[str]:
  """Return set of locations referenced by user's birth and death fields."""
  locs = set()
  for attribute in ["birth_location", "death_location"]:
    loc = db.get(user_num, attribute)
    # Note: occationally loc is an int ... skip
    if loc and isinstance(loc, str):
      # Break loc up into sections so that we can count country, state, county, etc.
      # , is most common separtor, but I've see () and [] as well
      # (for Mexico specifically).
      for section in re.split(r"[,()\[\]]", loc):
        # Replace all accented chars with ASCII to standardize
        # Otherwise we end up with Mexico and México as sep locs.
        section = unidecode(section.strip())
        if section:
          locs.add(section)
  return locs


def summarize_group(db : data_reader.Database, category_db : category_tools.CategoryDb,
                    people : Collection[UserNum]) -> None:
  num_people = len(people)
  print(f"Summarizing over {num_people} people")
  counts : dict[str, collections.Counter[str]] = {
    "location": collections.Counter(),
    "category": collections.Counter(),
    "manager": collections.Counter(),
  }
  birth_years = []
  for user_num in people:
    counts["category"].update(category_db.list_categories_for_person(user_num))
    counts["location"].update(get_locations(db, user_num))
    counts["manager"][db.get(user_num, "manager_num")] += 1
    birth_date = db.birth_date_of(user_num)
    if birth_date:
      birth_years.append(birth_date.year)

  cutoffs = {
    "location": 20,
    "category": 10,
    "manager": 5,
  }
  for type in counts.keys():
    print(f"Most common {type}:")
    for (thing, count) in counts[type].most_common(cutoffs[type]):
      print(f" - {count / num_people:6.2%}  {thing}")
  birth_years.sort()
  utils.log("Birth Year Stats:")
  for i in range(5):
    percentile = i / 4.0
    by_index = round(percentile * (len(birth_years) - 1))
    print(f" - {percentile:4.0%}-ile:  {birth_years[by_index]}")

def load_locs(filename : Path) -> list[str]:
  with open(filename, "r") as f:
    return list(line.strip() for line in f)

def iter_closest_each_loc(db : data_reader.Database, focus_id : str,
                          locs : Collection[str]
                          ) -> Iterator[tuple[str, int, UserNum]]:
  focus_num = db.get_person_num(focus_id)
  remaining_locs = set(locs)
  for node in bfs_tools.ConnectionBfs(db, focus_num):
    hits = get_locations(db, node.person) & remaining_locs
    if hits:
      for loc in hits:
        yield (loc, node.dist, node.person)
      remaining_locs -= hits
      if not remaining_locs:
        return

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("focus_id")
  parser.add_argument("num_circles", nargs="?", type=int, default=7)
  parser.add_argument("--state", action="store_true")
  parser.add_argument("--version", help="Data version (defaults to most recent).")
  args = parser.parse_args()

  db = data_reader.Database(args.version)
  category_db = category_tools.CategoryDb(args.version)

  circles = circles_tools.load_circles(db, args.focus_id, args.num_circles)
  people = frozenset(itertools.chain.from_iterable(circles))
  summarize_group(db, category_db, people)

  if args.state:
    print("Finding closest person from every US State:")
    states = load_locs(Path("data/us_states.txt"))
    n = 1
    for loc, dist, id in iter_closest_each_loc(db, args.focus_id, states):
      print(f"  {n:3d} {dist:3d} {loc:20s} {id:20}")
      n += 1

main()
