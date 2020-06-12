#!/bin/bash
# Script for updating data dump from apps.wikitree.com

set -u
set -e

USERNAME=${1:-ligocki7}

PW_FILE=$(realpath data/apps.password.txt)

echo "(1) Check version of data dump"
# TODO: Put password in file.
TIMESTAMP=$( \
  echo ls -l dumps/dump_people_users.csv.gz \
  | sshpass -f "$PW_FILE" sftp ${USERNAME}@apps.wikitree.com \
  | python3 process_ls_date.py)
echo "Data dump version: $TIMESTAMP"
if [ -d data/dumps/$TIMESTAMP ]; then
  echo "We already have this dump"
  echo "Done"
  exit 0
fi

echo "(2) If we don't yet have this dump, download it"
mkdir data/dumps/$TIMESTAMP
cd data/dumps/$TIMESTAMP
echo get dumps/*.csv.gz | sshpass -f "$PW_FILE" sftp ${USERNAME}@apps.wikitree.com

echo "(3) Unzip (overwriting previous CSVs)"
for x in people_users people_marriages categories; do
  gunzip dump_${x}.csv.gz -c > ../../dump_${x}.csv
done
cd ../../..  # Back to main repo

echo "(4) Process new dump"
mv data/wikitree_dump{,.bak}.db
echo csv_to_sqlite.py
python csv_to_sqlite.py

echo csv_to_groups.py
python csv_to_groups.py
echo "csv_to_groups.py --sibling-in-law"
python csv_to_groups.py --sibling-in-law

rm -f data/categories.db
echo process_categories.sh
bash process_categories.sh

echo sqlite_to_graph.py
python sqlite_to_graph.py

echo nuclear_family_graph.py
python nuclear_family_graph.py

echo graph_core.py
python graph_core.py data/nuclear.main.adj.nx data/nuclear.core.adj.nx

echo "(5) Print stats about new dump"
# TODO

echo "Done"
