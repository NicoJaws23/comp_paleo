#!/usr/bin/env bash
# dataset_report.sh
# Generate a summary report of all TSV files in a directory.
# Usage: ./dataset_report.sh <directory>
#
#Author: Nico Jaworski
#Date: 09/14/2026

# -- Argument handling --------------------------------------

if [ $# -ne 1 ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

DIRPATH="$1"

if [ ! -d "$DIRPATH" ]; then
    echo "Error: not a directory: $DIRPATH"
    exit 1
fi
echo "Dataset Report"
echo "Directory $DIRPATH"
echo "Generated $(date)"
echo "======================================================="
# -- Initialise counters and log file -----------------------

TSV_COUNT=$(ls "$DIRPATH"/*.tsv 2>/dev/null | wc -l | tr -d ' ')
LOG_FILE="small_files.log"
> "$LOG_FILE"
SMALL_FILES=0
TOTAL_ROWS=0
ALL_PASS=0
if [ "$TSV_COUNT" -eq 0 ]; then
    echo "No TSV files found in: $DIRPATH"
    exit 0
fi

echo "Found $TSV_COUNT TSV file(s) in: $DIRPATH"
echo ""

# -- Main loop: process each TSV file -----------------------
for FILEPATH in "$DIRPATH"/*.tsv; do
    FILENAME=$(basename "$FILEPATH")
    ROWS=$(tail -n +2 "$FILEPATH" | wc -l | tr -d ' ')
    TOTAL_ROWS=$((TOTAL_ROWS + ROWS))
    COLS=$(head -1 "$FILEPATH" | tr '\t' '\n' | wc -l | tr -d ' ')
    FIRSTCOLS=$(head -1 "$FILEPATH" | cut -f 1,2,3 | awk -F'\t' '{print $1" | "$2" | "$3}')
    BAD_ROWS=$(awk -F'\t' -v cols="$COLS" 'NF != cols {print NR}' "$FILEPATH" | wc -l | tr -d ' ')
    echo "File:    $FILENAME"
    echo "Rows:    $ROWS (excluding header)"
    echo "Columns: $COLS"
    echo "First 3 columns: $FIRSTCOLS"
    if [ "$BAD_ROWS" -eq 0 ]; then
        echo "Validation: PASS"
    else
        echo "Validation: FAIL"
        ALL_PASS=$((ALL_PASS + 1))
    fi
    if [ "$ROWS" -lt 100 ]; then
        echo "$FILENAME has $ROWS rows" | tee -a "$LOG_FILE"
        SMALL_FILES=$((SMALL_FILES + 1))
    fi
    echo "-------------------------------------------------------------"
done

# -- Summary ------------------------------------------------
echo "======================================================="
echo "Summary"
echo "Files processed: $TSV_COUNT"
echo "Total rows: $TOTAL_ROWS"
echo "Small files: $SMALL_FILES"
if [ "$ALL_PASS" -eq 0 ]; then
    echo "Overall result: PASS"
    exit 0
else
    echo "Overall result: FAIL"
    exit 1
fi
