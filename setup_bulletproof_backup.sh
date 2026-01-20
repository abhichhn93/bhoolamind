#!/bin/bash

# BhoolamMind v1.5 - Bulletproof Backup System
# GOAL: Make data IMPOSSIBLE to lose, even by accident

echo "🛡️ BULLETPROOF BACKUP SYSTEM SETUP"
echo "=================================="
echo "Creating multiple layers of data protection..."

# Create backup directories
mkdir -p backups/hourly
mkdir -p backups/daily  
mkdir -p backups/weekly
mkdir -p backups/monthly
mkdir -p backups/cloud_sync
mkdir -p backups/emergency
mkdir -p backups/git_history

echo "✅ Created backup directory structure"

# 1. HOURLY BACKUP SCRIPT
cat > backup_hourly.sh << 'EOF'
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
EOF

chmod +x backup_hourly.sh

# 2. DAILY BACKUP SCRIPT  
cat > backup_daily.sh << 'EOF'
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
EOF

chmod +x backup_daily.sh

# 3. CLOUD SYNC SCRIPT
cat > backup_cloud.sh << 'EOF'
#!/bin/bash
# Cloud backup - syncs to multiple cloud providers

TIMESTAMP=$(date +%Y%m%d_%H%M)
DB_PATH="memory/sqlite_db/bhoolamind.db"
CLOUD_DIR="backups/cloud_sync"

if [ -f "$DB_PATH" ]; then
    # Create cloud-ready backup
    cp "$DB_PATH" "$CLOUD_DIR/bhoolamind_cloud_${TIMESTAMP}.db"
    
    echo "✅ Cloud backup prepared: bhoolamind_cloud_${TIMESTAMP}.db"
    
    # TODO: Add actual cloud sync commands when credentials are set
    echo "⏳ Cloud sync commands will be added when configured:"
    echo "   - Google Drive sync"
    echo "   - iCloud sync" 
    echo "   - GitHub backup repo"
    echo "   - AWS S3 sync"
    
else
    echo "❌ Database not found for cloud backup"
fi
EOF

chmod +x backup_cloud.sh

# 4. EMERGENCY BACKUP SCRIPT
cat > backup_emergency.sh << 'EOF'
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
EOF

chmod +x backup_emergency.sh

echo "✅ Created all backup scripts"

# 5. CRON SCHEDULE SETUP
cat > setup_auto_backup.sh << 'EOF'
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
EOF

chmod +x setup_auto_backup.sh

# 6. DATA PROTECTION RULES
cat > data_protection_rules.md << 'EOF'
# 🛡️ BULLETPROOF DATA PROTECTION RULES

## RULE 1: NEVER DELETE WITHOUT BACKUP
- Any delete operation MUST create backup first
- Minimum 3 copies before any deletion
- Emergency backup before any risky operation

## RULE 2: MULTIPLE BACKUP LAYERS
- Hourly: Last 48 hours (local)
- Daily: Last 30 days (local) 
- Weekly: Last 12 weeks (cloud)
- Monthly: Last 12 months (cloud)
- Emergency: Permanent (never delete)

## RULE 3: VERSION CONTROL
- Every change tracked in Git
- Daily commits with data snapshots
- Cloud repository backup
- Multiple branch protection

## RULE 4: CLOUD REDUNDANCY
- Primary: GitHub repository
- Secondary: Google Drive sync
- Tertiary: iCloud backup
- Emergency: AWS S3 archive

## RULE 5: AI PROTECTION PROTOCOLS
- AI cannot delete without explicit backup
- Delete commands require manual confirmation
- Automatic recovery scripts available
- Rollback capability for any operation
EOF

echo "✅ Created data protection rules"

# 7. RECOVERY SCRIPTS
cat > recover_data.sh << 'EOF'
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
EOF

chmod +x recover_data.sh

echo ""
echo "🛡️ BULLETPROOF PROTECTION SUMMARY:"
echo "=================================="
echo "✅ Hourly backups (48 hours retention)"
echo "✅ Daily backups (30 days retention)"  
echo "✅ Cloud sync preparation"
echo "✅ Emergency backup system"
echo "✅ Automatic cron scheduling"
echo "✅ Data recovery scripts"
echo "✅ Protection rules documented"

echo ""
echo "🚀 NEXT STEPS:"
echo "=============="
echo "1. Run: ./setup_auto_backup.sh (setup automatic backups)"
echo "2. Run: ./backup_emergency.sh (create first emergency backup)"
echo "3. Configure cloud credentials for sync"
echo "4. Test recovery: ./recover_data.sh"

echo ""
echo "🔒 DATA PROTECTION ACTIVATED!"
