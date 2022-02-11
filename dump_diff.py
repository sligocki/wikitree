"""
Compare two dumps to see details about how profiles were added/deleted.
"""

import argparse
import csv
import partition_tools
from pathlib import Path
import random

import api_tools


def load_all_profiles(version, debug_limit_read=None):
  all_profiles = set()
  # Use boolean in the data dump
  with open(Path("data", "version", version, "dump_people_users.csv"), "r") as f:
    csv_reader = csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
    for row in csv_reader:
      all_profiles.add(row["User ID"])
  return all_profiles

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("old_version")
  parser.add_argument("new_version")
  parser.add_argument("--sample-api", type=int, default=1000,
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
  print(f" * {len(deleted_profiles)=:_}")
  
  sample_deleted = random.sample(list(deleted_profiles), args.sample_api)
  num_redirects = 0
  for profile_num in sample_deleted:
    if api_tools.is_redirect(profile_num):
      num_redirects += 1
  print(f'Of "deleted" profiles, {num_redirects / len(sample_deleted):.0%} were actually merges')

main()
