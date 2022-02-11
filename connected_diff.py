"""
Compare two dumps to see how much increase in "connected profiles" comes from
previously unconnected profiles and how much from totally new profiles.
"""

import argparse
import csv
import partition_tools
from pathlib import Path
import random


def load_connection_status(use_dump_conn, version, debug_limit_read=None):
  connected = set()
  unconnected = set()
  if use_dump_conn:
    # Use computed network connectivity from data dump
    p_db = partition_tools.PartitionDb(version)
    main_component_rep = p_db.main_component_rep("connected")
    for row in p_db.enum_all("connected"):
      if row["rep"] == main_component_rep:
        connected.add(row["user_num"])
      else:
        unconnected.add(row["user_num"])
      if debug_limit_read and len(unconnected) + len(connected) >= debug_limit_read:
        return connected, unconnected
  else:
    # Use boolean in the data dump
    with open(Path("data", "version", version, "dump_people_users.csv"), "r") as f:
      csv_reader = csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
      for row in csv_reader:
        if row["Connected"] == "1":
          connected.add(row["User ID"])
        else:
          assert row["Connected"] == "0", row
          unconnected.add(row["User ID"])
        if debug_limit_read and len(unconnected) + len(connected) >= debug_limit_read:
          return connected, unconnected
  return connected, unconnected

def count_overlap(a, b1, b2):
  return a & b1, a & b2, a - b1 - b2

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("old_version")
  parser.add_argument("new_version")
  parser.add_argument("--use-dump-conn", action="store_true",
                      help="If true, calculate connectivity via the dump network itself. Note that since the dump does not contain any private profiles, this will show fewer profiles connected to the global tree. If false, we instead use the boolean set in the dump.")
  parser.add_argument("--debug-limit-read", type=int)
  args = parser.parse_args()
  
  old_connected, old_unconnected = load_connection_status(args.use_dump_conn, args.old_version, args.debug_limit_read)
  old_all = old_connected | old_unconnected
  new_connected, new_unconnected = load_connection_status(args.use_dump_conn, args.new_version, args.debug_limit_read)
  new_all = new_connected | new_unconnected
  
  con_con, con_uncon, con_added = \
    count_overlap(new_connected, old_connected, old_unconnected)
  uncon_con, uncon_uncon, uncon_added = \
    count_overlap(new_unconnected, old_connected, old_unconnected)

  print(f"Version {args.new_version} vs. {args.old_version}")
  print(f" * Totals {len(new_all):_} vs. {len(old_all):_}")
  print(f"   - Added: {len(new_all - old_all):_}")
  print(f"   - Deleted/Merged: {len(old_all - new_all):_}")
  print(f" * Connected: Total: {len(new_connected):_} ({len(new_connected) / (len(new_all)):.1%})")
  if new_connected:
    print(f"   - New profiles: {len(con_added):_} ({len(con_added) / len(new_connected):.1%})")
    print(f"   - Previously unconnected: {len(con_uncon):_} ({len(con_uncon) / len(new_connected):.1%})")
    print(f"   - Previously connected: {len(con_con):_} ({len(con_con) / len(new_connected):.1%})")
  print(f" * Unconnected: Total: {len(new_unconnected):_} ({len(new_unconnected) / (len(new_all)):.1%})")
  if new_unconnected:
    print(f"   - New profiles: {len(uncon_added):_} ({len(uncon_added) / len(new_unconnected):.1%})")
    print(f"   - Previously unconnected: {len(uncon_uncon):_} ({len(uncon_uncon) / len(new_unconnected):.1%})")
    print(f"   - Previously connected: {len(uncon_con):_} ({len(uncon_con) / len(new_unconnected):.1%})")

main()
