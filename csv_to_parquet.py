import argparse
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.csv
import pyarrow.parquet

import utils


def rename_wikitree_columns(table):
  """Rename columns from the original CSV"""
  name_map = {
    "User ID": "user_num",
    "WikiTree ID": "wikitree_id_old",
    "WikiTree ID_DB": "wikitree_id",
    "Touched": "touched_time",
    "Registration": "registered_time",
    "Edit Count": "edit_count",

    # Names
    "Prefix": "name_prefix",
    "First Name": "name_first_birth",
    "Preferred Name": "name_first_preferred",
    "Middle Name": "name_middle",
    "Nicknames": "name_nicknames",
    "Last Name at Birth": "name_last_birth",
    "Last Name Current": "name_last_current",
    "Last Name Other": "name_last_other",
    "Suffix": "name_suffix",

    "Gender": "gender_code",
    "Birth Date": "birth_date",
    "Death Date": "death_date",
    "Birth Location": "birth_location",
    "Death Location": "death_location",
    "Father": "father_num",
    "Mother": "mother_num",
    "Photo": "image_profile",
    "No Children": "no_more_children",
    "No Siblings": "no_more_siblings",
    "Page ID": "page_id",
    "Manager": "manager_num",
    "Has Children": "has_children",
    "Is Living": "is_living",
    "Privacy": "privacy_code",
    "Background": "image_background",
    "Thank Count": "thank_count",
    "Is Locked": "is_locked",
    "Is Guest": "is_guest",
    "Connected": "is_connected",
  }

  missing_column_names = set(table.column_names) - name_map.keys()
  assert set(table.column_names) == set(name_map.keys()), (
    set(table.column_names) - set(name_map.keys()),
    set(name_map.keys()) - set(table.column_names))

  new_names = [name_map[old] for old in table.column_names]

  return table.rename_columns(new_names)

def parse_wikitree_dates(table, cols):
  """Parse WikiTree dates which may be of many formats"""
  for col in cols:
    array = table[col].combine_chunks()
    # Standardize unknown to start of month/year.
    array = pc.replace_substring_regex(
      array, r"^(....)$", r"\10101")
    array = pc.replace_substring_regex(
      array, r"00..$", "0101")
    array = pc.replace_substring_regex(
      array, r"00$", "01")
    # Cleanup non-sensical 0s.
    array = pc.replace_with_mask(
      array, pc.equal(array, "0"),
      pa.scalar(None, pa.string()))
    # Convert to timestamp.
    array = pc.strptime(array, format="%Y%m%d", unit='s',
                        error_is_null=True)
    # Convert to date.
    array = array.cast(pa.date32())
    # Update column in table.
    table = table.set_column(
      table.schema.get_field_index(col), col, array)
  return table

def load_person_csv(csv_path):
  utils.log(f"Loading {str(csv_path)}")
  person_table = pa.csv.read_csv(csv_path,
    parse_options=pa.csv.ParseOptions(
      delimiter="\t", quote_char=False),
    convert_options=pa.csv.ConvertOptions(
      column_types={
        # Booleans are stored as 0 or 1 in CSV, so must explicitly tell PyArrow to convert.
        "No Children": pa.bool_(),
        "No Siblings": pa.bool_(),
        "Has Children": pa.bool_(),
        "Is Living": pa.bool_(),
        "Is Locked": pa.bool_(),
        "Is Guest": pa.bool_(),
        "Connected": pa.bool_(),
        # Datetime fields (does not include date fields: Birth Date, Death Date).
        "Touched": pa.timestamp("s"),
        "Registration": pa.timestamp("s"),
        # Date fields. Load as strings and convert below.
        "Birth Date": pa.string(),
        "Death Date": pa.string(),
      },
      # Nonstandard formats used in dump. Like 19991231235959
      timestamp_parsers=["%Y%m%d%H%M%S"],
    ))
  utils.log(f"Loaded {person_table.num_rows:_} rows of people")

  person_table = rename_wikitree_columns(person_table)
  person_table = parse_wikitree_dates(person_table, ["birth_date", "death_date"])
  # TODO: Encode as categorical: Gender, Privacy?
  utils.log(f"Cleaned {person_table.num_rows:_} rows of people")

  return person_table

def csv_to_parquet(args):
  data_dir = utils.data_version_dir(args.version)

  person_table = load_person_csv(Path(data_dir, "dump_people_users.csv"))
  # TODO: Also load custom users.
  pa.parquet.write_table(person_table, Path(data_dir, "person.parquet"))
  utils.log(f"Wrote {person_table.num_rows:_} rows of people")

  # TODO: Load marriages
  # TODO: Compute children, siblings, co-parents.

  utils.log("Done")


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--version", help="Data version (defaults to most recent).")
  args = parser.parse_args()

  csv_to_parquet(args)

main()
