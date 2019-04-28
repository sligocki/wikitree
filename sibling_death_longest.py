from __future__ import division

import datetime

import csv_load

db = csv_load.CsvLoad()
db.load_all()

#max_diff = datetime.timedelta(0)
for later in db.siblings:
  for earlier in db.siblings[later]:
    if later in db.death_date and earlier in db.death_date:
      diff = db.death_date[later] - db.death_date[earlier]
      if diff.days > 110 * 365.24:
        print diff.days / 365.24, \
              "\t", db.num2id[earlier], "\t", db.num2id[later], \
              "\t", db.death_date[earlier], "\t", db.death_date[later]
