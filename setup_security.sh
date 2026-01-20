#!/bin/bash

# BhoolamMind v1.5 - Security Setup Script
# Run this to set up proper security and git management

echo "🔐 BhoolamMind v1.5 Security Setup"
echo "=================================="

# Check current directory
if [ ! -f "modules/database.py" ]; then
    echo "❌ Please run this from the bhoolamind_v1.5 directory"
    exit 1
fi

echo "📍 Current location: $(pwd)"
echo ""

# 1. Create .env file for credentials
echo "🔧 Creating .env file for future credentials..."
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# BhoolamMind v1.5 Configuration
# Add API keys here when needed

# OpenAI (for ChatGPT integration)
# OPENAI_API_KEY=your-key-here

# Anthropic (for Claude integration)
# ANTHROPIC_API_KEY=your-key-here

# Hugging Face (for models)
# HUGGINGFACE_API_KEY=your-key-here

# Database encryption (if needed)
# DB_ENCRYPTION_KEY=your-encryption-key

# Security settings
DB_PATH=memory/sqlite_db/bhoolamind.db
BACKUP_PATH=backups/
LOG_LEVEL=INFO
EOF
    chmod 600 .env
    echo "✅ Created .env file (secure permissions)"
else
    echo "✅ .env file already exists"
fi

# 2. Update .gitignore
echo "🔧 Updating .gitignore for security..."
cat >> .gitignore << 'EOF'

# BhoolamMind Security
.env
*.db
memory/
data/
backups/
__pycache__/
*.pyc
*.log

# API Keys and credentials
api_keys.txt
secrets.json
credentials.yaml
EOF

echo "✅ Updated .gitignore"

# 3. Create backup directory
echo "🔧 Creating backup directory..."
mkdir -p backups
echo "✅ Created backups/ directory"

# 4. Create first backup
echo "🔧 Creating initial backup..."
if [ -f "memory/sqlite_db/bhoolamind.db" ]; then
    cp memory/sqlite_db/bhoolamind.db "backups/bhoolamind_initial_$(date +%Y%m%d_%H%M).db"
    echo "✅ Created initial backup"
else
    echo "⚠️ No database found to backup"
fi

# 5. Create backup script
echo "🔧 Creating backup script..."
cat > backup_bhoolamind.sh << 'EOF'
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
EOF

chmod +x backup_bhoolamind.sh
echo "✅ Created backup_bhoolamind.sh"

# 6. Show current database status
echo ""
echo "📊 Current Database Status:"
echo "=========================="
if [ -f "memory/sqlite_db/bhoolamind.db" ]; then
    DB_SIZE=$(stat -f%z "memory/sqlite_db/bhoolamind.db" 2>/dev/null || stat -c%s "memory/sqlite_db/bhoolamind.db")
    echo "📁 Database: memory/sqlite_db/bhoolamind.db"
    echo "💾 Size: $DB_SIZE bytes"
    echo "🔍 To view contents: python show_learning.py"
else
    echo "❌ No database found"
fi

# 7. Security recommendations
echo ""
echo "🛡️ Security Status:"
echo "=================="
echo "✅ .env file created (secure permissions)"
echo "✅ .gitignore updated"
echo "✅ Backup system ready"
echo "✅ No external API calls yet"
echo "✅ All data stored locally"

echo ""
echo "🚨 IMPORTANT NOTES:"
echo "==================="
echo "1. Your database contains conversation data - 44 interactions"
echo "2. No passwords or credentials stored yet"
echo "3. All data is local to your machine"
echo "4. Database is NOT encrypted (can be added later)"
echo "5. Git will ignore sensitive files"

echo ""
echo "🔧 Next Steps:"
echo "=============="
echo "1. Review database: python show_learning.py"
echo "2. Create manual backup: ./backup_bhoolamind.sh"
echo "3. Add to git: git add . && git commit -m 'Setup security'"
echo "4. Add API keys to .env when needed"

echo ""
echo "✅ Security setup complete!"
