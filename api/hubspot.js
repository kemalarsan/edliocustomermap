/**
 * Vercel serverless function to proxy HubSpot API calls
 * Handles CORS and API authentication
 */

export default async function handler(req, res) {
    // Enable CORS
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

    // Handle preflight request
    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }

    // Only allow GET requests
    if (req.method !== 'GET') {
        res.status(405).json({ error: 'Method not allowed' });
        return;
    }

    // Get Authorization header
    const authHeader = req.headers.authorization;
    if (!authHeader) {
        res.status(401).json({ error: 'Authorization header required' });
        return;
    }

    try {
        // Extract the HubSpot API path from query parameters
        const { path = '/crm/v3/objects/companies', ...queryParams } = req.query;
        
        // Build query string
        const queryString = new URLSearchParams(queryParams).toString();
        const hubspotUrl = `https://api.hubapi.com${path}${queryString ? '?' + queryString : ''}`;
        
        console.log('Proxying request to:', hubspotUrl);

        // Make request to HubSpot API
        const response = await fetch(hubspotUrl, {
            method: 'GET',
            headers: {
                'Authorization': authHeader,
                'Content-Type': 'application/json',
                'User-Agent': 'Edlio-Customer-Map/1.0'
            }
        });

        const data = await response.json();

        if (!response.ok) {
            res.status(response.status).json({ 
                error: 'HubSpot API error', 
                details: data 
            });
            return;
        }

        res.status(200).json(data);
        
    } catch (error) {
        console.error('Proxy error:', error);
        res.status(500).json({ 
            error: 'Proxy error', 
            details: error.message 
        });
    }
}