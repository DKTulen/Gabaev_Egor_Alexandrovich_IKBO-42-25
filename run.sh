#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
PY="${PYTHON:-python3}"
if [ "${1:-}" = "test" ]; then
    exec "$PY" -m unittest discover -s tests -t . -v
fi
exec "$PY" src/main.py "${1:-config.yaml}"
