import argparse
from pathlib import Path

import pyarrow
import pyarrow.compute as pc
import pyarrow.csv
import pyarrow.parquet

import utils


def ParseDates(table, cols):
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
      pyarrow.scalar(None, pyarrow.string()))
    # Convert to timestamp.
    array = pc.strptime(array, format="%Y%m%d", unit='s',
                        error_is_null=True)
    # Convert to date.
    array = array.cast(pyarrow.date32())
    # Update column in table.
    table = table.set_column(
      table.schema.get_field_index(col), col, array)
  return table

def csv_to_parquet(args):
  data_dir = utils.data_version_dir(args.version)

  # TODO: Also load custom users.
  utils.log("Loading person CSV")
  person_table = pyarrow.csv.read_csv(
    Path(data_dir, "dump_people_users.csv"),
    parse_options=pyarrow.csv.ParseOptions(
      delimiter="\t", quote_char=False),
    convert_options=pyarrow.csv.ConvertOptions(
      column_types={
        # Booleans are stored as 0 or 1 in CSV, so must explicitly tell PyArrow to convert.
        "No Children": pyarrow.bool_(),
        "No Siblings": pyarrow.bool_(),
        "Has Children": pyarrow.bool_(),
        "Is Living": pyarrow.bool_(),
        "Is Locked": pyarrow.bool_(),
        "Is Guest": pyarrow.bool_(),
        "Connected": pyarrow.bool_(),
        # Datetime fields (does not include date fields: Birth Date, Death Date).
        "Touched": pyarrow.timestamp("s"),
        "Registration": pyarrow.timestamp("s"),
        # Date fields. Load as strings and convert below.
        "Birth Date": pyarrow.string(),
        "Death Date": pyarrow.string(),
      },
      # Nonstandard formats used in dump. Like 19991231235959
      timestamp_parsers=["%Y%m%d%H%M%S"],
    ))
  utils.log(f"Loaded {person_table.num_rows} people")

  utils.log("Cleaning Data")
  person_table = ParseDates(person_table, ["Birth Date", "Death Date"])

  # TODO: Encode as categorical: Gender, Privacy

  utils.log(person_table.schema)
  utils.log("Writing person parquet")
  pyarrow.parquet.write_table(person_table, Path(data_dir, "person.parquet"))
  utils.log(f"Wrote {person_table.num_rows} rows")

  # TODO: Load marriages
  # TODO: Compute children, siblings, co-parents.

  utils.log("Done")


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--version", help="Data version (defaults to most recent).")
  args = parser.parse_args()

  csv_to_parquet(args)

main()
