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
# TODO: Compute relationships from parquet file.

# TODO: Remove these once we give up on sqlite?
# 30m
time python3 csv_to_sqlite.py --version=${TIMESTAMP}

# 30m
# time python3 graph_make_person.py --version=${TIMESTAMP}
# time python3 graph_make_family_bipartite.py --version=${TIMESTAMP}
# time python3 graph_make_family.py --version=${TIMESTAMP}

# time python3 graph_core.py ${VERSION_DIR}/family.main.adj.nx \
#                            ${VERSION_DIR}/family.core.adj.nx \
#                            ${VERSION_DIR}/family.core.collapse.csv
# time python3 graph_core_annotate.py ${VERSION_DIR}/family.main.adj.nx \
#                                     ${VERSION_DIR}/family.core.adj.nx \
#                                     ${VERSION_DIR}/family.core.weighted.edgelist.nx.gz \
#                                     ${VERSION_DIR}/family.core.collapse.csv \
#                                     ${VERSION_DIR}/family.dist_to_core.db

# # Load connected components of graph
# # 10m
# time python3 csv_to_partitions.py --version=${TIMESTAMP}

echo "(4) TODO: Compute Stats?"

echo
echo "Done"
