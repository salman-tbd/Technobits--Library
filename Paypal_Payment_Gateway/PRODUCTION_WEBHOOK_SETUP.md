# Production Webhook Setup Guide

## When deploying to production, follow these steps to enable PayPal webhooks:

### 1. Deploy Your Django App
Deploy to any cloud platform:
- **Heroku:** `https://yourapp.herokuapp.com`
- **DigitalOcean:** `https://yourdomain.com`
- **AWS/Railway/Render:** `https://yourapp.platform.com`

### 2. Update PayPal Developer Dashboard
1. **Log in:** https://developer.paypal.com/
2. **Go to:** My Apps & Credentials → Your App → Webhooks
3. **Add/Update Webhook URL:** `https://yourdomain.com/api/paypal/webhook/`
4. **Select Event Types:**
   - `PAYMENT.CAPTURE.COMPLETED`
   - `PAYMENT.CAPTURE.DENIED`
   - `PAYMENT.CAPTURE.PENDING`
   - `PAYMENT.CAPTURE.REFUNDED`
   - `PAYMENT.CAPTURE.REVERSED`

### 3. Environment Variables
Ensure these are set in production:
```bash
PAYPAL_CLIENT_ID=your_production_client_id
PAYPAL_SECRET_KEY=your_production_secret_key
PAYPAL_BASE_URL=https://api-m.paypal.com  # Production URL (not sandbox)
PAYPAL_WEBHOOK_ID=your_webhook_id  # Optional, for signature verification
```

### 4. Test Production Webhooks
1. **Process a real payment** through your deployed app
2. **Check Django Admin:** `https://yourdomain.com/admin/payments/paypalwebhookevent/`
3. **Verify webhook events** are being received and processed

### 5. Monitor Webhooks
- **PayPal Dashboard:** Monitor webhook delivery status
- **Django Logs:** Check for any processing errors
- **Database:** Verify transaction status updates

## Benefits in Production:
✅ **Real-time payment status updates**
✅ **Automatic transaction completion**
✅ **Payment failure handling**
✅ **Audit trail of all payment events**
✅ **Better user experience with instant confirmations**

## Current Status:
- 🟡 **Local Development:** Webhooks not accessible (expected)
- 🟢 **Production Ready:** All webhook code is implemented and tested
