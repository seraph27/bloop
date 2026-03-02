#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

today=$(date +"%Y-%m-%d")

# Skip if already committed today
last=$(git log -1 --format="%s" 2>/dev/null || echo "")
[[ "$last" == "$today" ]] && exit 0

echo "$today" >> log
git add log
git commit -m "$today"
git push origin main
