#!/usr/bin/env bash
#Identidy with column count

#takes datafile and returns row count and column count
# ./dataset_info.sh <filepath>


FILENAME=$(basename "$1")
ROWS=$(tail -n +2 "$1" | wc -l)
COLS=$(head -1 "$1" | tr '\t' '\n' | wc -l)
DATACOUNT=$((ROWS * COLS))

echo "===================="
echo "File:    $1"
echo "Rows:    $ROWS (exculding header)"
echo "Columns: $COLS"
echo "Datacount $DATACOUNT"
