# Live Data Integration Guide for Edlio Customer Map

## Overview

This guide explains how to integrate live data from HubSpot, Maxio, and Salesforce into the Edlio Customer Map, replacing static `data.js` with real-time customer information.

## Architecture

### Current State (Static)
```
Excel Files → Python Scripts → Geocoding → data.js → Customer Map
    ↓              ↓             ↓           ↓            ↓
Manual export   Parse data   Add lat/lng  Static file  No updates
```

### Future State (Live)
```
HubSpot/Maxio/Salesforce → Live API → Merge with Geocoded Data → Dynamic Map
         ↓                    ↓              ↓                      ↓
    Real-time data      Auto-sync     Keep locations         Live updates
```

## Implementation Plan

### Phase 1: HubSpot Integration (Ready Now)

#### What's Already Built
- ✅ `hubspot-api.js` - Client-side HubSpot API wrapper
- ✅ `api/hubspot.js` - Vercel serverless proxy for CORS
- ✅ `live-data-integration.js` - Data merging logic
- ✅ `live-data-demo.html` - Working demonstration

#### Integration Steps

1. **Add Live Data Scripts to index.html**
```html
<!-- Add after data.js -->
<script src="hubspot-api.js"></script>
<script src="live-data-integration.js"></script>
```

2. **Initialize Live Data on Page Load**
```javascript
// Replace the static customer loading with:
let liveDataIntegration = null;

async function initializeLiveData() {
    // Initialize live data integration
    liveDataIntegration = new LiveDataIntegration();
    
    // Configure with API key (store securely!)
    liveDataIntegration.configureAPIs({
        hubspotAPIKey: 'your-hubspot-api-key'
    });
    
    // Get merged data
    const liveCustomers = await liveDataIntegration.initialize();
    
    // Use live data in the map
    customers = liveCustomers;
    allCustomers = liveCustomers;
    filteredCustomers = liveCustomers;
    
    // Update the map
    updateMap();
}
```

3. **Add Live Data Indicator**
```html
<!-- Add to sidebar -->
<div class="live-status">
    <span class="live-indicator"></span>
    Live Data: <span id="liveStatus">Connecting...</span>
</div>
```

### Phase 2: Incremental Updates

Instead of replacing all data at once, merge live updates:

```javascript
// Merge strategy preserves geocoded locations
function mergeCustomerData(staticCustomer, liveCustomer) {
    return {
        // Keep geocoded location
        lat: staticCustomer.lat,
        lng: staticCustomer.lng,
        
        // Update with live data
        name: liveCustomer.name || staticCustomer.name,
        products: liveCustomer.products || staticCustomer.products,
        contractValue: liveCustomer.contractValue,
        renewalDate: liveCustomer.renewalDate,
        
        // Metadata
        lastUpdated: new Date().toISOString(),
        source: 'hubspot'
    };
}
```

### Phase 3: Add Real-time Features

#### Contract Values on Map
```javascript
// Show contract value in popup
function createPopupContent(customer) {
    return `
        <div class="popup-title">${customer.name}</div>
        <div class="popup-info">Contract: $${customer.contractValue?.toLocaleString() || 'N/A'}</div>
        <div class="popup-info">Renewal: ${customer.renewalDate || 'N/A'}</div>
    `;
}
```

#### Live Filtering
```javascript
// Add contract value filter
<select id="contractFilter">
    <option value="">All Contracts</option>
    <option value="0-10000">Under $10K</option>
    <option value="10000-50000">$10K - $50K</option>
    <option value="50000+">Over $50K</option>
</select>
```

## API Configuration

### HubSpot Setup

1. **Get Private App Token**
   - Go to HubSpot Settings → Integrations → Private Apps
   - Create app with CRM permissions
   - Copy the access token

2. **Required Scopes**
   - `crm.objects.companies.read`
   - `crm.objects.contacts.read`
   - `crm.objects.deals.read`

3. **Custom Properties Needed**
   ```
   edlio_products: Multi-checkbox (CMS, Mobile, MassComm, Payments)
   school_type: Dropdown (District, Charter, Private, CMO, ESC)
   contract_value: Number
   renewal_date: Date
   ```

### Maxio Integration (Phase 2)

```javascript
// Future Maxio integration
async function syncMaxioData() {
    const response = await fetch('/api/maxio/subscriptions', {
        headers: {
            'Authorization': `Bearer ${maxioAPIKey}`,
            'Accept': 'application/json'
        }
    });
    
    const subscriptions = await response.json();
    
    // Merge subscription data
    subscriptions.forEach(sub => {
        const customer = findCustomerByDomain(sub.customer.domain);
        if (customer) {
            customer.mrr = sub.mrr_in_cents / 100;
            customer.subscription_state = sub.state;
        }
    });
}
```

### Salesforce Integration (Phase 3)

```javascript
// Future Salesforce integration using JSforce
const conn = new jsforce.Connection({
    instanceUrl: 'https://edlio.my.salesforce.com',
    accessToken: salesforceToken
});

const accounts = await conn.query(
    "SELECT Id, Name, Website, Type, AnnualRevenue FROM Account WHERE Type = 'Customer'"
);
```

## Security Considerations

### API Key Storage

**DON'T**: Store API keys in client-side code
```javascript
// BAD - Never do this!
const API_KEY = 'pak-na1-xxxxx-xxxxx';
```

**DO**: Use environment variables
```javascript
// Good - Use Vercel environment variables
const API_KEY = process.env.HUBSPOT_API_KEY;
```

### Implement Authentication Check
```javascript
// Only allow authenticated users to access live data
if (!isAuthenticated || !currentUser.email.endsWith('@edlio.com')) {
    throw new Error('Unauthorized access to live data');
}
```

## Performance Optimization

### Caching Strategy
```javascript
// Cache live data for 5 minutes
const CACHE_DURATION = 5 * 60 * 1000;

if (Date.now() - lastSync < CACHE_DURATION) {
    return cachedData;
}
```

### Pagination for Large Datasets
```javascript
// HubSpot pagination
async function getAllCompanies() {
    let allCompanies = [];
    let after = null;
    
    do {
        const response = await fetchCompanies({ after, limit: 100 });
        allCompanies = allCompanies.concat(response.results);
        after = response.paging?.next?.after;
    } while (after);
    
    return allCompanies;
}
```

## Testing Strategy

### 1. Test API Connection
```bash
# Test HubSpot API
curl https://api.hubapi.com/crm/v3/objects/companies?limit=1 \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### 2. Test Data Merge
- Verify geocoded locations are preserved
- Check that products update correctly
- Ensure no duplicate customers

### 3. Performance Testing
- Load time with live data
- Memory usage with large datasets
- API rate limit handling

## Rollout Plan

### Week 1: Development Environment
- Set up API keys in Vercel
- Test with subset of data
- Verify merge logic

### Week 2: Staging
- Deploy to staging URL
- Test with full dataset
- Monitor performance

### Week 3: Production
- Gradual rollout (10% → 50% → 100%)
- Monitor error rates
- Gather user feedback

## Monitoring

### Add Analytics
```javascript
// Track live data performance
window.gtag('event', 'live_data_sync', {
    source: 'hubspot',
    record_count: customers.length,
    sync_duration: syncTime,
    errors: errorCount
});
```

### Error Handling
```javascript
// Graceful fallback to static data
try {
    customers = await liveDataIntegration.syncNow();
} catch (error) {
    console.error('Live data sync failed, using static data', error);
    customers = window.customers; // Fallback to data.js
    
    // Notify user
    showNotification('Using cached data. Live sync unavailable.', 'warning');
}
```

## Benefits

### Immediate Value
1. **Real-time Product Usage**: See which schools use which products
2. **Contract Values**: Visualize revenue by geography
3. **Renewal Tracking**: Identify upcoming renewals on the map
4. **Churn Risk**: Highlight at-risk customers

### Future Possibilities
1. **Predictive Analytics**: ML models using live data
2. **Sales Intelligence**: Opportunity scoring
3. **Customer Health Scores**: Combine usage + contract data
4. **Automated Alerts**: Notify sales of changes

## Next Steps

1. **Get API Keys**
   - HubSpot Private App token
   - Maxio API credentials
   - Salesforce OAuth setup

2. **Update Vercel Environment**
   ```bash
   vercel env add HUBSPOT_API_KEY
   vercel env add MAXIO_API_KEY
   vercel env add SALESFORCE_CLIENT_ID
   ```

3. **Test Integration**
   - Open `live-data-demo.html`
   - Enter API key
   - Verify data sync

4. **Deploy to Production**
   - Create feature branch
   - Add live data integration
   - Test thoroughly
   - Merge to main

---

Ready to make your customer map come alive with real-time data? The infrastructure is built and waiting!