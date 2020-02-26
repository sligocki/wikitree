import collections
import time

import data_reader


def print_hist(hist, total):
  cumm = 0.0
  mean = 0.0
  for i in range(max(hist.keys()) + 1):
    # Skip empty buckets.
    if hist[i]:
      frac = hist[i] / total
      cumm += frac
      print("%5d : %10d (%7.4f%% / Cumm: %7.4f%%)"
            % (i, hist[i], 100. * frac, 100. * cumm))
      mean += i * frac
  print("Mean: %.2f" % mean)


db = data_reader.Database()

# Histogram of counts for # children/grandchildren of all people in tree.
num_people = 0
hist_num_children = collections.defaultdict(int)
hist_num_grandchildren = collections.defaultdict(int)
max_num_grandchildren = 0
for person in db.enum_people():
  children = db.children_of(person)
  grandchildren = set()
  for child in children:
    grandchildren.update(db.children_of(child))
  num_people += 1
  hist_num_children[len(children)] += 1
  num_grandchildren = len(grandchildren)
  hist_num_grandchildren[num_grandchildren] += 1
  if num_grandchildren > max_num_grandchildren:
    max_num_grandchildren = num_grandchildren
    print(" *** New max:", num_grandchildren, db.num2id(person), db.name_of(person))
  elif num_grandchildren > 120:
    print(" ---------- :", num_grandchildren, db.num2id(person), db.name_of(person))

  if num_people % 1000000 == 0:
    print(" ... ", num_people, time.process_time())
  #   print("Histogram of number of children:")
  #   print_hist(hist_num_children, num_people)
  #   print()
  #   print("Histogram of number of grand-children:")
  #   print_hist(hist_num_grandchildren, num_people)

print("Histogram of number of children:")
print_hist(hist_num_children, num_people)
print()
print("Histogram of number of grand-children:")
print_hist(hist_num_grandchildren, num_people)
