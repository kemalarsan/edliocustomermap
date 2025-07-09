/**
 * Simple Node.js proxy server for HubSpot API calls
 * Run with: node hubspot-proxy.js
 * Deploy to Vercel as serverless function
 */

const http = require('http');
const https = require('https');
const url = require('url');

const PORT = process.env.PORT || 3001;

// CORS headers
const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Content-Type': 'application/json'
};

const server = http.createServer((req, res) => {
    // Handle CORS preflight
    if (req.method === 'OPTIONS') {
        res.writeHead(200, corsHeaders);
        res.end();
        return;
    }

    // Only allow GET requests to HubSpot API
    if (req.method !== 'GET') {
        res.writeHead(405, corsHeaders);
        res.end(JSON.stringify({ error: 'Method not allowed' }));
        return;
    }

    const urlParts = url.parse(req.url, true);
    const apiPath = urlParts.pathname.replace('/api/hubspot', '');
    
    // Get Authorization header
    const authHeader = req.headers.authorization;
    if (!authHeader) {
        res.writeHead(401, corsHeaders);
        res.end(JSON.stringify({ error: 'Authorization header required' }));
        return;
    }

    // Construct HubSpot API URL
    const hubspotUrl = `https://api.hubapi.com${apiPath}?${urlParts.query || ''}`;
    
    console.log('Proxying request to:', hubspotUrl);

    // Make request to HubSpot API
    const options = {
        headers: {
            'Authorization': authHeader,
            'Content-Type': 'application/json',
            'User-Agent': 'Edlio-Customer-Map/1.0'
        }
    };

    https.get(hubspotUrl, options, (hubspotRes) => {
        let data = '';
        
        hubspotRes.on('data', (chunk) => {
            data += chunk;
        });
        
        hubspotRes.on('end', () => {
            res.writeHead(hubspotRes.statusCode, corsHeaders);
            res.end(data);
        });
    }).on('error', (error) => {
        console.error('HubSpot API error:', error);
        res.writeHead(500, corsHeaders);
        res.end(JSON.stringify({ error: 'Proxy error', details: error.message }));
    });
});

server.listen(PORT, () => {
    console.log(`HubSpot proxy server running on port ${PORT}`);
    console.log(`Use: http://localhost:${PORT}/api/hubspot/crm/v3/objects/companies`);
});

module.exports = server;