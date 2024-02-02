"""
Count (or list) circles.
"""

import argparse

import circles_tools
import data_reader


def try_id(db, person_num) -> str:
  id = db.num2id(person_num)
  if id:
    return id
  else:
    return str(person_num)


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("focus_id", nargs="+")
  parser.add_argument("--num-circles", "-n", type=int, default=7)
  parser.add_argument("--list", "-l", action="store_true")
  parser.add_argument("--load-connections", "--load", action="store_true")
  parser.add_argument("--version", help="Data version (defaults to most recent).")
  args = parser.parse_args()

  db = data_reader.Database(args.version)
  if args.load_connections:
    db.load_connections()

  for id in args.focus_id:
    circles = circles_tools.load_circles(db, id, args.num_circles)
    sizes = [len(circle) for circle in circles]
    print(f"{id:15s} : {sum(sizes):7d} :", sizes)

    if args.list:
      for dist in range(args.num_circles + 1):
        print("  Circle", dist)
        for i, person_num in enumerate(sorted(circles[dist])):
          done = db.connections_complete_of(person_num)
          done_str = " " if done else "X"
          print(f"   * {i:4} {done_str} {try_id(db, person_num)}")

if __name__ == "__main__":
  main()
