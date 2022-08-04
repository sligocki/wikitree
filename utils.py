"""General utilities."""

import datetime
from pathlib import Path
import sys


def log(*messages):
  print(f"{datetime.datetime.now().isoformat()} ", *messages, file=sys.stderr)
  sys.stderr.flush()

def data_version_dir(version):
  """In order to allow using multiple version of data at the same time, we
  allow putting them in separate data dirs."""
  if version:
    return Path("data", "version", version)
  else:
    return Path("data", "version", "default")

class TopN:
  """Data structure which only keeps top N items."""
  def __init__(self, size):
    self.size = size
    self.items = []

  def add(self, measure, item):
    if len(self.items) < self.size or measure > self.min_val():
      self.items.append((measure, item))
      self.items.sort(key=lambda x: x[0], reverse=True)
      if len(self.items) > self.size:
        del self.items[-1]

  def min_val(self):
    if self.items:
      return self.items[-1][0]
    else:
      return 0
