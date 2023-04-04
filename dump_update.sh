#!/bin/bash
# Script for updating data dump from apps.wikitree.com

set -u
set -e

# source dump_download.sh so that we set $TIMESTAMP
source dump_download.sh
if $DOWNLOADED; then
  time bash dump_build.sh $TIMESTAMP

  echo
  echo "Update default version to $TIMESTAMP"
  rm -f data/version/default
  ln -s $TIMESTAMP data/version/default

  echo
  bash dump_cleanup.sh
fi
