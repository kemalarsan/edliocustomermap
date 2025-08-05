# Changelog

## Version 3.7.1 - 2025-08-04 (Hotfix)

### Fixed
- HubSpot data now properly updates customer counts and metrics dashboard after sync
- Map markers now correctly display for geocoded HubSpot customers
- Fixed issue where total customer count remained at 1993 despite successful HubSpot sync
- Added missing updateTypeCounts() and updateMetricsDashboard() calls after HubSpot sync
- Ensured applyFilters() runs to include HubSpot customers in filtered data

---


## Version 3.7 - 2025-08-04

### Added
- HubSpot geocoding integration with real-time address geocoding
- Unified geocoding service for batch processing data imports
- Version control system with automated backups and rollback capability
- Comprehensive pre-deployment testing framework
- localStorage caching for geocoded addresses

### Changed
- Updated HubSpot sync function to include geocoding with progress tracking
- Enhanced map display to show geocoded HubSpot customers alongside static data
- Improved data merging logic for HubSpot and static customer data

### Fixed
- HubSpot data now displays on map with proper coordinates
- Resolved geocoding rate limiting issues with 1-second delays
- Fixed HubSpot data overlay problem that prevented customers from appearing on map

---


## Version 3.6 - 2024-07-21

### Current Stable Release
- Comprehensive competitive intelligence system
- 2,301 Apptegy competitor locations mapped
- State drill-down analysis
- Bidirectional hover system
- Admin dashboard with shared login tracking
- 7-view navigation system with keyboard shortcuts

### Known Issues
- HubSpot API authentication returning 401 errors
- HubSpot data not displaying on map (no geocoding)

---

## Previous Versions

### Version 3.5 - 2024-07-15
- Added simple JSON file shared logging
- Admin dashboard for team login visibility

### Version 3.4 - 2024-07-10
- Implemented bidirectional hover system
- Performance optimizations for rapid hovering

### Version 3.3 - 2024-07-05
- Added 7-view navigation system
- Keyboard shortcuts (1-7) for view switching

### Version 3.2 - 2024-06-28
- Advanced metrics dashboard
- Hidden by default, activated with ?mode=advanced

### Version 3.1 - 2024-06-20
- Fixed state drill-down map rendering
- Fixed main map visibility after authentication

### Version 3.0 - 2024-06-15
- Major release with competitive intelligence
- Complete UI redesign
- Enhanced filtering capabilities

### Version 2.0 - 2024-05-01
- Google SSO authentication
- Customer clustering for performance
- Export functionality

### Version 1.0 - 2024-04-01
- Initial release
- Basic customer mapping
- Search and filter capabilities