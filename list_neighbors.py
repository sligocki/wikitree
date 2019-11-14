import sys

import data_reader

db = data_reader.Database()
wikitree_id = sys.argv[1]
user_num = db.id2num(wikitree_id)
print "Neighbors of:", db.name_of(user_num), wikitree_id, user_num
for neigh in db.neighbors_of(user_num):
  print db.relationship_type(user_num, neigh), db.name_of(neigh), db.num2id(neigh), neigh
