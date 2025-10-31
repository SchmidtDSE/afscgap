#!/bin/bash

# Check if BUCKET_NAME is set
if [ -z "$BUCKET_NAME" ]; then
    echo "Error: BUCKET_NAME environment variable is not set"
    echo "Please run: source ../../setup_env.sh"
    exit 1
fi

# Check if year argument is provided
if [ -z "$1" ]; then
    echo "Error: Year argument is required"
    echo "Usage: bash get_year.sh <year>"
    echo "Example: bash get_year.sh 2025"
    exit 1
fi

YEAR=$1

echo "-- Getting species --"
python request_source.py species $BUCKET_NAME species
[ $? -ne 0 ] && exit $?

echo "-- Getting catch --"
python request_source.py catch $BUCKET_NAME catch
[ $? -ne 0 ] && exit $?

echo "-- Getting $YEAR --"
python request_source.py haul $BUCKET_NAME haul $YEAR
[ $? -ne 0 ] && exit $?

echo "Done with getting $YEAR."
