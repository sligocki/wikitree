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
time python3 csv_to_sqlite.py --version=${TIMESTAMP}
time bash process_categories.sh ${TIMESTAMP}

time python3 graph_make_family_bipartite.py --version=${TIMESTAMP}
mkdir -p ${VERSION_DIR}/communities/
for x in $(seq 0 9); do
  time python3 community_generate.py \
    ${VERSION_DIR}/fam_bipartite.main.graph \
    ${VERSION_DIR}/communities/fam_bipartite.main.comm_${x}
done
time python3 community_intersect.py \
  ${VERSION_DIR}/fam_bipartite.main.graph \
  ${VERSION_DIR}/communities/fam_bipartite.main.comm_* \
  --out-communities=${VERSION_DIR}/communities/fam_bipartite.main.inter_10
# time python3 community_analyze.py --version=${TIMESTAMP} \
#   ${VERSION_DIR}/fam_bipartite.main.graph \
#   ${VERSION_DIR}/communities/fam_bipartite.main.inter_10

# time python3 graph_make_family.py --version=${TIMESTAMP}
# time python3 graph_core.py ${VERSION_DIR}/family.main.adj.nx \
#                            ${VERSION_DIR}/family.core.adj.nx \
#                            ${VERSION_DIR}/family.core.collapse.csv
# time python3 graph_core_annotate.py ${VERSION_DIR}/family.main.adj.nx \
#                                     ${VERSION_DIR}/family.core.adj.nx \
#                                     ${VERSION_DIR}/family.core.weighted.edgelist.nx.gz \
#                                     ${VERSION_DIR}/family.core.collapse.csv \
#                                     ${VERSION_DIR}/family.dist_to_core.db

# Note: Skipping big graphs
# time python3 graph_make_person.py --version=${TIMESTAMP}

# Load connected components of graph
# time python3 csv_to_partitions.py --version=${TIMESTAMP}
# time python3 csv_to_partitions.py --version=${TIMESTAMP} --sibling-in-law

echo
echo "(3) Check categories"
time python3 category_check.py --version=${TIMESTAMP}

echo
echo "Done"
