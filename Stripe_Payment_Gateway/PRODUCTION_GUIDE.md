# 🚀 Production Deployment Guide

## Moving from Test Mode to Live Mode

Your Stripe Payment Gateway is **production-ready**! Here's how to deploy it with live Stripe keys.

## 🚨 Quick Start - Critical Changes Only

**Before deploying, ensure these 4 critical items are correct:**

1. **Replace Stripe Keys** with live versions:
   ```env
   STRIPE_SECRET_KEY=sk_live_your_actual_live_key_here
   STRIPE_PUBLISHABLE_KEY=pk_live_your_actual_live_key_here
   ```

2. **Set Production Mode**:
   ```env
   DEBUG=False
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```

3. **Deploy to HTTPS Domain** (required for live payments)

4. **Configure Live Webhooks** in Stripe dashboard for your production domain

**✅ That's it! Your code works identically with live keys.**

---

## 🔑 Step 1: Get Live Stripe Keys

### In Your Stripe Dashboard:
1. **Activate your account** - Complete business verification
2. **Switch to Live mode** (toggle in top-left)
3. **Get your Live API keys**:
   - Go to Developers → API Keys
   - Copy your **Live Publishable Key** (`pk_live_...`)
   - Copy your **Live Secret Key** (`sk_live_...`)

## 🔧 Step 2: Update Environment Variables

### Backend Environment Variables
Create a `.env` file in your backend directory or set environment variables:

```env
# Production Django Settings
SECRET_KEY=your-super-secret-django-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Live Stripe Keys (CRITICAL - Replace these!)
STRIPE_SECRET_KEY=sk_live_your_actual_live_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_live_your_actual_live_publishable_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_live_webhook_secret_here

# Database (for production)
DATABASE_URL=postgres://user:pass@host:port/dbname
```

### Frontend Environment Variables
Create a `.env.local` file in your frontend directory:

```env
# Live Stripe Key (CRITICAL - Replace this!)
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_your_actual_live_publishable_key_here

# Production API URL
NEXT_PUBLIC_API_BASE_URL=https://yourdomain.com/api

# App Configuration
NEXT_PUBLIC_APP_NAME=Your Payment Gateway
NEXT_PUBLIC_APP_URL=https://yourdomain.com
```

## 🌐 Step 3: Deploy to Production

### Backend Deployment Options:
1. **Heroku** - Easy Django deployment
2. **DigitalOcean App Platform** - Simple and affordable
3. **AWS Elastic Beanstalk** - Scalable
4. **Railway** - Modern deployment platform

### Frontend Deployment Options:
1. **Vercel** - Perfect for Next.js (recommended)
2. **Netlify** - Great for static sites
3. **DigitalOcean App Platform** - Full-stack option

### Example Vercel Deployment:
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy frontend
cd frontend
vercel --prod

# Set environment variables in Vercel dashboard
```

## 🔒 Step 4: Security Checklist

### ✅ Required Security Updates:

1. **HTTPS Only** - All payments must use HTTPS
2. **Strong Django Secret Key** - Generate a new one
3. **Debug Mode Off** - Set `DEBUG=False`
4. **Allowed Hosts** - Set specific domains
5. **CORS Settings** - Configure for your domain

Update your backend settings for production:

```python
# settings.py additions for production
SECURE_SSL_REDIRECT = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# CORS settings for production
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]
```

## 📡 Step 5: Configure Webhooks

### Set Up Live Webhooks:
1. Go to Stripe Dashboard → Developers → Webhooks
2. **Add endpoint**: `https://yourdomain.com/api/webhooks/stripe/`
3. **Select events**:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `checkout.session.completed`
   - `invoice.payment_succeeded` (if using subscriptions)

4. **Copy the webhook secret** and add to your environment variables

## 🧪 Step 6: Test Live Mode

### Safe Testing in Live Mode:
1. **Use small amounts** (like $0.50) for initial tests
2. **Test with real cards** (your own cards)
3. **Verify webhooks** are working
4. **Check transaction records** in Stripe dashboard
5. **Test refunds** if needed

### Test Checklist:
- [ ] Payment Intent creation works
- [ ] Checkout Session redirects properly
- [ ] Payments process successfully
- [ ] Success page displays correctly
- [ ] Webhooks receive events
- [ ] Database records are created
- [ ] Admin panel shows transactions

## 💳 Step 7: Business Setup

### Complete These in Stripe:
1. **Business Profile** - Company details, tax info
2. **Banking Details** - Where to receive payouts
3. **Tax Settings** - Configure tax collection if needed
4. **Payout Schedule** - Daily, weekly, or monthly
5. **Statement Descriptors** - What appears on customer statements

## 🚨 Important Differences: Test vs Live

| Feature | Test Mode | Live Mode |
|---------|-----------|-----------|
| **Cards** | Test cards only | Real cards only |
| **Money** | Fake transactions | Real money processed |
| **Webhooks** | Test webhooks | Live webhooks required |
| **Fees** | No fees | Stripe fees apply (2.9% + $0.30) |
| **Disputes** | Simulated | Real customer disputes |
| **Payouts** | Not processed | Real money to your bank |

## 🔍 Monitoring & Maintenance

### Set Up Monitoring:
1. **Stripe Dashboard** - Monitor payments, disputes, failures
2. **Error Logging** - Use Sentry or similar for error tracking
3. **Uptime Monitoring** - Ensure your API is always available
4. **Performance Monitoring** - Track API response times

### Regular Maintenance:
- Monitor failed payments and retry logic
- Keep Stripe SDK updated
- Review and respond to disputes
- Monitor for suspicious activity
- Update webhook endpoints if needed

## 🆘 Troubleshooting Common Issues

### If Payments Fail in Live Mode:
1. **Check API keys** - Ensure you're using live keys
2. **Verify HTTPS** - All requests must be HTTPS
3. **Check webhooks** - Ensure they're configured for live mode
4. **Review logs** - Check both your app and Stripe logs
5. **Test with small amounts** - Start with $0.50 transactions

### If Webhooks Don't Work:
1. **Check endpoint URL** - Must be publicly accessible
2. **Verify webhook secret** - Must match your environment variable
3. **Check HTTPS** - Webhook endpoints must use HTTPS
4. **Review event types** - Ensure you're listening for correct events

## 🔍 Production Configuration Validation

### Critical Settings Check

Before deploying, manually verify these settings:

#### 🔑 Stripe Configuration
- [ ] **STRIPE_SECRET_KEY** starts with `sk_live_` (not `sk_test_`)
- [ ] **STRIPE_PUBLISHABLE_KEY** starts with `pk_live_` (not `pk_test_`)
- [ ] **STRIPE_WEBHOOK_SECRET** is set for live webhooks
- [ ] Keys are properly set in environment variables (not hardcoded)

#### ⚙️ Django Settings
- [ ] **DEBUG = False** (never True in production)
- [ ] **SECRET_KEY** is not the default/demo key
- [ ] **ALLOWED_HOSTS** contains your production domain(s)
- [ ] **SECURE_SSL_REDIRECT = True** for HTTPS enforcement
- [ ] **SESSION_COOKIE_SECURE = True**
- [ ] **CSRF_COOKIE_SECURE = True**

#### 🌐 Domain & URLs
- [ ] **HTTPS enabled** on production domain
- [ ] **Frontend URLs** updated to production domain
- [ ] **CORS settings** configured for production domain
- [ ] **Success/Cancel URLs** point to live domain

#### 🗄️ Database & Infrastructure
- [ ] **Production database** configured (not SQLite for high traffic)
- [ ] **Database backups** enabled
- [ ] **Static files** properly served
- [ ] **Error logging** configured (Sentry, etc.)

### Quick Validation Commands

```bash
# Check Django settings
python manage.py check --deploy

# Verify environment variables are loaded
python -c "from django.conf import settings; print('DEBUG:', settings.DEBUG); print('STRIPE_SECRET_KEY starts with:', settings.STRIPE_SECRET_KEY[:7])"

# Test database connection
python manage.py dbshell --version

# Collect static files
python manage.py collectstatic --dry-run
```

## 📋 Complete Pre-Launch Checklist

### Phase 1: Configuration
- [ ] All test payments working perfectly in development
- [ ] Live Stripe keys obtained from Stripe dashboard
- [ ] Environment variables updated with live keys
- [ ] Django settings configured for production
- [ ] HTTPS enabled on all domains
- [ ] Database properly configured

### Phase 2: Deployment
- [ ] Code deployed to production server
- [ ] Environment variables set on production
- [ ] Database migrations run successfully
- [ ] Static files collected and served
- [ ] Admin panel accessible with superuser account

### Phase 3: Stripe Setup
- [ ] Stripe account activated (business verification complete)
- [ ] Live mode enabled in Stripe dashboard
- [ ] Webhooks configured for production domain
- [ ] Webhook endpoints tested and responding
- [ ] Business details completed in Stripe

### Phase 4: Testing
- [ ] Small test payments ($0.50) successful
- [ ] Payment success page working
- [ ] Payment cancel/failure page working
- [ ] Webhook events being received
- [ ] Admin panel showing transactions
- [ ] Error handling tested

### Phase 5: Monitoring
- [ ] Error logging/monitoring set up
- [ ] Uptime monitoring configured
- [ ] Stripe dashboard notifications enabled
- [ ] Customer support process ready
- [ ] Backup and recovery plan in place

## 🎉 You're Ready for Production!

Your code is **production-ready**. The main changes are:
1. **Environment variables** (Stripe keys, domain URLs)
2. **HTTPS deployment**
3. **Webhook configuration**

The payment flow, error handling, and user experience remain exactly the same!

---

**Need Help?** 
- Check Stripe's [Go-Live Checklist](https://stripe.com/docs/development/checklist)
- Review their [Production Best Practices](https://stripe.com/docs/development/best-practices)
- Test thoroughly with small amounts first
