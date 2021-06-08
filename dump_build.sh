#!/bin/bash
# Script for updating data dump from apps.wikitree.com

set -u
set -e
set -x

TIMESTAMP=$1

VERSION_DIR="data/version/${TIMESTAMP}/"
rm -rf $VERSION_DIR
mkdir -p $VERSION_DIR

echo
echo "(1) Unzip"
for x in people_users people_marriages categories; do
  gunzip -c data/dumps/${TIMESTAMP}/dump_${x}.csv.gz > ${VERSION_DIR}/dump_${x}.csv
done

echo
echo "(2) Process new dump"
python3 csv_to_sqlite.py --version=${TIMESTAMP}

python3 csv_to_partitions.py --version=${TIMESTAMP}
python3 csv_to_partitions.py --version=${TIMESTAMP} --sibling-in-law

bash process_categories.sh ${TIMESTAMP}

# Note: Skipping Graph stuff for now because it's pretty intense to do each week.
# python3 sqlite_to_graph.py --version=${TIMESTAMP}

python3 nuclear_family_graph.py --version=${TIMESTAMP}
python3 graph_core.py ${VERSION_DIR}/nuclear.main.adj.nx \
                      ${VERSION_DIR}/nuclear.core.adj.nx \
                      ${VERSION_DIR}/nuclear.core.collapse.csv

echo
echo "(3) Check categories"
python3 category_check.py --version=${TIMESTAMP}

echo
echo "Done"
