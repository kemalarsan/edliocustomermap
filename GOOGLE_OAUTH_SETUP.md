# Google OAuth Setup for Edlio Customer Map

## Overview
The Edlio Customer Map now includes Google SSO authentication that restricts access to only @edlio.com email addresses. This ensures that sensitive customer data is only accessible to authorized Edlio team members.

## Setup Instructions

### Step 1: Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the "Google+ API" (for user profile information)

### Step 2: Configure OAuth Consent Screen
1. Go to APIs & Services → OAuth consent screen
2. Choose "Internal" user type (restricts to your organization)
3. Fill in application information:
   - Application name: "Edlio Customer Map"
   - User support email: your@edlio.com
   - Application home page: https://your-domain.vercel.app
   - Authorized domains: Add your deployment domain (e.g., vercel.app)
   - Developer contact information: your@edlio.com

### Step 3: Create OAuth 2.0 Credentials
1. Go to APIs & Services → Credentials
2. Click "Create Credentials" → "OAuth 2.0 Client ID"
3. Application type: "Web application"
4. Name: "Edlio Customer Map"
5. Authorized JavaScript origins:
   - `https://your-domain.vercel.app`
   - `http://localhost:3000` (for testing)
6. Authorized redirect URIs:
   - `https://your-domain.vercel.app`
   - `http://localhost:3000` (for testing)

### Step 4: Update Application Configuration
1. Copy the Client ID from your OAuth 2.0 credentials
2. Replace `YOUR_GOOGLE_CLIENT_ID` in index.html with your actual Client ID:
   ```javascript
   const GOOGLE_CLIENT_ID = 'your-actual-client-id-here.apps.googleusercontent.com';
   ```

### Step 5: Deploy Changes
1. Commit and push your changes to trigger deployment
2. Test the authentication flow with an @edlio.com email address

## Security Features

### Domain Restriction
- Only @edlio.com email addresses can access the application
- Users with other email domains will see an access denied message

### Authentication Flow
1. User visits the application
2. Authentication overlay appears with Google Sign-In button
3. User signs in with Google
4. Application verifies the email domain
5. If authorized, user sees the customer map
6. If not authorized, user sees an error message

### User Experience
- Clean, branded login screen with Edlio colors
- User information displayed in top-right corner when authenticated
- Sign out button for easy logout
- Automatic authentication check on page load

## Testing

### Valid Test Cases
- Sign in with any @edlio.com email address
- Should successfully access the customer map
- User info should display correctly
- Sign out should work properly

### Invalid Test Cases
- Try signing in with @gmail.com or other domains
- Should see "Access denied" message
- Should remain on login screen

## Troubleshooting

### Common Issues
1. **"Invalid Client ID"**: Make sure you've replaced YOUR_GOOGLE_CLIENT_ID with your actual client ID
2. **"Not authorized"**: Verify your domain is added to authorized origins
3. **"Access denied"**: Check that you're using an @edlio.com email address

### Production Considerations
- Store the Client ID as an environment variable in production
- Consider implementing session persistence for better UX
- Add logging for authentication events
- Monitor for suspicious access attempts

## Environment Variables (Optional)
For production deployments, you may want to use environment variables:

```javascript
const GOOGLE_CLIENT_ID = process.env.GOOGLE_CLIENT_ID || 'YOUR_GOOGLE_CLIENT_ID';
```

This setup provides enterprise-grade security while maintaining a smooth user experience for authorized Edlio team members.