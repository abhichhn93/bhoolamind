#!/bin/bash
# Daily backup - keeps 30 days of history

TIMESTAMP=$(date +%Y%m%d)
DB_PATH="memory/sqlite_db/bhoolamind.db"
BACKUP_DIR="backups/daily"

if [ -f "$DB_PATH" ]; then
    # Create daily backup
    cp "$DB_PATH" "$BACKUP_DIR/bhoolamind_daily_${TIMESTAMP}.db"
    
    # Keep only last 30 days
    ls -t $BACKUP_DIR/bhoolamind_daily_*.db | tail -n +31 | xargs rm -f 2>/dev/null
    
    echo "✅ Daily backup: bhoolamind_daily_${TIMESTAMP}.db"
    
    # Also create git backup
    git add -A
    git commit -m "Daily backup: $(date)" 2>/dev/null || echo "Git commit skipped"
    
else
    echo "❌ Database not found for daily backup"
fi
