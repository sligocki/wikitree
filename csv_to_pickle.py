import cPickle as pickle

import csv_dump

def split(d, max_size):
  split_ds = [{}]
  for key in d:
    if len(split_ds[-1]) >= max_size:
      split_ds.append({})
    split_ds[-1][key] = d[key]
  return split_ds

connections, id2num, num2id = csv_dump.load_connections()
split_connections = split(connections, 1000000)

for i, conns in enumerate(split_connections):
  print "Pickling connections", i, "of", len(split_connections), ":", time.clock()
  with open("connections_%d.pickle" % i, "wb") as f:
    pickle.dump(conns, f)

print "Pickling map id->num", time.clock()
with open("id2num.pickle", "wb") as f:
  pickle.dump(id2num, f, -1)

print "Pickling map num->id", time.clock()
with open("num2id.pickle", "wb") as f:
  pickle.dump(num2id, f, -1)
