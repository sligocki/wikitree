import argparse
import datetime

import category_tools
import csv_iterate
import data_reader


def is_residence(location, places):
  for name in places:
    if name in location:
      return True
  return False


def category_check(category_name, target_places):
  db = data_reader.Database()

  residents = set()
  for user in csv_iterate.iterate_users():
    for place in (user.birth_location(), user.death_location()):
      if place and is_residence(place, target_places):
        residents.add(user.user_num())
  for marriage in csv_iterate.iterate_marriages():
    if marriage.marriage_location() and \
       is_residence(marriage.marriage_location(), target_places):
      for user_num in marriage.user_nums():
        residents.add(user_num)
  print(f"# Residents = {len(residents)}")
  editable_residents = {
    user_num for user_num in residents
    if db.get(user_num, "privacy_level") >= 60
    and (not db.birth_date_of(user_num)
         or db.birth_date_of(user_num) >= datetime.date(1500, 1, 1))}
  print(f"# Editable residents = {len(editable_residents)}")

  in_category = category_tools.list_category(category_name)
  print(f"# in category = {len(in_category)}")

  cat_not_resident = in_category - residents
  print(f"# in category, not resident = {len(cat_not_resident)}")

  residents_not_in_cat = residents - in_category
  print(f"# Residents not in category = {len(residents_not_in_cat)}")

  # Only list editable residents. Can't fix the private ones.
  editable_residents_not_in_cat = editable_residents - in_category
  print(f"# Editable residents not in category = {len(editable_residents_not_in_cat)}")
  for person in sorted(editable_residents_not_in_cat):
    print(f" * https://www.wikitree.com/wiki/{db.num2id(person)}")


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--no-shapinsay", dest="shapinsay", action="store_false")
  parser.add_argument("--no-inowroclaw", dest="inowroclaw", action="store_false")
  args = parser.parse_args()

  if args.shapinsay:
    print("Shapinsay")
    category_check(
      category_name="Shapinsay_Parish,_Orkney",
      target_places=("Shapinsay",))
    print()

  if args.inowroclaw:
    print("Inowrocław county")
    category_check(
      category_name="Inowrocław_County,_Kuyavian-Pomeranian_Voivodeship,_Poland",
      target_places=(
        # Inowrocław in Polish and German spelling.
        "Inowrocław", "Inowroclaw", "Inowrazlaw", "Hohensalza", "Jungleslau",
        # Towns in Strelno, Posen that are now in Inowrocław county.
        "Ludzisk", "Polanowitz",
        # Removed "Piaski" because there's Piaski, Warsaw too :/
        # Specific towns in Inowrocław.
        "Płonkowo", "Plonkowo", "Pakość", "Pakosc", "Tuczno",
      ))
    print()

main()
