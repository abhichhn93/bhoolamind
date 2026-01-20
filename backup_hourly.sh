#!/bin/bash
# Hourly backup - keeps learning data safe

TIMESTAMP=$(date +%Y%m%d_%H%M)
DB_PATH="memory/sqlite_db/bhoolamind.db"
BACKUP_DIR="backups/hourly"

if [ -f "$DB_PATH" ]; then
    # Create backup with timestamp
    cp "$DB_PATH" "$BACKUP_DIR/bhoolamind_${TIMESTAMP}.db"
    
    # Keep only last 48 hours (48 files)
    ls -t $BACKUP_DIR/bhoolamind_*.db | tail -n +49 | xargs rm -f 2>/dev/null
    
    echo "✅ Hourly backup: bhoolamind_${TIMESTAMP}.db"
else
    echo "❌ Database not found for hourly backup"
fi
