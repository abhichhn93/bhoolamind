#!/bin/bash
# Setup automatic backups via cron

CURRENT_DIR=$(pwd)

echo "Setting up automatic backup schedule..."

# Add cron jobs for automatic backups
(crontab -l 2>/dev/null; echo "# BhoolamMind Automatic Backups") | crontab -
(crontab -l 2>/dev/null; echo "0 * * * * cd $CURRENT_DIR && ./backup_hourly.sh") | crontab -
(crontab -l 2>/dev/null; echo "0 2 * * * cd $CURRENT_DIR && ./backup_daily.sh") | crontab -  
(crontab -l 2>/dev/null; echo "0 3 * * 0 cd $CURRENT_DIR && ./backup_cloud.sh") | crontab -

echo "✅ Automatic backup schedule configured:"
echo "   - Hourly backups (every hour)"
echo "   - Daily backups (2 AM every day)"  
echo "   - Cloud sync (3 AM every Sunday)"

crontab -l | grep -i bhoola
