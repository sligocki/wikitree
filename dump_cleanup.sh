#!/bin/bash
# Script for deleting old dump builds to save disk space.

set -u
set -e

echo Staring Cleanup
# Save 4 most recent versions.
for x in $(ls data/version/ | egrep '^20\d\d-\d\d-\d\d$' | sort | head --lines=-4); do
  echo Removing data/version/$x
  rm -rf data/version/$x
done
echo Finished Cleanup
echo
df -h .
