# Edlio Customer Map - Stable Features (v3.0-stable)

## Current Stable State
This document describes the features in the v3.0-stable release.

### Core Features ✅

1. **Interactive Customer Map**
   - Leaflet-based map with OpenStreetMap tiles
   - Customer clustering for performance
   - Color-coded markers by school type
   - Click markers for customer details

2. **Google SSO Authentication**
   - Restricted to @edlio.com emails only
   - Session persistence for 50 minutes
   - Login activity tracking
   - Clean sign-out functionality

3. **Advanced Metrics Dashboard** (?mode=advanced)
   - 5 key metrics displayed:
     - Active Customers
     - Total ARR
     - Average Contract Value
     - Customer Types Distribution
     - Renewal Risk Analysis
   - Hidden by default, activated with URL parameter

4. **Complete 6-View Navigation System** (?mode=advanced)
   - **🗺️ Map View (1)**: Interactive customer map with clustering
   - **📊 Table View (2)**: Customer table showing first 50 records
   - **📈 Analytics View (3)**: Revenue metrics and state breakdowns
   - **📅 Timeline View (4)**: Contract renewals and at-risk accounts
   - **🎯 Adoption View (5)**: Product mix analysis and upsell opportunities
   - **🎧 Support View (6)**: Technical support metrics and issue tracking
   - Full keyboard shortcuts (Press 1-6 to switch views)
   - Tab-based interface with visual indicators
   - All views respect current filter state

5. **Search & Filter Capabilities**
   - Search by school name
   - Filter by school type (Charter, District, Private, CMO, ESC)
   - Filter by products (CMS, Mobile App, Mass Comm, Payments)
   - Geographic search by ZIP code with radius

6. **Export Functions**
   - Export current view customers to CSV
   - Export all filtered customers to CSV
   - Login activity export for admins

### Stable Architecture
- Single index.html file
- External data.js with 2348 customer records
- No complex state management
- Clean separation of concerns

### Known Working Features
- ✅ Authentication persists on refresh
- ✅ Map loads properly after login
- ✅ All filters work correctly
- ✅ Export functions operate as expected
- ✅ Metrics dashboard displays with advanced mode
- ✅ All 6 navigation tabs function properly
- ✅ Keyboard shortcuts (1-6) work seamlessly
- ✅ View switching maintains filter state
- ✅ Real-time data calculations in all views
- ✅ Responsive design works on all screen sizes

### Deployment
- Hosted on Vercel
- Automatic deployment from main branch
- Domain: https://edliomap.edlio.com

## Development Guidelines

### Safe Development Process
1. Always branch from v2.0-stable tag for new features
2. Test thoroughly on feature branches
3. Never commit directly to main
4. Use pull requests for code review
5. Tag stable releases before major changes

### Branch Strategy
- `main` - Production branch (protected)
- `develop` - Integration branch for new features
- `feature/*` - Individual feature branches
- `fix/*` - Bug fix branches

### Testing Checklist
Before merging any changes:
- [ ] Login works and persists on refresh
- [ ] Map loads with all customers
- [ ] Filters function correctly
- [ ] Export features work
- [ ] No console errors
- [ ] Performance is acceptable