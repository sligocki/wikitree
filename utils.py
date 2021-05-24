"""General utilities."""

import datetime
import sys


def log(*messages):
  print(f"{datetime.datetime.now().isoformat()} ", *messages, file=sys.stderr)
  sys.stderr.flush()
