/**
 * HubSpot Geocoding Integration
 * Fetches HubSpot data and geocodes addresses for map display
 */

class HubSpotGeocodeIntegration {
    constructor() {
        this.geocodeCache = new Map();
        this.loadCache();
        this.rateLimitDelay = 1000; // 1 second between geocoding requests
        this.lastGeocode = 0;
    }

    /**
     * Load geocoding cache from localStorage
     */
    loadCache() {
        try {
            const cached = localStorage.getItem('hubspot_geocode_cache');
            if (cached) {
                const data = JSON.parse(cached);
                this.geocodeCache = new Map(data);
                console.log(`📍 Loaded ${this.geocodeCache.size} cached geocodes`);
            }
        } catch (e) {
            console.error('Failed to load geocode cache:', e);
        }
    }

    /**
     * Save geocoding cache to localStorage
     */
    saveCache() {
        try {
            const data = Array.from(this.geocodeCache.entries());
            localStorage.setItem('hubspot_geocode_cache', JSON.stringify(data));
        } catch (e) {
            console.error('Failed to save geocode cache:', e);
        }
    }

    /**
     * Geocode an address using Nominatim with rate limiting
     */
    async geocodeAddress(address) {
        if (!address) return null;
        
        // Check cache first
        if (this.geocodeCache.has(address)) {
            return this.geocodeCache.get(address);
        }

        // Rate limiting
        const now = Date.now();
        const timeSinceLastRequest = now - this.lastGeocode;
        if (timeSinceLastRequest < this.rateLimitDelay) {
            await new Promise(resolve => 
                setTimeout(resolve, this.rateLimitDelay - timeSinceLastRequest)
            );
        }

        try {
            this.lastGeocode = Date.now();
            
            const params = new URLSearchParams({
                q: address,
                format: 'json',
                limit: '1',
                countrycodes: 'us'
            });

            const response = await fetch(
                `https://nominatim.openstreetmap.org/search?${params}`,
                {
                    headers: {
                        'User-Agent': 'Edlio Customer Map Geocoder',
                        'Accept': 'application/json'
                    }
                }
            );

            if (!response.ok) {
                throw new Error(`Geocoding failed: ${response.status}`);
            }

            const data = await response.json();
            
            if (data && data.length > 0) {
                const result = {
                    lat: parseFloat(data[0].lat),
                    lng: parseFloat(data[0].lon),
                    display_name: data[0].display_name
                };
                
                // Cache the result
                this.geocodeCache.set(address, result);
                this.saveCache();
                
                return result;
            }
            
            // Cache null results to avoid repeated failed lookups
            this.geocodeCache.set(address, null);
            this.saveCache();
            
            return null;
        } catch (error) {
            console.error(`Geocoding error for "${address}":`, error);
            return null;
        }
    }

    /**
     * Process HubSpot companies and add geocoding
     */
    async processHubSpotData(companies, options = {}) {
        const { 
            batchSize = 10, 
            onProgress = () => {},
            maxRetries = 3 
        } = options;

        const results = [];
        const totalCompanies = companies.length;
        
        console.log(`🗺️ Starting geocoding for ${totalCompanies} HubSpot companies`);

        for (let i = 0; i < companies.length; i += batchSize) {
            const batch = companies.slice(i, Math.min(i + batchSize, companies.length));
            
            const batchResults = await Promise.all(
                batch.map(async (company) => {
                    const properties = company.properties || {};
                    
                    // Build address for geocoding
                    const addressParts = [
                        properties.address,
                        properties.city,
                        properties.state,
                        properties.zip
                    ].filter(part => part && part.trim());
                    
                    const fullAddress = addressParts.join(', ');
                    
                    // If we have a full address, try to geocode
                    let geocodeResult = null;
                    if (fullAddress.length > 5) { // Basic validation
                        geocodeResult = await this.geocodeAddress(fullAddress);
                    }
                    
                    // Convert to map format with geocoding
                    return {
                        id: `hs_${company.id}`,
                        name: properties.name || 'Unknown School',
                        address: fullAddress,
                        city: properties.city || '',
                        state: properties.state || '',
                        zip: properties.zip || '',
                        website: properties.website || '',
                        phone: properties.phone || '',
                        type: this.determineSchoolType(properties),
                        products: this.extractProducts(properties),
                        source: 'hubspot',
                        lastUpdated: new Date().toISOString(),
                        lat: geocodeResult?.lat || null,
                        lng: geocodeResult?.lng || null,
                        geocoded: !!geocodeResult,
                        geocodeDisplay: geocodeResult?.display_name || null
                    };
                })
            );
            
            results.push(...batchResults);
            
            // Report progress
            const progress = Math.min(100, Math.round((i + batch.length) / totalCompanies * 100));
            const geocoded = results.filter(r => r.geocoded).length;
            
            onProgress({
                processed: i + batch.length,
                total: totalCompanies,
                geocoded: geocoded,
                progress: progress
            });
            
            console.log(`📍 Progress: ${i + batch.length}/${totalCompanies} (${geocoded} geocoded)`);
        }
        
        console.log(`✅ Geocoding complete: ${results.filter(r => r.geocoded).length}/${totalCompanies} successfully geocoded`);
        
        return results;
    }

    /**
     * Determine school type from HubSpot properties
     */
    determineSchoolType(properties) {
        if (properties.school_type) {
            return properties.school_type.toLowerCase();
        }
        
        const name = (properties.name || '').toLowerCase();
        if (name.includes('charter')) return 'charter';
        if (name.includes('district')) return 'district';
        if (name.includes('private')) return 'private';
        if (name.includes('academy')) return 'charter';
        
        return 'district';
    }

    /**
     * Extract product information from HubSpot
     */
    extractProducts(properties) {
        // Check for Edlio products field
        if (properties.edlio_products) {
            try {
                if (properties.edlio_products.startsWith('{')) {
                    return JSON.parse(properties.edlio_products);
                }
                
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
        
        // Default products based on common patterns
        return {
            cms: true, // Most Edlio customers have CMS
            mobile: false,
            masscomm: false,
            payments: false
        };
    }

    /**
     * Merge geocoded HubSpot data with existing customer data
     */
    mergeWithExistingData(hubspotData, existingData) {
        const merged = new Map();
        
        // First, add all existing data
        existingData.forEach(customer => {
            const key = this.getCustomerKey(customer);
            merged.set(key, {
                ...customer,
                source: customer.source || 'static'
            });
        });
        
        // Then, overlay HubSpot data
        hubspotData.forEach(hsCustomer => {
            const key = this.getCustomerKey(hsCustomer);
            
            if (merged.has(key)) {
                // Update existing customer with HubSpot data
                const existing = merged.get(key);
                merged.set(key, {
                    ...existing,
                    ...hsCustomer,
                    source: 'hubspot_updated',
                    originalData: existing // Keep reference to original
                });
            } else {
                // Add new customer from HubSpot
                merged.set(key, hsCustomer);
            }
        });
        
        return Array.from(merged.values());
    }

    /**
     * Generate a unique key for customer matching
     */
    getCustomerKey(customer) {
        // Try to match by domain first
        if (customer.website || customer.url) {
            const url = customer.website || customer.url;
            const domain = url.replace(/^https?:\/\//, '').replace(/^www\./, '').split('/')[0];
            return `domain:${domain}`;
        }
        
        // Fall back to name + state
        const name = (customer.name || '').toLowerCase().replace(/[^a-z0-9]/g, '');
        const state = (customer.state || '').toUpperCase();
        return `name:${name}:${state}`;
    }
}

// Export for use in main application
if (typeof module !== 'undefined' && module.exports) {
    module.exports = HubSpotGeocodeIntegration;
} else {
    window.HubSpotGeocodeIntegration = HubSpotGeocodeIntegration;
}