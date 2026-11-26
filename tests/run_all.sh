#!/bin/sh
# Сборка + все проверки. Нужны: python3, pillow, playwright (pip install pillow playwright && playwright install chromium)
set -e
cd "$(dirname "$0")/.."
mkdir -p tests/shots
python3 booking/build.py
python3 editor/build.py
for t in tests/test_*.py; do echo "== $t"; python3 "$t" | tail -3; done
