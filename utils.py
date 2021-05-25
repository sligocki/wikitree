"""General utilities."""

import datetime
import sys


def log(*messages):
  print(f"{datetime.datetime.now().isoformat()} ", *messages, file=sys.stderr)
  sys.stderr.flush()

class TopN:
  """Data structure which only keeps top N items."""
  def __init__(self, size):
    self.size = size
    self.items = []

  def add(self, measure, item):
    if len(self.items) < self.size or measure > self.items[-1][0]:
      self.items.append((measure, item))
      self.items.sort(key=lambda x: x[0], reverse=True)
      if len(self.items) > self.size:
        del self.items[-1]
