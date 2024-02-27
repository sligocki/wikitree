"""General utilities."""

import datetime
from pathlib import Path
import sys
from typing import Any


def log(*messages) -> None:
  print(f"{datetime.datetime.now().isoformat()} ", *messages, file=sys.stderr)
  sys.stderr.flush()

def data_version_dir(version : str) -> Path:
  """In order to allow using multiple version of data at the same time, we
  allow putting them in separate data dirs."""
  if version:
    return Path("data", "version", version)
  else:
    return Path("data", "version", "default")

class TopN:
  """Data structure which only keeps top N items."""
  def __init__(self, size : int) -> None:
    self.size = size
    self.items : list[tuple[int, Any]] = []

  def add(self, measure : int, item) -> None:
    if not self.is_full() or measure > self.min_val():
      self.items.append((measure, item))
      self.items.sort(key=lambda x: x[0], reverse=True)
      if len(self.items) > self.size:
        del self.items[-1]

  def min_val(self) -> int:
    if self.items:
      return self.items[-1][0]
    else:
      return 0

  def is_full(self) -> bool:
    return len(self.items) == self.size
