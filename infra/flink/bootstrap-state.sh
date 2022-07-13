#!/bin/sh
set -eu
mkdir -p /state/checkpoints /state/savepoints
chown -R flink:flink /state
exec /docker-entrypoint.sh "$@"
