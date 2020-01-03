import csv_iterate

fields = ["User ID", "WikiTree ID", "Father", "Mother", "First Name", "Middle Name", "Last Name at Birth", "Last Name Current", "Gender"]

print "\t".join(fields)
for user in csv_iterate.iterate_users(only_custom=True):
  print "\t".join(user.row[user.key[field]] for field in fields)
