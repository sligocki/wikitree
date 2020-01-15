# Script for updating data dump from apps.wikitree.com

set -u
set -e

USERNAME=${1:-ligocki7}

PW_FILE=$(realpath data/apps.password.txt)

# 1) Check version of data dump.
# TODO: Put password in file.
echo ls -l dumps/dump_people_users.csv.gz | sshpass -f "$PW_FILE" sftp ${USERNAME}@apps.wikitree.com

# 2) Figure out timestamp from ls.
# TODO: Auto-extract timestamp from ls format.
echo "Input timestamp now: [^C to cancel]"
read TIMESTAMP
echo "You entered [$TIMESTAMP]"

if [ -d data/dumps/$TIMESTAMP ]; then
  echo "We already have this dump"
  echo "Done"
  exit 0
fi

# 3) If we don't yet have this dump, download it.
mkdir data/dumps/$TIMESTAMP
cd data/dumps/$TIMESTAMP
echo get dumps/* | sshpass -f "$PW_FILE" sftp ${USERNAME}@apps.wikitree.com

# 4) Unzip (overwriting previous CSVs)
for x in users marriages; do
  gunzip dump_people_${x}.csv.gz -c > ../../dump_people_${x}.csv
done

# 5) Process new dump
cd ../../..  # Back to main repo
rm -f data/wikitree_dump.db
python csv_to_sqlite.py
python csv_to_graph.py
python csv_to_groups.py
# TODO: Update sibling-in-laws

# 6) Print stats about new dump
# TODO
