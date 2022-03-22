#!/bin/bash
# Script for updating data dump from apps.wikitree.com

set -u
set -e

# source dump_download.sh so that we set $TIMESTAMP
source dump_download.sh
if $DOWNLOADED; then
  time bash dump_build.sh $TIMESTAMP

  echo "Update default version"
  rm -f data/version/default
  ln -s $TIMESTAMP data/version/default
fi
