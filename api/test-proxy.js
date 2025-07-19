/**
 * Debug endpoint to test proxy authentication
 */

export default async function handler(req, res) {
    // Enable CORS
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }

    // Debug info
    const authHeader = req.headers.authorization;
    const envKey = process.env.HUBSPOT_API_KEY;
    
    let finalAuth = authHeader;
    if (!authHeader && envKey) {
        finalAuth = `Bearer ${envKey}`;
    }
    
    // Test actual API call
    let apiTestResult = null;
    if (finalAuth) {
        try {
            const response = await fetch('https://api.hubapi.com/crm/v3/objects/companies?limit=1', {
                headers: {
                    'Authorization': finalAuth,
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            apiTestResult = {
                status: response.status,
                ok: response.ok,
                data: response.ok ? data : data
            };
        } catch (error) {
            apiTestResult = {
                error: error.message
            };
        }
    }
    
    res.status(200).json({
        debug: {
            received_auth_header: authHeader ? authHeader.substring(0, 20) + '...' : null,
            env_key_exists: !!envKey,
            env_key_preview: envKey ? envKey.substring(0, 15) + '...' : null,
            final_auth_used: finalAuth ? finalAuth.substring(0, 25) + '...' : null,
            headers_received: Object.keys(req.headers)
        },
        api_test: apiTestResult
    });
}