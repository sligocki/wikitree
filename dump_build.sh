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
echo "(2) Convert to parquet"
# 2m
time python3 csv_to_parquet.py --version=${TIMESTAMP}

echo
echo "(3) Compute relationships"
# 6m
time python3 pq_compute_relatives.py --version=${TIMESTAMP}

echo
echo "(4) Building Graph"
# 2m
time python3 graph_make_family.py --version=${TIMESTAMP}
# 10m
time python3 graph_core.py ${VERSION_DIR}/graphs/family/all.graph.adj.nx

echo
echo "(5) Convert to SQLite DB"
# 30m
time python3 csv_to_sqlite.py --version=${TIMESTAMP}

echo
echo "(6) TODO: Compute Stats?"

echo
echo "Done"
