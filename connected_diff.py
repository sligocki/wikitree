"""
Compare two dumps to see how much increase in "connected profiles" comes from
previously unconnected profiles and how much from totally new profiles.
"""

import argparse
import csv
from pathlib import Path


def load_connection_status(version, debug_limit_read=None):
  connected = set()
  unconnected = set()
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
  parser.add_argument("--debug-limit-read", type=int)
  args = parser.parse_args()
  
  old_connected, old_unconnected = load_connection_status(args.old_version, args.debug_limit_read)
  new_connected, new_unconnected = load_connection_status(args.new_version, args.debug_limit_read)
  
  con_con, con_uncon, con_added = \
    count_overlap(new_connected, old_connected, old_unconnected)
  uncon_con, uncon_uncon, uncon_added = \
    count_overlap(new_unconnected, old_connected, old_unconnected)
  print(f"""
Version {args.new_version} vs. {args.old_version}
 * Totals {len(new_connected) + len(new_unconnected):_} vs. {len(old_connected) + len(old_unconnected):_}
 * Connected: Total: {len(new_connected):_} ({len(new_connected) / (len(new_connected) + len(new_unconnected)):.1%})
   - New profiles: {len(con_added):_} ({len(con_added) / len(new_connected):.1%})
   - Previously unconnected: {len(con_uncon):_} ({len(con_uncon) / len(new_connected):.1%})
   - Previously connected: {len(con_con):_} ({len(con_con) / len(new_connected):.1%})
 * Unconnected: Total: {len(new_unconnected):_} ({len(new_unconnected) / (len(new_connected) + len(new_unconnected)):.1%})
   - New profiles: {len(uncon_added):_} ({len(uncon_added) / len(new_unconnected):.1%})
   - Previously unconnected: {len(uncon_uncon):_} ({len(uncon_uncon) / len(new_unconnected):.1%})
   - Previously connected: {len(uncon_con):_} ({len(uncon_con) / len(new_unconnected):.1%})
""")

main()
