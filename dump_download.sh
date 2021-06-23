#!/bin/bash
# Script for updating data dump from apps.wikitree.com

set -u
set -e

USERNAME=${1:-ligocki7}

PW_FILE=$(realpath data/apps.password.txt)

echo "Checking version of data dump"
# We export TIMESTAMP so that it can be used by dump_build.sh
TIMESTAMP=$( \
  echo ls -l dumps/dump_people_users.csv.gz \
  | sshpass -f "$PW_FILE" sftp ${USERNAME}@apps.wikitree.com \
  | python3 process_ls_date.py)
echo "Data dump version: $TIMESTAMP"
export TIMESTAMP

if [ -d data/dumps/$TIMESTAMP ]; then
  echo "We already have this dump"
  echo "Done"
else
  echo "We don't yet have this dump: downloading it"
  mkdir data/dumps/$TIMESTAMP
  # cd in a subshell so that we don't permanently change directories.
  (cd data/dumps/$TIMESTAMP;
   echo get dumps/*.csv.gz | sshpass -f "$PW_FILE" sftp ${USERNAME}@apps.wikitree.com)
fi
