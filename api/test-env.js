/**
 * Test endpoint to verify environment variables are set
 */

export default async function handler(req, res) {
    // Enable CORS
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }

    // Return environment variable status (masked for security)
    const hubspotKey = process.env.HUBSPOT_API_KEY;
    
    res.status(200).json({
        hubspot_key_set: !!hubspotKey,
        hubspot_key_preview: hubspotKey ? hubspotKey.substring(0, 15) + '...' : 'NOT SET',
        node_env: process.env.NODE_ENV || 'not set',
        vercel: !!process.env.VERCEL,
        timestamp: new Date().toISOString()
    });
}