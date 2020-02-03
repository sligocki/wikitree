"""
Convert date from call to ls to standardized form.
"""

import datetime
import sys

month_name2num = {
  "Jan" : 1,
  "Feb" : 2,
  "Mar" : 3,
  "Apr" : 4,
  "May" : 5,
  "Jun" : 6,
  "Jul" : 7,
  "Aug" : 8,
  "Sep" : 9,
  "Oct" : 10,
  "Nov" : 11,
  "Dec" : 12,
}

text = sys.stdin.read()
fields = text.split()
# Expected format:
#   -rw-r--r--    ? 517      517      995891602 Jan 26 14:21 foo.txt
# or
#   -rw-r--r--  1 sl929  wheel  0 Dec 13  1985 /tmp/foo
month_str, day_str, year_or_time_str = fields[-4:-1]
day = int(day_str)
month_num = month_name2num[month_str]

if ":" in year_or_time_str:
  # Year is implicit -> It's within the last 12 months.
  today = datetime.date.today()
  if month_num <= today.month:
    # It's this calendar year.
    year = today.year
  else:
    # It's last calendar year.
    year = today.year - 1
else:
  # Year is explicitly in ls output.
  year = int(year_or_time_str)

file_date = datetime.date(year, month_num, day)
print(file_date.isoformat())
