# Simple Password Authentication for Edlio Customer Map

## Overview
The Edlio Customer Map now uses a simple password-based authentication system that restricts access to @edlio.com email addresses with a shared password. This is a practical solution that provides security without requiring complex OAuth setup.

## How It Works

### Authentication Process
1. **User visits the application**
2. **Login screen appears** with email and password fields
3. **User enters @edlio.com email** and the shared password
4. **System validates**:
   - Email ends with @edlio.com
   - Password matches the configured password
5. **If valid**: User gains access to the customer map
6. **If invalid**: Error message is shown

### Security Features
- **Domain restriction**: Only @edlio.com email addresses are allowed
- **Password protection**: Shared password required for access
- **Session management**: 24-hour login sessions stored locally
- **Automatic logout**: Sessions expire after 24 hours
- **Clean error handling**: Clear messages for invalid attempts

## Configuration

### Changing the Password
To change the access password, edit line 805 in `index.html`:

```javascript
const EDLIO_ACCESS_PASSWORD = 'EdlioMap2025!'; // Change this to your preferred password
```

### Adjusting Session Duration
To change how long users stay logged in, edit line 806:

```javascript
const SESSION_DURATION = 24 * 60 * 60 * 1000; // 24 hours in milliseconds
```

Examples:
- 1 hour: `1 * 60 * 60 * 1000`
- 8 hours: `8 * 60 * 60 * 1000`
- 1 week: `7 * 24 * 60 * 60 * 1000`

## Usage Instructions

### For Edlio Team Members
1. Navigate to the customer map URL
2. Enter your @edlio.com email address
3. Enter the shared access password (get this from your administrator)
4. Click "Access Customer Map"
5. You'll be logged in for 24 hours

### For Administrators
1. Share the access password with authorized team members
2. To change the password:
   - Edit the `EDLIO_ACCESS_PASSWORD` constant in index.html
   - Commit and push the changes to deploy
   - Notify team members of the new password

## Security Considerations

### Advantages
- ✅ **No external dependencies** - Works immediately without OAuth setup
- ✅ **Simple to manage** - One password for all authorized users
- ✅ **Domain restriction** - Only @edlio.com emails allowed
- ✅ **Session management** - Users don't need to re-enter password frequently
- ✅ **Easy to change** - Password can be updated quickly

### Limitations
- ⚠️ **Shared password** - All users use the same password
- ⚠️ **Client-side storage** - Session stored in browser localStorage
- ⚠️ **No individual user tracking** - Can't track who accessed what
- ⚠️ **Password visible in code** - Password is in the JavaScript source

### Best Practices
1. **Use a strong password** with letters, numbers, and special characters
2. **Change password regularly** (monthly or quarterly)
3. **Only share with authorized team members**
4. **Monitor for unauthorized access attempts**
5. **Consider upgrading to OAuth for higher security needs**

## Troubleshooting

### Common Issues
1. **"Access denied" message**: Make sure email ends with @edlio.com
2. **"Invalid password"**: Check that you're using the correct password
3. **Session expired**: Re-enter your credentials (happens after 24 hours)
4. **Login form not working**: Check browser console for JavaScript errors

### Password Recovery
If you forget the password:
1. Check line 805 in the index.html file
2. Contact your system administrator
3. Look for the password in your team's password manager

## Alternative Options

If you need more security, consider:
1. **Google OAuth** - Follow the GOOGLE_OAUTH_SETUP.md guide
2. **Individual passwords** - Create separate passwords for each user
3. **Two-factor authentication** - Add SMS or authenticator app verification
4. **Server-side authentication** - Move authentication to a backend service

## Current Configuration
- **Password**: `EdlioMap2025!` (change this!)
- **Session Duration**: 24 hours
- **Allowed Domain**: @edlio.com
- **Storage**: Browser localStorage

---

This simple authentication provides immediate security while keeping things manageable for your team. You can always upgrade to more sophisticated authentication later if needed.