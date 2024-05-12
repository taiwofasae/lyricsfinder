#!/bin/bash -eu
# Reset config file
> ./config.js
# Find all the LYRICSAPP_ environment variables in the environment
declare -a customVars
for key in $(env | awk -F "=" '{print $1}' | grep ".*LYRICSAPP_.*")
do
  customVars+=($key)
done
# Recreate a new config.js
for key in "${customVars[@]}"
do
  echo "window.$key='${!key}';" >> ./config.js
done