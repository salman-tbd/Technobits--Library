# 💳 Stripe Payment Gateway

A complete, production-ready Stripe payment integration with Django backend and Next.js frontend.

## 🚀 Features

- ✅ **Stripe Payment Intent** - Secure payment processing
- ✅ **Stripe Checkout** - Hosted checkout experience  
- ✅ **Transaction Management** - Admin panel for payments
- ✅ **Success/Cancel Pages** - Complete payment flow
- ✅ **Production Ready** - Security headers, HTTPS support
- ✅ **Clean UI** - Modern, responsive design with Tailwind CSS
- ✅ **TypeScript** - Full type safety

## 🏗️ Architecture

```
├── backend/          # Django REST API
│   ├── payments/     # Payment models, views, admin
│   └── stripe_gateway/ # Django settings
└── frontend/         # Next.js React app
    ├── src/app/      # App router pages
    ├── src/components/ # Reusable components
    └── src/lib/      # API client, utilities
```

## 🔧 Quick Setup

### Backend (Django)
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
```

### Environment Variables
```env
# Backend
STRIPE_SECRET_KEY=sk_test_your_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here

# Frontend
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
```

## 🌐 API Endpoints

- `POST /api/create-payment-intent/` - Create Payment Intent
- `POST /api/create-checkout-session/` - Create Checkout Session
- `GET /api/session-status/` - Get session status
- `GET /api/` - List transactions
- `GET /api/stats/` - Payment statistics

## 🔒 Production Deployment

**Ready to go live?** See the comprehensive **[PRODUCTION_GUIDE.md](./PRODUCTION_GUIDE.md)** for:

- ✅ Live Stripe keys configuration
- ✅ Security settings checklist
- ✅ HTTPS deployment guide
- ✅ Webhook setup instructions
- ✅ Complete pre-launch checklist

**Critical for production:**
1. Replace test keys with live Stripe keys
2. Set `DEBUG=False` 
3. Deploy to HTTPS domain
4. Configure live webhooks

## 🧪 Testing

### Test Cards (Development)
- **Success**: `4242 4242 4242 4242`
- **Decline**: `4000 0000 0000 0002`
- **Any future date, CVC, ZIP**

## 📱 Screenshots

- Clean payment form with amount/description inputs
- Secure Stripe Checkout hosted page
- Success page with payment confirmation
- Admin panel for transaction management

## 🛠️ Tech Stack

**Backend:**
- Django 5.0+ with REST Framework
- Stripe Python SDK
- SQLite (dev) / PostgreSQL (prod)

**Frontend:**
- Next.js 14+ with App Router
- TypeScript for type safety
- Tailwind CSS for styling
- Stripe.js for payment processing

## 📄 License

MIT License - feel free to use in your projects!

## 🆘 Support

- 📖 Check [PRODUCTION_GUIDE.md](./PRODUCTION_GUIDE.md) for deployment help
- 🔗 [Stripe Documentation](https://stripe.com/docs)
- 🐛 Open an issue for bugs or questions

---

**⭐ Star this repo if it helped you build your payment system!**
