"""
Compare two dumps to see details about how profiles were added/deleted.
"""

import argparse
import collections
import csv
import partition_tools
from pathlib import Path
import random

import api_tools

import pandas as pd


def load_all_profiles(version, debug_limit_read=None):
  in_path = Path("data", "version", version, "person.parquet")
  df = pd.read_parquet(in_path, columns=["wikitree_id"])
  return set(df.wikitree_id)


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("old_version")
  parser.add_argument("new_version")
  parser.add_argument("--sample-api", type=int,
                      help="Number of profiles to try looking up via API.")
  args = parser.parse_args()

  old_profiles = load_all_profiles(args.old_version)
  new_profiles = load_all_profiles(args.new_version)

  added_profiles = new_profiles - old_profiles
  deleted_profiles = old_profiles - new_profiles

  print(f"Version {args.new_version} vs. {args.old_version}")
  print(f" * {len(old_profiles)=:_}")
  print(f" * {len(new_profiles)=:_}")
  print(f" * {len(added_profiles)=:_}")
  print(f" * {len(deleted_profiles)=:_} (includes merges and moves)")

  if args.sample_api:
    sample_deleted = random.sample(list(deleted_profiles), args.sample_api)

    # Keep counter so that we keep track if multiple profiles
    # were merged into a single destination.
    redirect_dst_counts = collections.Counter()
    # Reasons that deleted profiles could not be accessed.
    non_redirect_reasons = collections.Counter()
    for profile_id in sample_deleted:
      redirect_info = api_tools.redirect_info(profile_id)
      if redirect_info.redirects_to:
        redirect_dst_counts[redirect_info.redirects_to] += 1
      else:
        non_redirect_reasons[redirect_info.status] += 1

    # If destination pre-existed, this is a merge
    num_merged = sum(cnt for dst, cnt in redirect_dst_counts.items()
                     if dst in old_profiles)
    # If destination did not pre-exist, this is a move/rename.
    num_moved = sum(cnt for dst, cnt in redirect_dst_counts.items()
                    if dst not in old_profiles)

    print()
    print('Of "deleted" profiles:')
    if len(sample_deleted) < len(deleted_profiles):
      print(f" * ~{num_moved / len(sample_deleted):.0%} were moves / renames")
      print(f" * ~{num_merged / len(sample_deleted):.0%} were merges")
      print(f" * ~{non_redirect_reasons.total() / len(sample_deleted):.0%} were not redirects (deleted / made private)")
    else:
      print(f" * {num_moved=:_}")
      print(f" * {num_merged=:_}")
      print(f" * {non_redirect_reasons.total()=:_}")
    print(" * Non-redirects:", non_redirect_reasons)


main()
