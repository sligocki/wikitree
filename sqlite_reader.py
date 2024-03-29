from collections.abc import Container, Sequence
import datetime
from pathlib import Path
import sqlite3
from typing import Iterator

import utils


UserNum = int
WikiId = str
IdOrNum = WikiId | UserNum

class Database(object):
  def __init__(self, version : str) -> None:
    self.filename = Path(utils.data_version_dir(version), "wikitree_dump.db")
    try:
      self.conn = sqlite3.connect(self.filename)
    except sqlite3.OperationalError:
      raise sqlite3.OperationalError(f"Unable to open DB file {self.filename}")
    self.conn.row_factory = sqlite3.Row
    self.cursor = self.conn.cursor()

  def get(self, user_num : UserNum, attribute : str):
    assert isinstance(user_num, UserNum), repr(user_num)
    self.cursor.execute(f"SELECT {attribute} FROM people WHERE user_num=?", (user_num,))
    rows = self.cursor.fetchall()
    if rows:
      assert len(rows) == 1, (user_num, attribute, rows)
      return rows[0][0]

  def get_person_num(self, id_or_num : str) -> UserNum:
    try:
      return int(id_or_num)
    except ValueError:
      pass
    return self.id2num(id_or_num)

  def id2num(self, wikitree_id : WikiId) -> UserNum:
    self.cursor.execute("SELECT user_num FROM people WHERE wikitree_id=?", (wikitree_id,))
    rows = self.cursor.fetchall()
    assert len(rows) == 1, (wikitree_id, rows)
    return rows[0]["user_num"]

  def num2id(self, user_num : UserNum) -> WikiId | None:
    return self.get(user_num, "wikitree_id")

  def name_of(self, user_num : UserNum) -> str | None:
    return self.get(user_num, "birth_name")

  def birth_date_of(self, user_num : UserNum) -> datetime.date | None:
    date_str = self.get(user_num, "birth_date")
    if date_str:
      return datetime.date.fromisoformat(date_str)

  def death_date_of(self, user_num : UserNum) -> datetime.date | None:
    date_str = self.get(user_num, "death_date")
    if date_str:
      return datetime.date.fromisoformat(date_str)

  def registered_time_of(self, user_num : UserNum) -> datetime.datetime | None:
    datetime_str = self.get(user_num, "registered_time")
    if datetime_str:
      return datetime.datetime.fromisoformat(datetime_str)

  def touched_time_of(self, user_num : UserNum) -> datetime.datetime | None:
    datetime_str = self.get(user_num, "touched_time")
    if datetime_str:
      return datetime.datetime.fromisoformat(datetime_str)

  def age_at_death_of(self, user_num : UserNum) -> datetime.timedelta | None:
    birth_date = self.birth_date_of(user_num)
    death_date = self.death_date_of(user_num)
    if birth_date and death_date:
      return death_date - birth_date

  def father_of(self, user_num : UserNum) -> int | None:
    return self.get(user_num, "father_num")

  def mother_of(self, user_num : UserNum) -> int | None:
    return self.get(user_num, "mother_num")

  def parents_of(self, user_num : UserNum) -> frozenset[int]:
    return frozenset(
      p for p in (self.father_of(user_num), self.mother_of(user_num)) if p)

  def has_person(self, user_num : UserNum) -> bool:
    self.cursor.execute("SELECT 1 FROM people WHERE user_num=?", (user_num,))
    rows = self.cursor.fetchall()
    return len(rows) > 0

  def enum_people(self) -> Iterator[int]:
    cursor = self.conn.cursor()
    cursor.execute("SELECT user_num FROM people")
    while True:
      row = cursor.fetchone()
      if not row:
        return
      yield row["user_num"]

  def enum_people_no_more_children(self) -> Iterator[int]:
    cursor = self.conn.cursor()
    cursor.execute("SELECT user_num FROM people WHERE no_more_children")
    while True:
      row = cursor.fetchone()
      if not row:
        return
      yield row["user_num"]


  def neighbors_of(self, user_num : UserNum) -> frozenset[int]:
    self.cursor.execute("SELECT relative_num FROM relationships WHERE user_num=?", (user_num,))
    rows = self.cursor.fetchall()
    return frozenset(row["relative_num"] for row in rows)

  def relative_of(self, user_num : UserNum, relationship_type : str) -> frozenset[int]:
    self.cursor.execute("SELECT relative_num FROM relationships WHERE user_num = ? AND relationship_type = ?", (user_num, relationship_type))
    rows = self.cursor.fetchall()
    return frozenset(row["relative_num"] for row in rows)

  def relative_of_mult(self, user_num : UserNum, relationship_types : Container[str]) -> frozenset[int]:
    self.cursor.execute("SELECT relative_num, relationship_type FROM relationships WHERE user_num=?", (user_num,))
    rows = self.cursor.fetchall()
    return frozenset(row["relative_num"] for row in rows
                     if row["relationship_type"] in relationship_types)

  def children_of(self, parent_num : UserNum) -> frozenset[int]:
    return self.relative_of(parent_num, "child")

  def siblings_of(self, user_num : UserNum) -> frozenset[int]:
    return self.relative_of(user_num, "sibling")

  def partners_of(self, user_num : UserNum) -> frozenset[int]:
    """Return set of spouses and co-parents."""
    self.cursor.execute("SELECT relative_num FROM relationships WHERE user_num = ? AND relationship_type IN ('spouse', 'coparent')", (user_num,))
    rows = self.cursor.fetchall()
    return frozenset(row["relative_num"] for row in rows)

  def relationship_type(self, user_num : UserNum, relative_num : UserNum) -> str:
    self.cursor.execute("SELECT relationship_type FROM relationships WHERE user_num=? AND relative_num=?", (user_num, relative_num))
    rows = self.cursor.fetchall()
    assert len(rows) >= 1, (user_num, relative_num, rows)
    return rows[0]["relationship_type"]

  def enum_connections(self) -> Iterator[tuple[int, int, str]]:
    cursor = self.conn.cursor()
    cursor.execute("SELECT user_num, relative_num, relationship_type FROM relationships")
    while True:
      row = cursor.fetchone()
      if not row:
        return
      yield (row["user_num"], row["relative_num"], row["relationship_type"])

  def connections_complete_of(self, user_num : UserNum) -> bool:
    return bool(
      len(self.parents_of(user_num)) == 2 and
      self.get(user_num, "no_more_children") and
      self.get(user_num, "no_more_siblings"))
    # Ignore Spouses for now since we don't have it in data dumps.
    #        self.get(user_num, "no_more_spouses"))
