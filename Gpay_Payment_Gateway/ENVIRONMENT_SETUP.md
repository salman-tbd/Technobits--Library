# Environment Setup Guide

## Frontend Environment Variables (.env.local)

Create a `.env.local` file in the `frontend` directory:

```env
# Google Pay Configuration
NEXT_PUBLIC_GOOGLE_PAY_MERCHANT_ID=your_actual_merchant_id_here
NEXT_PUBLIC_GOOGLE_PAY_ENVIRONMENT=TEST
NEXT_PUBLIC_GOOGLE_PAY_MERCHANT_NAME=Your Business Name
```

## Backend Environment Variables (.env)

Create a `.env` file in the `backend` directory:

```env
# Django Settings
SECRET_KEY=django-insecure-your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Google Pay
GOOGLE_PAY_MERCHANT_ID=your_actual_merchant_id_here
```

## Getting Google Pay Merchant ID

1. Go to [Google Pay Business Console](https://pay.google.com/business/console)
2. Create a new project or select existing one
3. Get your merchant ID from the console
4. For development, you can use `TEST` environment
5. For production, change environment to `PRODUCTION`

## Important Notes

- **Never commit .env files to version control**
- Use different merchant IDs for development and production
- Test with small amounts initially
- The current implementation logs payments but doesn't process them with external gateways
- For production, you'll need to integrate with your preferred payment processor

## Testing

The current setup:
- Receives Google Pay tokens from the frontend
- Logs payment information
- Returns success responses for testing
- No actual payment processing occurs