#!/bin/bash

echo "🚀 Auto-saving project..."

# Add all changes
git add .

# Commit with timestamp
git commit -m "auto update: $(date '+%Y-%m-%d %H:%M:%S')" 2>/dev/null

# Push to GitHub
git push

echo "✅ Done"
