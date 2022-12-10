#!/bin/bash
set -e

# Restore the database if it does not already exist.
if [ -f "${DB_FILE}" ]; then
	echo "Database already exists, skipping restore"
else
	echo "No database found, restoring from replica if exists"
	litestream restore -v -if-replica-exists -o "${DB_FILE}" "${REPLICA_URL}"
fi
# Run datasette
datasette serve \
    --host 0.0.0.0 \
    --port "${DS_PORT}" \
    --immutable "${DB_FILE}" \
    --metadata "${METADATA_PATH}" \
    --setting sql_time_limit_ms 20000 \
    --setting allow_download off \
    --cors
