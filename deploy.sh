#!/bin/bash
# Deploy enhanced table features

echo "🚀 Deploying enhanced table features..."

# Stage the files
git add enhanced-table-component.js index.html

# Commit with message
git commit -m "Add advanced table views with search, sorting, and pagination

🔥 ENHANCED TABLE FEATURES:
- EnhancedTable component with virtual scrolling and advanced filtering
- Column sorting (clickable headers with sort indicators)
- Real-time search across all columns
- Pagination controls (25/50/100 per page, or show all)
- Export filtered results to CSV
- Responsive design with sticky headers

📊 STATE DRILL-DOWN IMPROVEMENTS:
- Three view modes: Competitors, Customers, Side-by-Side
- Enhanced competitor table with 6 columns (name, city, state, domain, owner, created)
- Enhanced customer table with 5 columns (name, type, city, products, website)
- Advanced filtering perfect for 5,696 competitor dataset

🎯 PROXIMITY ANALYSIS UPGRADE:
- Enhanced proximity table with advanced search and filtering
- Risk level sorting and filtering
- Domain risk analysis integration
- Export capabilities for sales team

Perfect for handling the expanded 5,696 Apptegy competitor dataset with performance and usability.

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to production
git push

echo "✅ Enhanced table features deployed to production!"
echo "🎯 Available at: https://edliomap.edlio.com"