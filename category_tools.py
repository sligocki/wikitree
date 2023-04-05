from pathlib import Path

import pandas as pd

import utils


class CategoryDb:
  def __init__(self, version):
    self.filename = Path(utils.data_version_dir(version), "categories.parquet")
    self.data = pd.read_parquet(self.filename)

  def list_categories_for_person(self, user_num):
    return frozenset(self.data.loc[self.data.user_num == user_num, "category"])

  def list_people_in_category(self, category_name):
    return frozenset(self.data.loc[self.data.category == category_name, "user_num"])
