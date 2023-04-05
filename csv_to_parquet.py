import argparse
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.csv
import pyarrow.parquet as pq

import utils


WIKITREE_PERSON_COLUMNS_OLD2NEW = {
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

WIKITREE_MARRIAGE_COLUMNS_OLD2NEW = {
  "User ID1": "spouse1",
  "UserID2": "spouse2",
  "Marriage Location": "marriage_location",
  "Marriage Date": "marriage_date",
  "Marriage Date Status": "marriage_date_status",
  "Marriage Location Status": "marriage_location_status",
}

WIKITREE_CATEGORIES_COLUMNS_OLD2NEW = {
  "User ID": "user_num",
  "Category": "category",
}


def rename_columns(table, column_map, assert_all_columns):
  """Rename columns from the original CSV"""

  unspecified_column_names = set(table.column_names) - column_map.keys()
  assert not unspecified_column_names, unspecified_column_names
  if assert_all_columns:
    missing_column_names = set(column_map.keys()) - set(table.column_names)
    assert not missing_column_names, missing_column_names

  new_names = [column_map[old] for old in table.column_names]

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

def load_person_csv(csv_path, is_custom):
  utils.log(f"Loading {str(csv_path)}")
  table = pa.csv.read_csv(csv_path,
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
  utils.log(f"  Loaded {table.num_rows:_} rows of people")

  table = rename_columns(table, WIKITREE_PERSON_COLUMNS_OLD2NEW,
                         assert_all_columns=(not is_custom))
  if not is_custom:
    table = parse_wikitree_dates(table, ["birth_date", "death_date"])
  # TODO: Encode as categorical: Gender, Privacy?
  utils.log(f"  Cleaned {table.num_rows:_} rows of people")

  return table

def load_marriages_csv(csv_path, is_custom):
  utils.log(f"Loading {str(csv_path)}")
  table = pa.csv.read_csv(csv_path,
    parse_options=pa.csv.ParseOptions(
      delimiter="\t", quote_char=False),
    convert_options=pa.csv.ConvertOptions(
      column_types={
        # Date fields. Load as strings and convert below.
        "Marriage Date": pa.string(),
      },
      # Nonstandard formats used in dump. Like 19991231235959
      timestamp_parsers=["%Y%m%d%H%M%S"],
    ))
  utils.log(f"  Loaded {table.num_rows:_} rows of marriages")

  table = rename_columns(table, WIKITREE_MARRIAGE_COLUMNS_OLD2NEW,
                         assert_all_columns=(not is_custom))
  if "marriage_date" in table.column_names:
    table = parse_wikitree_dates(table, ["marriage_date"])
  utils.log(f"  Cleaned {table.num_rows:_} rows of marriages")

  return table

def load_categories_csv(csv_path):
  utils.log(f"Loading {str(csv_path)}")
  table = pa.csv.read_csv(csv_path,
    parse_options=pa.csv.ParseOptions(
      delimiter="\t", quote_char=False))
  utils.log(f"  Loaded {table.num_rows:_} rows of categories")

  table = rename_columns(table, WIKITREE_CATEGORIES_COLUMNS_OLD2NEW,
                         assert_all_columns=True)
  utils.log(f"  Cleaned {table.num_rows:_} rows of categories")

  return table

def csv_to_parquet(args):
  data_dir = utils.data_version_dir(args.version)

  person_custom_table = load_person_csv(
    Path("data", "custom_users.csv"), is_custom=True)
  person_table = load_person_csv(
    Path(data_dir, "dump_people_users.csv"), is_custom=False)
  person_table = pa.concat_tables([person_table, person_custom_table], promote=True)
  # TODO: Remove duplicate rows.
  pq.write_table(person_table, Path(data_dir, "people.parquet"))
  utils.log(f"Wrote {person_table.num_rows:_} rows of people")

  marriage_custom_table = load_marriages_csv(
    Path("data", "custom_marriages.csv"), is_custom=True)
  marriages_table = load_marriages_csv(
    Path(data_dir, "dump_people_marriages.csv"), is_custom=False)
  marriages_table = pa.concat_tables([marriages_table, marriage_custom_table], promote=True)
  pq.write_table(marriages_table, Path(data_dir, "marriages.parquet"))
  utils.log(f"Wrote {marriages_table.num_rows:_} rows of marriages")

  categories_table = load_categories_csv(Path(data_dir, "dump_categories.csv"))
  pq.write_table(categories_table, Path(data_dir, "categories.parquet"))
  utils.log(f"Wrote {categories_table.num_rows:_} rows of categories")

  utils.log("Done")


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--version", help="Data version (defaults to most recent).")
  args = parser.parse_args()

  csv_to_parquet(args)

main()
