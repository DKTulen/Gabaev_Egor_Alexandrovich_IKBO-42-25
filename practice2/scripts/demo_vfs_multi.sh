#!/usr/bin/env bash
cd "$(dirname "$0")/.." || exit 1
PYTHON="${PYTHON:-python3}"

echo "== VFS: multi.csv"
"$PYTHON" src/main.py --vfs examples/vfs/multi.csv \
    --script scripts/startup_stage3.emu
