import argparse
import datetime
import webbrowser

import category_tools
import csv_iterate
import data_reader


def is_residence(location, places):
  for name in places:
    if name.lower() in location.lower():
      return True
  return False


def category_check(version, args, *, target_places, category_name=None):
  db = data_reader.Database(version)
  category_db = category_tools.CategoryDb(version)

  residents = set()
  for user in csv_iterate.iterate_users(version=version):
    for place in (user.birth_location(), user.death_location()):
      if place and is_residence(place, target_places):
        residents.add(user.user_num())
  for marriage in csv_iterate.iterate_marriages(version=version):
    if marriage.marriage_location() and \
       is_residence(marriage.marriage_location(), target_places):
      for user_num in marriage.user_nums():
        residents.add(user_num)
  print(f"# Residents = {len(residents):_}")
  editable_residents = {
    user_num for user_num in residents
    if db.get(user_num, "privacy_level") >= 60
    and (not db.birth_date_of(user_num)
         or db.birth_date_of(user_num) >= datetime.date(1500, 1, 1))}
  print(f"# Editable residents = {len(editable_residents):_}")

  if category_name:
    in_category = category_db.list_people_in_category(category_name)
    print(f"# in category = {len(in_category):_}")

    cat_not_resident = in_category - residents
    print(f"# in category, not resident = {len(cat_not_resident):_}")

    residents_not_in_cat = residents - in_category
    print(f"# Residents not in category = {len(residents_not_in_cat):_}")

    # Only list editable residents. Can't fix the private ones.
    editable_residents_not_in_cat = editable_residents - in_category
    print(f"# Editable residents not in category = {len(editable_residents_not_in_cat):_}")
    for person in sorted(editable_residents_not_in_cat):
      url = f"https://www.wikitree.com/wiki/{db.num2id(person)}"
      print(" *", url)
      if args.open_links:
        webbrowser.open(url)


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--version", help="Data version (defaults to most recent).")

  parser.add_argument("--open-links", action="store_true")

  parser.add_argument("--no-shapinsay", dest="shapinsay", action="store_false")
  parser.add_argument("--no-inowroclaw", dest="inowroclaw", action="store_false")
  parser.add_argument("--no-kalmar", dest="kalmar", action="store_false")
  parser.add_argument("--no-honhardt", dest="honhardt", action="store_false")
  args = parser.parse_args()

  if args.shapinsay:
    print("Shapinsay parish, Orkney, Scotland (pop 1,000)")
    category_check(
      args.version, args,
      category_name="Shapinsay_Parish,_Orkney",
      target_places=["Shapinsay"])
    print()

  if args.inowroclaw:
    print("Inowrocław county, Poland (pop 70,000)")
    category_check(
      args.version, args,
      category_name="Inowrocław_County,_Kuyavian-Pomeranian_Voivodeship,_Poland",
      target_places=[
        # Inowrocław in various Polish and German spellings
        "Inowrocław", "Inowroclaw", "Inowrazlaw", "Hohensalza", "Jungleslau",
        # Gminas in Inowrocław county
        "Kruszwica", "Kruschwitz",
        "Gniewkowo", # "Argenau", TODO: matches Margenau
        "Janikowo", # "Amsee", TODO: matches Zallamsee
        "Pakość", "Pakosc", "Pakosch",
        "Złotniki Kujawskie", "Güldenhof", "Guldenhof",
        "Dąbrowa Biskupia", "Luisenfelde",
        # "Rojewo", TODO: matches Dobrojewo #"Roneck", TODO: matches Mamaroneck
        # Towns in Strelno, Posen that are now in Inowrocław county
        "Ludzisko", "Ludzisk",
        "Polanowitz",  # Removed "Polanowice" (there are several: https://pl.wikipedia.org/wiki/Polanowice)
        # Removed "Piaski" because there's Piaski, Warsaw too :/
        # Specific towns in Inowrocław
        "Płonkowo", "Plonkowo", "Tuczno",
      ])
    print()

  if args.kalmar:
    print("Kalmar county, Sweden (pop 240,000)")
    category_check(
      args.version, args,
      # TODO: We really want all subcategories of this ...
      # category_name="Kalmar_County",
      target_places=["Kalmar"])
    print()

  if args.honhardt:
    print("Honhardt parish, Württemberg, Germany (pop 5,000)")
    category_check(
      args.version, args,
      # TODO: category_name="Honhardt,_Württemberg",
      target_places=[
        "Honhardt",
        # Honhardt is now part of the town Frankenhardt
        "Frankenhardt",
        # Location within Honhardt
        "Hirschhof",
      ])
    print()

main()
