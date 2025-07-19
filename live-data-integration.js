/**
 * Live Data Integration Module for Edlio Customer Map
 * Merges static data with live HubSpot, Maxio, and Salesforce data
 */

class LiveDataIntegration {
    constructor() {
        this.hubspotAPI = null;
        this.staticData = window.customers || []; // From data.js
        this.mergedData = [];
        this.lastSync = null;
        this.syncInterval = null;
        
        // Data source status
        this.status = {
            hubspot: { connected: false, lastSync: null, recordCount: 0 },
            maxio: { connected: false, lastSync: null, recordCount: 0 },
            salesforce: { connected: false, lastSync: null, recordCount: 0 }
        };
        
        // HubSpot API key (should be stored securely in production)
        this.hubspotAPIKey = localStorage.getItem('hubspot_api_key') || 
                            (window.API_CONFIG ? window.API_CONFIG.HUBSPOT_API_KEY : '') || 
                            '';
    }

    /**
     * Initialize the live data integration
     */
    async initialize() {
        console.log('🚀 Initializing Live Data Integration...');
        
        // Initialize HubSpot API if key is available
        if (this.hubspotAPIKey) {
            this.hubspotAPI = new HubSpotAPI(this.hubspotAPIKey);
            await this.syncHubSpotData();
        }
        
        // Start periodic sync (every 5 minutes)
        this.startPeriodicSync();
        
        return this.getMergedData();
    }

    /**
     * Sync data from HubSpot
     */
    async syncHubSpotData() {
        try {
            console.log('📊 Syncing HubSpot data...');
            
            // Fetch companies from HubSpot
            const headers = {
                'Content-Type': 'application/json'
            };
            
            // Only add Authorization header if we have an API key
            if (this.hubspotAPIKey) {
                headers['Authorization'] = `Bearer ${this.hubspotAPIKey}`;
            }
            
            const response = await fetch(`/api/hubspot?path=/crm/v3/objects/companies&limit=100&properties=name,domain,address,address2,city,state,zip,country,website,phone,hs_object_id,edlio_products,contract_value,renewal_date`, {
                headers
            });

            if (!response.ok) {
                throw new Error(`HubSpot API error: ${response.status}`);
            }

            const data = await response.json();
            const hubspotCompanies = data.results || [];
            
            // Update status
            this.status.hubspot = {
                connected: true,
                lastSync: new Date(),
                recordCount: hubspotCompanies.length
            };
            
            console.log(`✅ HubSpot sync complete: ${hubspotCompanies.length} companies`);
            
            // Merge with existing data
            this.mergeHubSpotData(hubspotCompanies);
            
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