/**
 * Live Data Integration Module for Edlio Customer Map
 * Merges static data with live HubSpot, Maxio, and Salesforce data
 */

class LiveDataIntegration {
    constructor() {
        this.hubspotAPI = null;
        this.refreshStaticData();
        this.mergedData = [];
        this.lastSync = null;
        this.syncInterval = null;
        
        // Data source status
        this.status = {
            hubspot: { connected: false, lastSync: null, recordCount: 0 },
            maxio: { connected: false, lastSync: null, recordCount: 0 },
            salesforce: { connected: false, lastSync: null, recordCount: 0 }
        };
        
        // HubSpot API key - will use environment variable through proxy if not provided
        this.hubspotAPIKey = localStorage.getItem('hubspot_api_key') || 
                            (window.API_CONFIG ? window.API_CONFIG.HUBSPOT_API_KEY : '') || 
                            null; // null means use environment variable
    }

    /**
     * Initialize the live data integration
     */
    async initialize() {
        console.log('🚀 Initializing Live Data Integration...');
        
        // Always try to sync HubSpot data (will use environment variable if no key)
        await this.syncHubSpotData();
        
        // Start periodic sync (every 5 minutes)
        this.startPeriodicSync();
        
        return this.getMergedData();
    }

    /**
     * Sync data from HubSpot
     */
    async syncHubSpotData(enableGeocoding = false) {
        try {
            console.log('📊 Syncing HubSpot data...');
            console.log('🔑 API Key available:', !!this.hubspotAPIKey);
            
            // Refresh static data before merging
            this.refreshStaticData();
            
            // Fetch companies from HubSpot
            const headers = {
                'Content-Type': 'application/json'
            };
            
            // Only add Authorization header if we have an API key (otherwise use environment variable)
            if (this.hubspotAPIKey) {
                headers['Authorization'] = `Bearer ${this.hubspotAPIKey}`;
            }
            // If no API key, the proxy will use the environment variable
            
            // Build proper query parameters (HubSpot max limit is 100)
            const queryParams = new URLSearchParams({
                path: '/crm/v3/objects/companies',
                limit: '100' // HubSpot's maximum limit per request
            });
            
            const response = await fetch(`/api/hubspot?${queryParams.toString()}`, {
                headers
            });

            console.log('📡 HubSpot API Response Status:', response.status);

            if (!response.ok) {
                const errorData = await response.json();
                console.error('❌ HubSpot API Error:', errorData);
                throw new Error(`HubSpot API error: ${response.status} - ${JSON.stringify(errorData)}`);
            }

            const data = await response.json();
            console.log('📊 Raw HubSpot response:', JSON.stringify(data).substring(0, 200) + '...');
            
            const hubspotCompanies = data.results || [];
            console.log('📊 HubSpot Companies Retrieved:', hubspotCompanies.length);
            
            // If no results, check if it's an API issue
            if (hubspotCompanies.length === 0 && data.results === undefined) {
                console.warn('⚠️ Unexpected HubSpot response format:', data);
            }
            
            // Update status
            this.status.hubspot = {
                connected: true,
                lastSync: new Date(),
                recordCount: hubspotCompanies.length
            };
            
            console.log(`✅ HubSpot sync complete: ${hubspotCompanies.length} companies`);
            
            // Geocode companies if enabled
            if (enableGeocoding && typeof HubSpotGeocoder !== 'undefined') {
                console.log('🌍 Geocoding HubSpot companies...');
                const geocoder = new HubSpotGeocoder();
                
                // Load cache
                geocoder.loadGeocodedCache();
                
                // Geocode companies that need it
                const geocodedCompanies = await geocoder.geocodeCompanies(hubspotCompanies);
                
                // Save geocoded data
                geocoder.saveGeocodedData(geocodedCompanies);
                
                // Use geocoded data for merging
                this.mergeHubSpotData(geocodedCompanies);
            } else {
                // Merge without geocoding
                this.mergeHubSpotData(hubspotCompanies);
            }
            
        } catch (error) {
            console.error('❌ HubSpot sync failed:', error);
            this.status.hubspot.connected = false;
        }
    }

    /**
     * Merge HubSpot data with static data
     */
    mergeHubSpotData(hubspotCompanies) {
        console.log('🔄 Merging HubSpot data with static data...');
        console.log('📊 HubSpot companies to merge:', hubspotCompanies.length);
        console.log('📊 Static data available:', this.staticData.length);
        
        // Create a map of static data by domain/URL for quick lookup
        const staticDataMap = new Map();
        this.staticData.forEach(customer => {
            if (customer.url) {
                const domain = this.extractDomain(customer.url);
                staticDataMap.set(domain, customer);
            }
        });
        
        // Process HubSpot companies
        const enrichedData = hubspotCompanies.map(company => {
            const properties = company.properties;
            const domain = this.extractDomain(properties.website || properties.domain || '');
            
            // Find matching static data
            const staticCustomer = staticDataMap.get(domain);
            
            // Merge data - HubSpot data takes precedence for dynamic fields
            const merged = {
                // Keep geocoded location from static data
                lat: staticCustomer?.lat || null,
                lng: staticCustomer?.lng || null,
                
                // Update with live HubSpot data
                id: `hs_${company.id}`,
                name: properties.name || staticCustomer?.name || 'Unknown School',
                url: properties.website || properties.domain || staticCustomer?.url || '',
                type: this.determineSchoolType(properties, staticCustomer),
                state: properties.state || staticCustomer?.state || '',
                city: properties.city || staticCustomer?.city || '',
                
                // Live product data from HubSpot
                products: this.extractProducts(properties, staticCustomer),
                
                // Additional HubSpot fields
                contractValue: properties.contract_value || null,
                renewalDate: properties.renewal_date || null,
                lastUpdated: new Date().toISOString(),
                source: 'hubspot',
                
                // Keep static data if no HubSpot match
                ...(!company.id && staticCustomer ? staticCustomer : {})
            };
            
            return merged;
        });
        
        // Add static customers that weren't in HubSpot
        staticDataMap.forEach((customer, domain) => {
            if (!enrichedData.find(c => this.extractDomain(c.url) === domain)) {
                enrichedData.push({
                    ...customer,
                    source: 'static',
                    lastUpdated: 'static'
                });
            }
        });
        
        this.mergedData = enrichedData;
        console.log(`✅ Merge complete: ${this.mergedData.length} total customers`);
        
        // Debug: Count how many have coordinates and sources
        const withCoords = this.mergedData.filter(c => c.lat && c.lng);
        const hubspotData = this.mergedData.filter(c => c.source === 'hubspot');
        const staticData = this.mergedData.filter(c => c.source === 'static');
        
        console.log(`📍 Customers with coordinates: ${withCoords.length}/${this.mergedData.length}`);
        console.log(`🔄 HubSpot customers: ${hubspotData.length}`);
        console.log(`📊 Static customers: ${staticData.length}`);
        console.log(`🔄 HubSpot with coordinates: ${hubspotData.filter(c => c.lat && c.lng).length}`);
        
        // If no merged data, fall back to static data with source labels
        if (this.mergedData.length === 0 && this.staticData.length > 0) {
            console.log('⚠️ No HubSpot matches, using static data with source labels');
            this.mergedData = this.staticData.map(customer => ({
                ...customer,
                source: 'static',
                lastUpdated: 'static'
            }));
        }
    }

    /**
     * Get the current merged data
     */
    getMergedData() {
        return this.mergedData;
    }

    /**
     * Refresh static data from global variables
     */
    refreshStaticData() {
        // Try multiple sources for static data
        this.staticData = window.allCustomers || window.customers || [];
        
        // If no data, try loading from the data.js file
        if (this.staticData.length === 0 && typeof customers !== 'undefined') {
            this.staticData = customers;
        }
        
        console.log('📊 Static data refreshed:', this.staticData.length, 'customers');
        console.log('📊 Data sources checked - window.allCustomers:', window.allCustomers?.length || 0, 
                    ', window.customers:', window.customers?.length || 0,
                    ', global customers:', typeof customers !== 'undefined' ? customers.length : 0);
    }

    /**
     * Extract domain from URL
     */
    extractDomain(url) {
        if (!url) return '';
        try {
            const urlObj = new URL(url.startsWith('http') ? url : `https://${url}`);
            return urlObj.hostname.replace('www.', '');
        } catch {
            return url.replace('www.', '');
        }
    }

    /**
     * Determine school type from HubSpot properties
     */
    determineSchoolType(properties, staticCustomer) {
        // Check HubSpot custom field first
        if (properties.school_type) {
            return properties.school_type.toLowerCase();
        }
        
        // Fall back to name analysis
        const name = (properties.name || '').toLowerCase();
        if (name.includes('charter')) return 'charter';
        if (name.includes('district')) return 'district';
        if (name.includes('private')) return 'private';
        if (name.includes('academy')) return 'charter';
        
        // Use static data if available
        return staticCustomer?.type || 'district';
    }

    /**
     * Extract product information from HubSpot
     */
    extractProducts(properties, staticCustomer) {
        // Parse HubSpot custom field (comma-separated or JSON)
        if (properties.edlio_products) {
            try {
                // Try parsing as JSON first
                if (properties.edlio_products.startsWith('{')) {
                    return JSON.parse(properties.edlio_products);
                }
                
                // Parse comma-separated list
                const products = properties.edlio_products.toLowerCase().split(',');
                return {
                    cms: products.includes('cms'),
                    mobile: products.includes('mobile') || products.includes('access'),
                    masscomm: products.includes('masscomm') || products.includes('sia'),
                    payments: products.includes('payments')
                };
            } catch (e) {
                console.warn('Failed to parse products:', e);
            }
        }
        
        // Fall back to static data
        return staticCustomer?.products || {
            cms: true,
            mobile: false,
            masscomm: false,
            payments: false
        };
    }

    /**
     * Get merged data for the map
     */
    getMergedData() {
        return this.mergedData.length > 0 ? this.mergedData : this.staticData;
    }

    /**
     * Start periodic data sync
     */
    startPeriodicSync() {
        // Clear existing interval
        if (this.syncInterval) {
            clearInterval(this.syncInterval);
        }
        
        // Sync every 5 minutes
        this.syncInterval = setInterval(() => {
            console.log('⏰ Running periodic sync...');
            this.syncHubSpotData();
        }, 5 * 60 * 1000);
    }

    /**
     * Get data source status
     */
    getStatus() {
        return {
            ...this.status,
            lastSync: this.lastSync,
            totalRecords: this.mergedData.length,
            staticRecords: this.staticData.length
        };
    }

    /**
     * Configure API keys
     */
    configureAPIs(config) {
        if (config.hubspotAPIKey) {
            this.hubspotAPIKey = config.hubspotAPIKey;
            localStorage.setItem('hubspot_api_key', config.hubspotAPIKey);
            this.hubspotAPI = new HubSpotAPI(config.hubspotAPIKey);
        }
        
        // Future: Add Maxio and Salesforce configuration
        if (config.maxioAPIKey) {
            // this.maxioAPIKey = config.maxioAPIKey;
        }
        
        if (config.salesforceConfig) {
            // this.salesforceConfig = config.salesforceConfig;
        }
    }

    /**
     * Manual sync trigger
     */
    async syncNow() {
        console.log('🔄 Manual sync triggered...');
        await this.syncHubSpotData();
        // Future: Add Maxio and Salesforce sync
        return this.getMergedData();
    }
}

// Export for use in main application
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LiveDataIntegration;
} else {
    window.LiveDataIntegration = LiveDataIntegration;
}