/**
 * HubSpot API Integration Module
 * Fetches companies (schools) data from HubSpot and converts to map format
 */

class HubSpotAPI {
    constructor(apiKey) {
        this.apiKey = apiKey;
        this.baseURL = 'https://api.hubapi.com';
        this.cache = new Map();
        this.lastSync = null;
    }

    /**
     * Fetch all companies from HubSpot
     */
    async fetchCompanies() {
        try {
            // Use Vercel proxy to avoid CORS issues
            const response = await fetch(`/api/hubspot?path=/crm/v3/objects/companies&limit=100&properties=name,address,city,state,zip,country,website,phone,hs_object_id`, {
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HubSpot API error: ${response.status}`);
            }

            const data = await response.json();
            return data.results || [];
        } catch (error) {
            console.error('Error fetching HubSpot companies:', error);
            throw error;
        }
    }

    /**
     * Convert HubSpot company to school format
     */
    convertToSchoolFormat(company) {
        const properties = company.properties;
        
        return {
            id: `hs_${company.id}`,
            name: properties.name || 'Unknown School',
            address: this.buildAddress(properties),
            city: properties.city || '',
            state: properties.state || '',
            zip: properties.zip || '',
            website: properties.website || '',
            phone: properties.phone || '',
            type: this.determineSchoolType(properties),
            products: this.extractProducts(properties),
            source: 'hubspot',
            lastUpdated: new Date().toISOString()
        };
    }

    /**
     * Build full address from HubSpot properties
     */
    buildAddress(properties) {
        const parts = [
            properties.address,
            properties.city,
            properties.state,
            properties.zip
        ].filter(part => part && part.trim());
        
        return parts.join(', ');
    }

    /**
     * Determine school type from HubSpot properties
     * This will need customization based on your HubSpot setup
     */
    determineSchoolType(properties) {
        // Default logic - customize based on your HubSpot custom properties
        const name = (properties.name || '').toLowerCase();
        
        if (name.includes('charter')) return 'charter';
        if (name.includes('district')) return 'district';
        if (name.includes('private')) return 'private';
        if (name.includes('academy')) return 'charter';
        
        return 'district'; // Default
    }

    /**
     * Extract Edlio products from HubSpot properties
     * Customize based on your HubSpot custom fields
     */
    extractProducts(properties) {
        return {
            cms: properties.has_cms === 'true' || false,
            mobile_app: properties.has_mobile_app === 'true' || false,
            mass_communications: properties.has_mass_comm === 'true' || false,
            payments: properties.has_payments === 'true' || false
        };
    }

    /**
     * Sync data from HubSpot and return in map format
     */
    async syncData() {
        try {
            console.log('Starting HubSpot sync...');
            const companies = await this.fetchCompanies();
            
            const schools = companies.map(company => this.convertToSchoolFormat(company));
            
            // Cache the results
            this.cache.set('schools', schools);
            this.lastSync = new Date();
            
            console.log(`HubSpot sync complete: ${schools.length} schools`);
            return schools;
            
        } catch (error) {
            console.error('HubSpot sync failed:', error);
            throw error;
        }
    }

    /**
     * Get cached data or sync if needed
     */
    async getData(forceSync = false) {
        if (forceSync || !this.cache.has('schools') || this.isStale()) {
            return await this.syncData();
        }
        
        return this.cache.get('schools');
    }

    /**
     * Check if cached data is stale (older than 1 hour)
     */
    isStale() {
        if (!this.lastSync) return true;
        
        const oneHour = 60 * 60 * 1000;
        return (new Date() - this.lastSync) > oneHour;
    }

    /**
     * Get sync status
     */
    getStatus() {
        return {
            isConnected: !!this.apiKey,
            lastSync: this.lastSync,
            cachedCount: this.cache.has('schools') ? this.cache.get('schools').length : 0,
            isStale: this.isStale()
        };
    }
}

// Export for use in main application
if (typeof module !== 'undefined' && module.exports) {
    module.exports = HubSpotAPI;
} else {
    window.HubSpotAPI = HubSpotAPI;
}