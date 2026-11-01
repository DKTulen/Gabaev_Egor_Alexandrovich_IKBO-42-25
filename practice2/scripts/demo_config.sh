#!/usr/bin/env bash
cd "$(dirname "$0")/.." || exit 1
PYTHON="${PYTHON:-python3}"

echo "== 1. Только стартовый скрипт (VFS по умолчанию)"
"$PYTHON" src/main.py --script scripts/startup_min.emu

echo "== 2. VFS и скрипт"
"$PYTHON" src/main.py --vfs examples/vfs/multi.csv \
    --script scripts/startup_min.emu

echo "== 3. Без параметров: введите exit в окне"
"$PYTHON" src/main.py
