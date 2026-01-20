#!/bin/bash
# Emergency backup - creates immediate full backup

echo "🚨 EMERGENCY BACKUP INITIATED"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
EMERGENCY_DIR="backups/emergency"

# Backup everything
if [ -f "memory/sqlite_db/bhoolamind.db" ]; then
    cp "memory/sqlite_db/bhoolamind.db" "$EMERGENCY_DIR/EMERGENCY_${TIMESTAMP}.db"
    echo "✅ Emergency DB backup created"
fi

# Backup all config files
cp -r modules "$EMERGENCY_DIR/modules_${TIMESTAMP}/" 2>/dev/null
cp *.py "$EMERGENCY_DIR/" 2>/dev/null
cp *.md "$EMERGENCY_DIR/" 2>/dev/null
cp .env "$EMERGENCY_DIR/env_${TIMESTAMP}" 2>/dev/null

echo "✅ Emergency backup complete: $EMERGENCY_DIR"
echo "🔒 This backup is PERMANENT and should never be deleted"
