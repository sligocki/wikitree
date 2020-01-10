"""
Scan through a WikiTree API response and find people not listed
in the data dump (Private/Living people).
"""

import argparse
import json

import data_reader


parser = argparse.ArgumentParser()
parser.add_argument("dna_connections_file"
                    help="Response to an API request: api.php?action=getConnectedProfilesByDNATest&key=<person>&dna_id=<id>")
args = parser.parse_args()

db = data_reader.Database()

with open(args.dna_connections_file) as f:
  results = json.load(f)

num_people = 0
num_missing = 0
for result in results:
  for person in result["connections"]:
    num_people += 1
    user_num = int(person["Id"])
    if not db.has_person(user_num):
      num_missing += 1
      print(user_num, person["Name"])

print("Checked %d people. Missing %d (%d%%)" %
      (num_people, num_missing, 100. * num_missing / num_people))
