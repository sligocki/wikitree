#!/bin/bash
# Script for updating data dump from apps.wikitree.com

set -u
set -e

bash dump_download.sh
bash dump_build.sh $TIMESTAMP

echo "Update default version"
rm -f data/version/default
ln -s $TIMESTAMP data/version/default
