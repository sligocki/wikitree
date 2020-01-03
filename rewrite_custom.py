import csv_iterate

fields = ["User ID", "WikiTree ID", "Father", "Mother", "First Name", "Middle Name", "Last Name at Birth", "Last Name Current", "Gender", "Birth Date", "Death Date"]

def get_field(user, field):
  try:
    return user.row[user.key[field]]
  except KeyError:
    return ""

print("\t".join(fields))
for user in csv_iterate.iterate_users(only_custom=True):
  print("\t".join(get_field(user, field) for field in fields))
