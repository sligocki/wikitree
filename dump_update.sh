#!/bin/bash
# Script for updating data dump from apps.wikitree.com

set -u
set -e

SKIP_DOWNLOAD=false
if [ "${1:-}" == "--skip-download" ]; then
  SKIP_DOWNLOAD=true
  shift
fi

if $SKIP_DOWNLOAD; then
  TIMESTAMP=$(ls -1 data/dumps/ | sort -r | head -n 1)
  echo "Skipping download. Using latest dump: $TIMESTAMP"
else
  # source dump_download.sh so that we set $TIMESTAMP
  # pass any remaining arguments to the sourced script
  source dump_download.sh "$@"
  if ! $DOWNLOADED; then
    exit 0
  fi
fi

time bash dump_build.sh $TIMESTAMP

echo
echo "Update default version to $TIMESTAMP"
rm -f data/version/default
ln -s $TIMESTAMP data/version/default

echo
bash dump_cleanup.sh
