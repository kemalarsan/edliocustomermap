# Vercel Environment Variable Setup

## Setting up HubSpot API Key in Vercel

To securely store the HubSpot API key in production, follow these steps:

### 1. Via Vercel Dashboard

1. Go to your Vercel project dashboard
2. Navigate to "Settings" → "Environment Variables"
3. Add a new variable:
   - **Name**: `HUBSPOT_API_KEY`
   - **Value**: `[Your HubSpot API Key]`
   - **Environment**: Select all (Production, Preview, Development)
4. Click "Save"

### 2. Via Vercel CLI

```bash
# Install Vercel CLI if not already installed
npm i -g vercel

# Add the environment variable
vercel env add HUBSPOT_API_KEY
# When prompted, enter your HubSpot API key
# Select all environments when asked
```

### 3. Verify Setup

After deployment, the API will automatically use the environment variable. Test it by:

1. Going to https://edliomap.edlio.com/?mode=advanced
2. Press "8" for Admin view
3. Select "HubSpot Live Data"
4. Click "Test Connection"

### Security Notes

- The API key is now stored securely in Vercel's environment
- The `api-config.js` file is gitignored and won't be deployed
- The serverless function will use the environment variable automatically
- No API keys are exposed in the client-side code

### Future Environment Variables

When adding Maxio and Salesforce integration:

```
MAXIO_API_KEY=your-maxio-key
SALESFORCE_CLIENT_ID=your-salesforce-client-id
SALESFORCE_CLIENT_SECRET=your-salesforce-secret
```

### Troubleshooting

If the API key isn't working:

1. Check Vercel logs: `vercel logs`
2. Ensure the environment variable is set for the correct environment
3. Redeploy after adding environment variables: `vercel --prod`
4. Check the API response in browser DevTools Network tab