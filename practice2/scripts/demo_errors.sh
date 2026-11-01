#!/usr/bin/env bash
cd "$(dirname "$0")/.." || exit 1
PYTHON="${PYTHON:-python3}"

for bad in examples/bad/*.csv no_such_file.csv; do
    echo "== VFS: $bad"
    "$PYTHON" src/main.py --vfs "$bad"
done

echo "== Скрипт не найден"
"$PYTHON" src/main.py --script no_such_script.emu
