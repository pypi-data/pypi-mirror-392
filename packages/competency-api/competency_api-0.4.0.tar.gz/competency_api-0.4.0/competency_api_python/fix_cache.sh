#!/bin/bash
# Script to fix corrupted fastembed cache

echo "=== Fixing FastEmbed Cache ==="
echo

CACHE_DIR="${FASTEMBED_CACHE_PATH:-$HOME/.cache/fastembed}"
BACKUP_DIR="$CACHE_DIR.backup.$(date +%Y%m%d_%H%M%S)"

echo "Cache directory: $CACHE_DIR"
echo

if [ -d "$CACHE_DIR" ]; then
    echo "📦 Backing up existing cache to: $BACKUP_DIR"
    mv "$CACHE_DIR" "$BACKUP_DIR"
    echo "✓ Backup complete"
else
    echo "ℹ️  No existing cache found"
fi

echo
echo "🧹 Creating fresh cache directory"
mkdir -p "$CACHE_DIR"
echo "✓ Fresh cache created"

echo
echo "=== Cache Fix Complete ==="
echo
echo "Next steps:"
echo "1. Run your Python code again - it will download the model fresh"
echo "2. If it works, you can safely delete the backup:"
echo "   rm -rf $BACKUP_DIR"
echo
