#!/bin/bash
# Data recovery script - restore from any backup

echo "🔄 BHOOLAMIND DATA RECOVERY"
echo "=========================="

echo "Available backups:"
echo "1. Hourly backups (last 48 hours)"
echo "2. Daily backups (last 30 days)"
echo "3. Emergency backups (permanent)"
echo "4. Cloud backups"

read -p "Which backup type to restore from? (1-4): " choice

case $choice in
    1)
        echo "Hourly backups:"
        ls -la backups/hourly/
        read -p "Enter filename to restore: " filename
        if [ -f "backups/hourly/$filename" ]; then
            cp "backups/hourly/$filename" "memory/sqlite_db/bhoolamind.db"
            echo "✅ Restored from hourly backup: $filename"
        fi
        ;;
    2)
        echo "Daily backups:"
        ls -la backups/daily/
        read -p "Enter filename to restore: " filename
        if [ -f "backups/daily/$filename" ]; then
            cp "backups/daily/$filename" "memory/sqlite_db/bhoolamind.db"
            echo "✅ Restored from daily backup: $filename"
        fi
        ;;
    3)
        echo "Emergency backups:"
        ls -la backups/emergency/
        read -p "Enter filename to restore: " filename
        if [ -f "backups/emergency/$filename" ]; then
            cp "backups/emergency/$filename" "memory/sqlite_db/bhoolamind.db"
            echo "✅ Restored from emergency backup: $filename"
        fi
        ;;
    4)
        echo "Cloud backup recovery not yet implemented"
        echo "Will sync from cloud when configured"
        ;;
    *)
        echo "Invalid choice"
        ;;
esac
