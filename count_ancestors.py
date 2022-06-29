import argparse

import data_reader


def count_ancestors(db, start_num, args):
  last_gen = [start_num]
  for gen_num in range(1, args.max_gens + 1):
    next_gen = []
    for person_num in last_gen:
      next_gen.extend(db.parents_of(person_num))
    print(f" * Gen {gen_num:3d} : {len(next_gen):7_d} / {2**gen_num:7_d} ({len(next_gen) /2**gen_num:4.0%}) Growth: {len(next_gen) / len(last_gen):4.2f}x")
    last_gen = next_gen


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("wikitree_id")
  parser.add_argument("--version", help="Data version (defaults to most recent).")
  parser.add_argument("--max-gens", type=int, default=30)
  args = parser.parse_args()

  db = data_reader.Database(args.version)
  start_num = db.id2num(args.wikitree_id)

  count_ancestors(db, start_num, args)
