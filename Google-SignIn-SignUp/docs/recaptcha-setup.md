# reCAPTCHA v3 Setup Guide

This guide will help you set up Google reCAPTCHA v3 for your authentication system.

## 1. Get reCAPTCHA Keys

1. Go to the [Google reCAPTCHA Admin Console](https://www.google.com/recaptcha/admin)
2. Click on "Create" to create a new site
3. Fill in the form:
   - **Label**: Your project name (e.g., "Google Sign-In/Sign-Up")
   - **reCAPTCHA type**: Choose "reCAPTCHA v3"
   - **Domains**: Add your domains:
     - For development: `localhost`, `127.0.0.1`
     - For production: your actual domain (e.g., `example.com`)
   - Accept the reCAPTCHA Terms of Service
4. Click "Submit"
5. Copy the **Site Key** and **Secret Key**

## 2. Environment Variables

### Frontend (.env.local or environment)
```bash
# reCAPTCHA Site Key (public key)
NEXT_PUBLIC_RECAPTCHA_SITE_KEY=6LcxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxXX
```

### Backend (.env or environment)
```bash
# reCAPTCHA Secret Key (private key)
RECAPTCHA_SECRET_KEY=6LcxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxXX
RECAPTCHA_ENABLED=true
RECAPTCHA_MIN_SCORE=0.5
```

## 3. Configuration Options

### reCAPTCHA Settings

- **RECAPTCHA_ENABLED**: Set to `false` to disable reCAPTCHA verification (useful for development)
- **RECAPTCHA_MIN_SCORE**: Minimum score required (0.0 = bot, 1.0 = human). Default: 0.5
  - `0.9+`: Very likely human
  - `0.7-0.8`: Likely human
  - `0.5-0.6`: Neutral
  - `0.3-0.4`: Suspicious
  - `0.0-0.2`: Very likely bot

### Score Recommendations by Action

- **Login**: 0.5 (moderate security)
- **Signup**: 0.6 (higher security for new accounts)
- **Password Reset**: 0.4 (lower threshold for legitimate users who may be stressed)
- **Contact Forms**: 0.7 (higher security for spam prevention)

## 4. Testing

### Development
- Use test keys provided by Google for development:
  - Site Key: `6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI`
  - Secret Key: `6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe`
- These keys always return success

### Production
- Use your actual keys from the reCAPTCHA console
- Monitor the reCAPTCHA admin dashboard for analytics

## 5. Integration Points

The reCAPTCHA integration is added to the following forms:

1. **Login Form** (`/login`)
   - Action: `login`
   - Triggers on form submission

2. **Signup Form** (`/signup`)
   - Action: `signup`
   - Triggers on form submission

3. **Forgot Password Form** (`/login` - forgot password flow)
   - Action: `forgot_password`
   - Triggers on email submission

4. **Reset Password Form** (`/reset-password`)
   - Action: `reset_password`
   - Triggers on password reset submission

## 6. Error Handling

If reCAPTCHA verification fails, users will see:
- "Security verification failed. Please try again."
- The form will remain functional but the submission will be blocked

## 7. Fallback Behavior

- If reCAPTCHA is not configured (no keys), the system will work without verification
- If reCAPTCHA service is unavailable, forms will still work (graceful degradation)
- Users will see "Loading security verification..." while reCAPTCHA loads

## 8. Troubleshooting

### Common Issues

1. **"reCAPTCHA not loaded" warnings**
   - Check that `NEXT_PUBLIC_RECAPTCHA_SITE_KEY` is set
   - Verify the site key is correct

2. **"reCAPTCHA verification failed" errors**
   - Check that `RECAPTCHA_SECRET_KEY` is set on the backend
   - Verify the secret key is correct
   - Check network connectivity to Google's servers

3. **Domain errors**
   - Ensure your domain is added to the reCAPTCHA console
   - For development, add `localhost` and `127.0.0.1`

### Debug Mode

Enable debug logging in Django settings:
```python
LOGGING = {
    'loggers': {
        'authentication': {
            'level': 'DEBUG',
        },
    },
}
```

This will log reCAPTCHA verification attempts and results.

## 9. Security Considerations

- Never expose the secret key in frontend code
- Use environment variables for all keys
- Monitor reCAPTCHA analytics for suspicious activity
- Consider implementing rate limiting as an additional security layer
- Regularly review and update minimum score thresholds based on your traffic patterns
