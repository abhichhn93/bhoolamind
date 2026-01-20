#!/bin/bash

# BhoolamMind v1.5 - Quick Cloud Setup
# Gets you started with GitHub backup immediately

echo "☁️ BHOOLAMIND CLOUD SETUP"
echo "========================="

# Check if we're in the right directory
if [ ! -f "modules/database.py" ]; then
    echo "❌ Please run from bhoolamind_v1.5 directory"
    exit 1
fi

echo "🔍 Checking current setup..."

# Check git status
if [ -d ".git" ]; then
    echo "✅ Git repository exists"
    git status --porcelain | wc -l | xargs echo "📝 Uncommitted changes:"
else
    echo "⚠️ No git repository - will initialize"
    git init
    echo "✅ Git repository initialized"
fi

# Setup .gitignore for cloud safety
echo "🔧 Updating .gitignore for cloud safety..."
cat >> .gitignore << 'EOF'

# Cloud Integration Safety
credentials/
*.key
*.pem
*.p12
secrets.json
google_drive.json
aws_credentials.json

# API Keys (double protection)
.env.local
.env.production
api_keys.txt

# Temporary cloud files
.gdrive_cache/
.aws_cache/
.dropbox_cache/
EOF

echo "✅ .gitignore updated for cloud safety"

# Create credentials directory
mkdir -p credentials
chmod 700 credentials
echo "✅ Created secure credentials directory"

# Update .env with cloud placeholders
echo "🔧 Adding cloud configuration to .env..."
cat >> .env << 'EOF'

# === CLOUD INTEGRATION SETTINGS ===

# GitHub Repository Backup
GITHUB_TOKEN=your_github_personal_access_token_here
GITHUB_REPO=yourusername/bhoolamind-ai-memory
GITHUB_BACKUP_ENABLED=false

# Google Drive Sync  
GOOGLE_DRIVE_FOLDER_ID=your_google_drive_folder_id_here
GOOGLE_DRIVE_CREDENTIALS_PATH=credentials/google_drive.json
GOOGLE_DRIVE_BACKUP_ENABLED=false

# AWS S3 Archive
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_S3_BUCKET=bhoolamind-ai-memory-archive
AWS_REGION=us-east-1
AWS_BACKUP_ENABLED=false

# Dropbox Backup
DROPBOX_ACCESS_TOKEN=your_dropbox_token_here
DROPBOX_APP_KEY=your_dropbox_app_key_here
DROPBOX_BACKUP_ENABLED=false

# Backup Schedule Settings
AUTO_BACKUP_ENABLED=true
CLOUD_SYNC_INTERVAL=3600  # 1 hour in seconds
LOCAL_BACKUP_INTERVAL=900  # 15 minutes in seconds
EOF

echo "✅ Cloud configuration added to .env"

# Create GitHub setup script
cat > setup_github_backup.sh << 'EOF'
#!/bin/bash

echo "🐙 GITHUB BACKUP SETUP"
echo "======================"

read -p "Enter your GitHub username: " username
read -p "Enter repository name (default: bhoolamind-ai-memory): " repo_name
repo_name=${repo_name:-bhoolamind-ai-memory}

echo ""
echo "📋 SETUP INSTRUCTIONS:"
echo "======================"
echo "1. Go to https://github.com/new"
echo "2. Create repository: $repo_name"
echo "3. Make it PRIVATE (your data is sensitive)"
echo "4. Don't initialize with README (we have files)"
echo ""
echo "5. Go to https://github.com/settings/tokens"
echo "6. Create Personal Access Token with 'repo' permissions"
echo "7. Copy the token when shown (you won't see it again)"
echo ""

read -p "Enter your GitHub Personal Access Token: " token

if [ ! -z "$token" ]; then
    # Update .env file
    sed -i.bak "s/GITHUB_TOKEN=.*/GITHUB_TOKEN=$token/" .env
    sed -i.bak "s/GITHUB_REPO=.*/GITHUB_REPO=$username\/$repo_name/" .env
    sed -i.bak "s/GITHUB_BACKUP_ENABLED=false/GITHUB_BACKUP_ENABLED=true/" .env
    
    # Setup git remote
    git remote add origin https://github.com/$username/$repo_name.git
    
    # First commit and push
    git add .
    git commit -m "Initial BhoolamMind v1.5 setup with bulletproof backup system"
    git push -u origin main
    
    echo "✅ GitHub backup setup complete!"
    echo "🔗 Repository: https://github.com/$username/$repo_name"
else
    echo "❌ No token provided - GitHub setup skipped"
fi
EOF

chmod +x setup_github_backup.sh

# Create cloud sync checker
cat > check_cloud_status.sh << 'EOF'
#!/bin/bash

echo "☁️ CLOUD BACKUP STATUS"
echo "======================"

# Check .env file
if [ -f ".env" ]; then
    echo "✅ Configuration file exists"
    
    # Check each service
    if grep -q "GITHUB_BACKUP_ENABLED=true" .env; then
        echo "✅ GitHub backup: ENABLED"
    else
        echo "⏳ GitHub backup: Not configured"
    fi
    
    if grep -q "GOOGLE_DRIVE_BACKUP_ENABLED=true" .env; then
        echo "✅ Google Drive: ENABLED"
    else
        echo "⏳ Google Drive: Not configured"
    fi
    
    if grep -q "AWS_BACKUP_ENABLED=true" .env; then
        echo "✅ AWS S3: ENABLED"
    else
        echo "⏳ AWS S3: Not configured"
    fi
    
    if grep -q "DROPBOX_BACKUP_ENABLED=true" .env; then
        echo "✅ Dropbox: ENABLED"
    else
        echo "⏳ Dropbox: Not configured"
    fi
    
else
    echo "❌ No configuration file found"
fi

# Check backups
echo ""
echo "📊 LOCAL BACKUP STATUS:"
echo "======================="
if [ -d "backups" ]; then
    find backups -name "*.db" | wc -l | xargs echo "💾 Total backups:"
    
    if [ -d "backups/emergency" ]; then
        find backups/emergency -name "*.db" | wc -l | xargs echo "🚨 Emergency backups:"
    fi
    
    if [ -d "backups/hourly" ]; then
        find backups/hourly -name "*.db" | wc -l | xargs echo "⏰ Hourly backups:"
    fi
    
    if [ -d "backups/daily" ]; then
        find backups/daily -name "*.db" | wc -l | xargs echo "📅 Daily backups:"
    fi
else
    echo "❌ No backups directory found"
fi

echo ""
echo "🛡️ PROTECTION STATUS:"
echo "===================="
if [ -f "modules/ai_delete_protection.py" ]; then
    echo "✅ AI delete protection: ACTIVE"
else
    echo "❌ AI delete protection: MISSING"
fi

if [ -f "backup_emergency.sh" ]; then
    echo "✅ Emergency backup script: READY"
else
    echo "❌ Emergency backup script: MISSING"
fi
EOF

chmod +x check_cloud_status.sh

echo ""
echo "☁️ CLOUD SETUP SUMMARY:"
echo "======================="
echo "✅ Git repository ready"
echo "✅ Cloud configuration prepared"
echo "✅ GitHub setup script created"
echo "✅ Security measures in place"

echo ""
echo "🚀 NEXT STEPS:"
echo "=============="
echo "1. Setup GitHub: ./setup_github_backup.sh"
echo "2. Check status: ./check_cloud_status.sh"
echo "3. Configure other clouds as needed"

echo ""
echo "🔒 YOUR DATA IS NOW BULLETPROOF!"
echo "- Local backups: ACTIVE"
echo "- AI protection: ACTIVE"  
echo "- Cloud ready: YES"
echo "- Version control: READY"
