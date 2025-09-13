# Payment Integration Setup Guide

This guide explains how to set up and configure the payment processing features in the Google SignIn/SignUp Authentication & Payment System.

## Overview

The system supports unified payment processing through multiple providers:
- **Google Pay** - Secure tokenized payments
- **PayPal** - Order-based payment processing
- **Unified Analytics** - Cross-provider transaction reporting

## Payment Architecture

### Backend Components
- **Payment Models** (`payments/models.py`) - Unified transaction storage
- **Payment Services** (`payments/services.py`) - Provider abstraction layer
- **Payment Views** (`payments/views.py`) - REST API endpoints
- **Webhook Handlers** - Real-time payment notifications

### Frontend Components
- **Payment Components** (`components/payments/`) - UI integration
- **Checkout Pages** (`app/checkout/`) - Payment flows
- **Analytics Dashboard** (`app/analytics/`) - Transaction reporting
- **Demo Page** (`app/demos/`) - Integration examples

## Google Pay Setup

### 1. Google Pay Business Console

1. **Create Business Profile**:
   - Go to [Google Pay Business Console](https://pay.google.com/business/console)
   - Complete business verification process
   - Set up payment methods and processing

2. **Enable Google Pay API**:
   - In [Google Cloud Console](https://console.cloud.google.com/)
   - Enable "Google Pay API" in APIs & Services
   - Create credentials if needed

### 2. Configuration

**Environment Variables**:
```env
# Backend (.env)
GOOGLE_PAY_MERCHANT_ID=your_merchant_id_here

# Frontend (.env.local)
NEXT_PUBLIC_GOOGLE_PAY_MERCHANT_ID=your_merchant_id_here
```

**Payment Request Configuration**:
```javascript
// Frontend configuration in GooglePayButton.tsx
const paymentRequest = {
  apiVersion: 2,
  apiVersionMinor: 0,
  allowedPaymentMethods: [{
    type: 'CARD',
    parameters: {
      allowedAuthMethods: ['PAN_ONLY', 'CRYPTOGRAM_3DS'],
      allowedCardNetworks: ['MASTERCARD', 'VISA']
    },
    tokenizationSpecification: {
      type: 'PAYMENT_GATEWAY',
      parameters: {
        gateway: 'example',
        gatewayMerchantId: 'exampleGatewayMerchantId'
      }
    }
  }]
};
```

### 3. Testing

**Test Cards**:
- Use Google Pay test environment
- Test cards are provided in Google Pay documentation
- Verify tokenization and payment processing

## PayPal Setup

### 1. PayPal Developer Account

1. **Create Developer Account**:
   - Go to [PayPal Developer](https://developer.paypal.com/)
   - Sign up or log in with existing PayPal account

2. **Create Application**:
   - Navigate to "My Apps & Credentials"
   - Create new app for your integration
   - Select appropriate features (Orders, Payments)

### 2. Configuration

**Environment Variables**:
```env
# Backend (.env)
PAYPAL_CLIENT_ID=your_client_id_here
PAYPAL_CLIENT_SECRET=your_client_secret_here
PAYPAL_MODE=sandbox  # Use 'live' for production
```

**Webhook Configuration**:
```env
# PayPal webhook endpoint (configure in PayPal dashboard)
https://your-domain.com/payments/paypal/webhook/
```

### 3. Webhook Events

Configure these webhook events in PayPal dashboard:
- `PAYMENT.CAPTURE.COMPLETED`
- `PAYMENT.CAPTURE.DENIED`
- `CHECKOUT.ORDER.APPROVED`
- `CHECKOUT.ORDER.COMPLETED`

### 4. Testing

**Sandbox Testing**:
- Use PayPal sandbox environment
- Create test buyer and seller accounts
- Test order creation, approval, and capture flow

## Database Setup

### Run Migrations

```bash
# Apply payment-related migrations
python manage.py migrate payments

# Or using npm scripts
npm run migrate
```

### Payment Models

The system creates these database tables:
- `payments_paymenttransaction` - Unified transaction storage
- `payments_paymentwebhook` - Webhook event logging
- `payments_paymentmethod` - Stored payment methods (optional)

## API Endpoints

### Google Pay Processing

```bash
POST /payments/google-pay/process/
Content-Type: application/json
Authorization: Bearer <access-token>

{
  "payment_token": "google_pay_token_here",
  "amount": "29.99",
  "currency": "USD",
  "description": "Premium subscription"
}
```

### PayPal Order Management

**Create Order**:
```bash
POST /payments/paypal/create-order/
Content-Type: application/json
Authorization: Bearer <access-token>

{
  "amount": "29.99",
  "currency": "USD",
  "description": "Premium subscription"
}
```

**Capture Order**:
```bash
POST /payments/paypal/capture-order/
Content-Type: application/json
Authorization: Bearer <access-token>

{
  "order_id": "paypal_order_id_here"
}
```

### Transaction Management

**List Transactions**:
```bash
GET /payments/transactions/
Authorization: Bearer <access-token>
```

**Get Transaction Details**:
```bash
GET /payments/transactions/{transaction_id}/
Authorization: Bearer <access-token>
```

**Payment Analytics**:
```bash
GET /payments/analytics/
Authorization: Bearer <access-token>
```

## Frontend Integration

### Payment Components

**Google Pay Button**:
```tsx
import { GooglePayButton } from '@/components/payments/GooglePayButton';

<GooglePayButton
  amount="29.99"
  currency="USD"
  onSuccess={(result) => console.log('Payment successful', result)}
  onError={(error) => console.error('Payment failed', error)}
/>
```

**PayPal Button**:
```tsx
import { PayPalButton } from '@/components/payments/PayPalButton';

<PayPalButton
  amount="29.99"
  currency="USD"
  onSuccess={(result) => console.log('Payment successful', result)}
  onError={(error) => console.error('Payment failed', error)}
/>
```

### Checkout Pages

- **Google Pay Checkout**: `/checkout/google-pay`
- **PayPal Checkout**: `/checkout/paypal`
- **Payment Demo**: `/demos`

### Analytics Integration

```tsx
import { usePaymentAnalytics } from '@/hooks/usePaymentAnalytics';

const { analytics, loading, error } = usePaymentAnalytics();
```

## Security Considerations

### Payment Token Security
- Google Pay tokens are validated server-side
- PayPal orders use secure order IDs
- All payment data is encrypted in transit

### Webhook Security
- PayPal webhooks include signature verification
- Webhook events are logged for audit trails
- Failed webhook processing is retried automatically

### Data Protection
- Payment tokens are not stored permanently
- Transaction data follows PCI compliance guidelines
- User payment methods are optionally stored with encryption

## Testing & Development

### Demo Environment

Visit `/demos` to test payment integrations:
- Interactive Google Pay testing
- PayPal sandbox integration
- Transaction flow demonstration
- Error handling examples

### Analytics Dashboard

Visit `/analytics` to view:
- Transaction volume and trends
- Provider performance comparison
- Revenue analytics
- Payment method distribution

### Debug Mode

Enable debug logging in Django settings:
```python
LOGGING = {
    'loggers': {
        'payments': {
            'level': 'DEBUG',
            'handlers': ['console'],
        }
    }
}
```

## Production Deployment

### Environment Configuration

**Production Settings**:
```env
# Switch to live mode
PAYPAL_MODE=live
GOOGLE_PAY_ENVIRONMENT=PRODUCTION

# Use production credentials
PAYPAL_CLIENT_ID=live_client_id
PAYPAL_CLIENT_SECRET=live_client_secret
GOOGLE_PAY_MERCHANT_ID=live_merchant_id
```

### SSL Requirements
- HTTPS is required for production payment processing
- Configure SSL certificates for your domain
- Update CORS/CSRF settings for production URLs

### Monitoring
- Set up payment transaction monitoring
- Configure webhook failure alerts
- Monitor payment success/failure rates

## Troubleshooting

### Common Issues

**Google Pay Not Loading**:
- Verify merchant ID is correct
- Check browser compatibility
- Ensure HTTPS in production

**PayPal Orders Failing**:
- Verify client credentials
- Check webhook configuration
- Review PayPal sandbox vs live mode

**Transaction Not Recording**:
- Check database migrations
- Verify API authentication
- Review server logs for errors

### Debug Tools

**Payment Logs**:
```bash
# View payment-related logs
docker-compose logs backend | grep payments

# Check webhook processing
tail -f webhook_logs/paypal_webhooks.log
```

**Database Inspection**:
```bash
# Access Django shell
python manage.py shell

# Query transactions
from payments.models import PaymentTransaction
PaymentTransaction.objects.all()
```

## Support Resources

- **Google Pay Documentation**: [developers.google.com/pay](https://developers.google.com/pay)
- **PayPal Developer Docs**: [developer.paypal.com](https://developer.paypal.com/)
- **Project Issues**: Create GitHub issues for payment-related problems
- **Security Concerns**: Report security issues privately

---

This payment system provides a robust foundation for processing payments while maintaining security and providing comprehensive analytics. The unified architecture makes it easy to add additional payment providers in the future.
