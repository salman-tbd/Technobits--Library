# Google OAuth Setup Guide

This guide walks you through setting up Google OAuth for the authentication system.

## 📋 Prerequisites

- A Google account
- Access to Google Cloud Console

## 🚀 Step-by-Step Setup

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click "New Project"
4. Enter a project name (e.g., "Auth Demo")
5. Click "Create"

### 2. Enable Google+ API

1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google+ API"
3. Click on "Google+ API"
4. Click "Enable"

### 3. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client ID"
3. If prompted, configure the OAuth consent screen first:
   - Choose "External" for user type
   - Fill in the required fields:
     - App name: "Auth Demo"
     - User support email: your email
     - Developer contact information: your email
   - Click "Save and Continue"
   - Skip scopes for now, click "Save and Continue"
   - Add test users if needed, click "Save and Continue"

4. Back to creating OAuth client ID:
   - Application type: "Web application"
   - Name: "Auth Demo Client"
   - Authorized origins:
     - `http://localhost:3000` (for development)
     - `https://yourdomain.com` (for production)
   - Authorized redirect URIs: (leave empty for Google Identity Services)

5. Click "Create"
6. Copy the Client ID (you'll need this for environment variables)

### 4. Configure Environment Variables

#### Frontend (.env.local)
```bash
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
```

#### Backend (.env)
```bash
GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
```

**Important:** Use the same Client ID for both frontend and backend.

### 5. Test the Integration

1. Start your development servers:
   ```bash
   pnpm dev
   ```

2. Visit `http://localhost:3000/login`
3. Click the Google Sign-In button
4. Complete the Google authentication flow
5. You should be redirected back and logged in

## 🔒 Security Considerations

### Production Setup

1. **Update Authorized Origins:**
   - Remove `http://localhost:3000`
   - Add your production domain: `https://yourdomain.com`

2. **OAuth Consent Screen:**
   - Submit for verification if you plan to have many users
   - Add privacy policy and terms of service URLs

3. **Environment Variables:**
   ```bash
   # Frontend
   NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
   
   # Backend
   GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
   ```

### Best Practices

1. **Never expose the Client Secret** - Google Identity Services doesn't need it
2. **Use HTTPS in production** - Required for secure cookies
3. **Validate domains** - Only add trusted domains to authorized origins
4. **Monitor usage** - Check Google Cloud Console for API usage

## 🐛 Troubleshooting

### Common Issues

**"Google Client ID not found"**
- Ensure environment variables are set correctly
- Restart your development servers after adding env vars
- Check that the variable names match exactly

**"Invalid origin" error**
- Add your domain to authorized origins in Google Cloud Console
- Make sure the protocol (http/https) matches exactly
- For localhost, use `http://localhost:3000` not `http://localhost:3000/`

**"Invalid client" error**
- Double-check the Client ID is copied correctly
- Ensure the Client ID is the same in both frontend and backend
- Verify the project is enabled for Google+ API

**Google button not loading**
- Check browser console for JavaScript errors
- Ensure Google Identity Services script is loading
- Verify the Client ID is valid and not expired

### Debug Mode

To enable debug logging, add this to your frontend:

```javascript
// In your browser console
localStorage.setItem('debug', 'google-auth');
```

## 📚 Additional Resources

- [Google Identity Services Documentation](https://developers.google.com/identity/gsi/web)
- [Google Cloud Console](https://console.cloud.google.com/)
- [OAuth 2.0 Best Practices](https://tools.ietf.org/html/draft-ietf-oauth-security-topics)

## 🆘 Need Help?

If you encounter issues:

1. Check the browser developer console for errors
2. Verify all environment variables are set
3. Ensure Google Cloud project is properly configured
4. Check that APIs are enabled in Google Cloud Console
