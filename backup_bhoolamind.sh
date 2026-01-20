#!/bin/bash
# BhoolamMind Backup Script

DATE=$(date +%Y%m%d_%H%M)
DB_PATH="memory/sqlite_db/bhoolamind.db"
BACKUP_DIR="backups"

if [ -f "$DB_PATH" ]; then
    cp "$DB_PATH" "$BACKUP_DIR/bhoolamind_${DATE}.db"
    echo "✅ Backup created: bhoolamind_${DATE}.db"
    
    # Keep only last 10 backups
    ls -t $BACKUP_DIR/bhoolamind_*.db | tail -n +11 | xargs rm -f
    echo "🧹 Cleaned old backups (keeping last 10)"
else
    echo "❌ Database not found: $DB_PATH"
fi
