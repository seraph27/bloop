#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

today=$(date +"%Y-%m-%d")
last=$(git log -1 --format="%s" 2>/dev/null || echo "")
[[ "$last" == "$today" ]] && exit 0

python3 daily.py
git add README.md
git commit -m "$today"
git push origin main
