#!/bin/bash
# Revert enhanced table changes that broke Google SSO

echo "🔄 Reverting enhanced table changes to restore Google SSO..."

# Backup current state
cp index.html index-broken.html

# Check if we have a good backup
if [ -f "index.html.backup" ]; then
    echo "📋 Found backup file, restoring..."
    cp index.html.backup index.html
    echo "✅ Restored from index.html.backup"
elif [ -f "index-backup.html" ]; then
    echo "📋 Found index-backup.html, restoring..."
    cp index-backup.html index.html
    echo "✅ Restored from index-backup.html"
else
    echo "❌ No backup found. Manual restoration needed."
    echo "🚨 Please restore Google SSO authentication manually."
fi

# Remove enhanced table component reference if still present
if grep -q "enhanced-table-component.js" index.html; then
    sed -i '' '/enhanced-table-component.js/d' index.html
    echo "🧹 Removed enhanced table component reference"
fi

echo "🎯 Google SSO should now be restored!"
echo "🔗 Please test at: https://edliomap.edlio.com"