# Google Sign-In/Sign-Up Authentication & Payment System

A comprehensive, production-ready authentication and payment processing system built with **Next.js 14** (TypeScript) frontend and **Django 5.0** REST API backend. Features secure JWT authentication, Google OAuth integration, unified payment processing (Google Pay & PayPal), payment analytics, email services, and modern UI components.

## ✨ Key Features

🔐 **Multi-Authentication Support**
- Email/password registration and login with validation
- Google Sign-In integration with server-side verification
- Password reset functionality with email notifications

💳 **Unified Payment Processing**
- Google Pay integration with secure token processing
- PayPal integration with order management and webhooks
- Unified transaction management across all payment providers
- Real-time payment analytics and reporting
- Transaction history and status tracking
- Secure payment method storage (optional)

🛡️ **Production-Grade Security**
- JWT tokens stored in HTTP-only cookies (XSS protection)
- Google reCAPTCHA v3 integration for bot protection
- Automatic token refresh for seamless user experience
- CORS/CSRF protection configured for deployment
- Server-side Google credential verification
- Secure payment token handling and validation

🎨 **Modern User Interface**
- Responsive design with Tailwind CSS
- Form validation with React Hook Form + Zod
- Loading states and error handling
- Clean, professional authentication flows
- Interactive payment interfaces with real-time feedback
- Payment analytics dashboard with charts and insights
- Progressive landing page with enhanced UX

📧 **Email Integration**
- Welcome emails for new users
- Password reset email notifications
- Payment confirmation emails
- SendinBlue API integration

🔧 **Developer Experience**
- Full TypeScript support throughout
- Single-command development workflow
- Comprehensive error handling and debugging
- Well-documented API endpoints
- Payment provider abstraction layer
- Analytics hooks and utilities

## 🚀 Quick Start

### Prerequisites

- **Node.js 18+** and **npm** (see `.nvmrc` for exact version)
- **Python 3.11+** with **pip**
- **Docker Desktop** (for containerized deployment)
- **Google Cloud Console account** (for Google OAuth setup)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd Google-SignIn-SignUp
   ```

2. **Install dependencies using root scripts:**
   ```bash
   # Install frontend dependencies
   npm run install:frontend
   
   # Install backend dependencies (creates virtual environment)
   npm run install:backend
   ```
   
   Or install manually:
   ```bash
   # Frontend
   cd apps/frontend && npm install && cd ../..
   
   # Backend
   cd apps/backend && python -m venv .venv && .venv/Scripts/pip install -r requirements.txt && cd ../..
   ```

3. **Configure environment variables:**
   
   **Frontend** (`apps/frontend/.env.local`):
   ```env
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8007
   NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
   NEXT_PUBLIC_RECAPTCHA_SITE_KEY=your-recaptcha-site-key
   ```

   **Backend** (`apps/backend/.env`):
   ```env
   # Core Django Settings
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   
   # Authentication & Security
   GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
   RECAPTCHA_SECRET_KEY=your-recaptcha-secret-key
   RECAPTCHA_ENABLED=true
   RECAPTCHA_MIN_SCORE=0.5
   
   # CORS/CSRF Settings
   CORS_ALLOWED_ORIGINS=http://localhost:3007
   CSRF_TRUSTED_ORIGINS=http://localhost:3007
   
   # Email Service
   SENDINBLUE_API_KEY=your-sendinblue-api-key-optional
   
   # Payment Settings
   GOOGLE_PAY_MERCHANT_ID=your-google-pay-merchant-id
   PAYPAL_CLIENT_ID=your-paypal-client-id
   PAYPAL_CLIENT_SECRET=your-paypal-client-secret
   PAYPAL_MODE=sandbox  # or 'live' for production
   
   # JWT Token Settings
   JWT_ACCESS_TOKEN_LIFETIME_MINUTES=15
   JWT_REFRESH_TOKEN_LIFETIME_DAYS=7
   ```

   > **Note**: The default ports are `3007` for frontend and `8007` for backend to avoid conflicts.

4. **Set up the database:**
   ```bash
   npm run migrate
   ```
   
   Or manually:
   ```bash
   cd apps/backend && .venv/Scripts/python manage.py migrate && cd ../..
   ```

5. **Start the development servers:**
   
   **Option 1: Use root scripts (recommended)**
   ```bash
   # Backend (Terminal 1)
   npm run dev:backend
   
   # Frontend (Terminal 2) 
   npm run dev:frontend
   
   # Or both simultaneously
   npm run dev
   ```
   
   **Option 2: Manual startup**
   ```bash
   # Backend (Terminal 1)
   cd apps/backend && .venv/Scripts/python manage.py runserver 8007
   
   # Frontend (Terminal 2)
   cd apps/frontend && npm run dev
   ```

6. **Visit the application:**
   - **Frontend**: http://localhost:3007
   - **Backend API**: http://localhost:8007
   - **API Health Check**: http://localhost:8007/auth/health/
   - **Payment Demo**: http://localhost:3007/demos
   - **Analytics Dashboard**: http://localhost:3007/analytics

### 🐳 Docker Quick Start (Alternative)

For a containerized setup with Docker:

1. **Clone and setup:**
   ```bash
   git clone <your-repo-url>
   cd Google-SignIn-SignUp
   ```

2. **Create environment file:**
   ```bash
   # Create .env file in root directory
   echo "GOOGLE_CLIENT_ID=your-google-client-id" > .env
   echo "SENDINBLUE_API_KEY=your-api-key-optional" >> .env
   ```

3. **Start with Docker:**
   ```bash
   # Production mode
   docker-compose up --build
   
   # Development mode (with hot reloading)
   docker-compose -f docker-compose.dev.yml up --build
   
   # Using helper script (Windows)
   docker-helper.bat start
   
   # Using helper script (Linux/Mac)
   ./docker-helper.sh start
   ```

4. **Access the application:**
   - **Frontend**: http://localhost:3007
   - **Backend API**: http://localhost:8007

📚 **Complete Docker Guide**: See [docs/docker-setup.md](docs/docker-setup.md) for detailed Docker instructions, troubleshooting, and production deployment.

## 📁 Project Structure

```
Google-SignIn-SignUp/
├── apps/
│   ├── frontend/                    # Next.js 14 + TypeScript frontend
│   │   ├── src/
│   │   │   ├── app/                 # Next.js App Router pages
│   │   │   │   ├── page.tsx         # Home page with auth status
│   │   │   │   ├── login/page.tsx   # Login with email/Google
│   │   │   │   ├── signup/page.tsx  # Registration page
│   │   │   │   ├── reset-password/  # Password reset flow
│   │   │   │   ├── dashboard/       # User dashboard
│   │   │   │   ├── analytics/       # Payment analytics dashboard
│   │   │   │   ├── demos/           # Payment integration demos
│   │   │   │   └── checkout/        # Payment checkout flows
│   │   │   │       ├── google-pay/  # Google Pay checkout
│   │   │   │       └── paypal/      # PayPal checkout
│   │   │   ├── components/          # Reusable UI components
│   │   │   │   ├── LoginForm.tsx    # Email/password form
│   │   │   │   ├── SimpleGoogleButton.tsx  # Google Sign-In
│   │   │   │   ├── enhanced/        # Enhanced UI components
│   │   │   │   │   ├── LandingToggle.tsx    # Landing page toggle
│   │   │   │   │   └── ProgressiveLanding.tsx  # Progressive landing
│   │   │   │   └── payments/        # Payment components
│   │   │   │       ├── GooglePayButton.tsx     # Google Pay integration
│   │   │   │       ├── PayPalButton.tsx        # PayPal integration
│   │   │   │       └── PaymentSuccessModal.tsx # Success modal
│   │   │   ├── contexts/            # React Context providers
│   │   │   │   ├── AuthContext.tsx  # Auth state management
│   │   │   │   ├── NotificationContext.tsx  # Notifications
│   │   │   │   └── RecaptchaContext.tsx     # reCAPTCHA provider
│   │   │   ├── hooks/               # Custom React hooks
│   │   │   │   └── usePaymentAnalytics.ts   # Payment analytics
│   │   │   └── lib/                 # Utilities and API client
│   │   │       ├── api.ts           # Type-safe API client
│   │   │       ├── types.ts         # TypeScript definitions
│   │   │       └── validation.ts    # Zod form schemas
│   │   ├── package.json             # Frontend dependencies
│   │   └── tailwind.config.js       # Tailwind CSS config
│   │
│   └── backend/                     # Django 5.0 REST API backend
│       ├── authentication/         # Django auth app
│       │   ├── views.py            # Auth API endpoints
│       │   ├── serializers.py      # Data validation
│       │   ├── utils.py            # JWT & Google helpers
│       │   ├── email_service.py    # SendinBlue integration
│       │   ├── recaptcha_utils.py  # reCAPTCHA validation
│       │   └── authentication.py   # Custom JWT auth class
│       ├── payments/               # Payment processing app
│       │   ├── models.py           # Payment transaction models
│       │   ├── views.py            # Payment API endpoints
│       │   ├── services.py         # Payment service layer
│       │   ├── serializers.py      # Payment data validation
│       │   └── urls.py             # Payment URL patterns
│       ├── backend/                # Django project config
│       │   ├── settings.py         # Comprehensive settings
│       │   └── urls.py             # URL configuration
│       ├── manage.py               # Django management
│       └── requirements.txt        # Python dependencies
│
├── docs/                           # Documentation
│   ├── folder-structure.md         # Detailed project structure
│   ├── google-oauth-setup.md       # Google OAuth setup guide
│   ├── recaptcha-setup.md          # reCAPTCHA setup guide
│   └── docker-setup.md            # Complete Docker guide
├── docker-compose.yml              # Production Docker setup
├── docker-compose.dev.yml          # Development Docker setup
├── docker-helper.bat               # Windows Docker helper script
├── docker-helper.sh                # Unix Docker helper script
├── .nvmrc                          # Node.js version specification
├── package.json                    # Root development scripts
└── README.md                       # This file
```

## 🛠️ Technology Stack

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety throughout
- **Tailwind CSS** - Utility-first styling
- **React Hook Form** - Form handling with validation
- **Zod** - Schema validation and type inference
- **Framer Motion** - Animations and transitions
- **Recharts** - Data visualization for analytics
- **Lottie React** - Animated graphics and icons
- **React Hot Toast** - Notification system

### Backend
- **Django 5.0** - Python web framework
- **Django REST Framework** - API development
- **SimpleJWT** - JWT token authentication
- **Google Auth Library** - Google OAuth verification
- **SendinBlue API** - Email service integration
- **SQLite** - Database (easily configurable for PostgreSQL/MySQL)

### Payment Processing
- **Google Pay API** - Secure payment processing with tokenization
- **PayPal REST API** - Order creation, capture, and webhook handling
- **Unified Payment Models** - Provider-agnostic transaction management
- **Payment Analytics** - Real-time transaction reporting and insights

## 🛠️ Available Scripts

The root `package.json` provides convenient scripts for managing both applications:

```bash
# Development
npm run dev                   # Start both frontend and backend simultaneously
npm run dev:frontend          # Start Next.js dev server (port 3007)
npm run dev:backend           # Start Django dev server (port 8007)

# Installation
npm run install:frontend      # Install frontend dependencies
npm run install:backend       # Install backend dependencies + create venv
npm run setup:backend         # Full backend setup (venv + deps + migrations)

# Database
npm run migrate               # Run Django database migrations
npm run createsuperuser       # Create Django admin user

# Build
npm run build:frontend        # Build frontend for production
```

> **Why Root Scripts?** The root `package.json` acts as a development orchestration layer, providing a unified interface for managing both frontend and backend applications. This enables single-command workflows while maintaining clean separation between the applications.

## 🔌 API Endpoints

The Django backend provides comprehensive REST APIs for authentication and payment processing:

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register/` | Register with email/password | ❌ |
| POST | `/auth/login/` | Login with email/password | ❌ |
| POST | `/auth/google/` | Login/register with Google credential | ❌ |
| GET | `/auth/me/` | Get current user information | ✅ |
| POST | `/auth/logout/` | Logout and clear JWT cookies | ✅ |
| POST | `/auth/refresh/` | Refresh JWT access token | ❌ |
| POST | `/auth/forgot-password/` | Request password reset email | ❌ |
| POST | `/auth/reset-password/` | Reset password with token | ❌ |
| GET | `/auth/health/` | API health check | ❌ |

### Payment Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/payments/google-pay/process/` | Process Google Pay payment | ✅ |
| POST | `/payments/paypal/create-order/` | Create PayPal order | ✅ |
| POST | `/payments/paypal/capture-order/` | Capture PayPal order | ✅ |
| POST | `/payments/paypal/webhook/` | PayPal webhook handler | ❌ |
| GET | `/payments/transactions/` | List user transactions | ✅ |
| GET | `/payments/transactions/<id>/` | Get transaction details | ✅ |
| GET | `/payments/analytics/` | Get payment analytics data | ✅ |

### Request/Response Examples

**Register User**
```bash
POST /auth/register/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "name": "John Doe"
}
```

**Google Login**
```bash
POST /auth/google/
Content-Type: application/json

{
  "credential": "google-jwt-credential-from-frontend"
}
```

**Google Pay Payment**
```bash
POST /payments/google-pay/process/
Content-Type: application/json
Authorization: Bearer <access-token>

{
  "payment_token": "google-pay-payment-token",
  "amount": "29.99",
  "currency": "USD",
  "description": "Premium subscription"
}
```

**PayPal Create Order**
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

## 🌐 Google OAuth Setup

1. **Create Google Cloud Project**: Go to [Google Cloud Console](https://console.cloud.google.com/)
2. **Enable Google+ API**: In APIs & Services > Library
3. **Create OAuth 2.0 Credentials**: In APIs & Services > Credentials
4. **Configure OAuth Consent Screen**: Add app name, support email, etc.
5. **Add Authorized Origins**:
   - `http://localhost:3007` (development)
   - `https://yourdomain.com` (production)
6. **Copy Client ID**: Use the same ID for both frontend and backend environment variables

📚 **Detailed Setup Guide**: See [docs/google-oauth-setup.md](docs/google-oauth-setup.md) for complete step-by-step instructions with screenshots.

## 🛡️ reCAPTCHA v3 Setup

1. **Create reCAPTCHA Site**: Go to [Google reCAPTCHA Console](https://www.google.com/recaptcha/admin)
2. **Choose reCAPTCHA v3**: Select "reCAPTCHA v3" for invisible protection
3. **Add Domains**:
   - Development: `localhost`, `127.0.0.1`
   - Production: your actual domain
4. **Copy Keys**: Use Site Key for frontend, Secret Key for backend
5. **Configure Environment Variables**: Add keys to your `.env` files

📚 **Complete reCAPTCHA Guide**: See [docs/recaptcha-setup.md](docs/recaptcha-setup.md) for detailed setup instructions, configuration options, and troubleshooting.

## 💳 Payment Provider Setup

### Google Pay Setup

1. **Create Google Pay Business Console Account**: Go to [Google Pay Business Console](https://pay.google.com/business/console)
2. **Enable Google Pay API**: In your Google Cloud Console project
3. **Configure Payment Methods**: Set up accepted payment methods
4. **Get Merchant ID**: Copy your Google Pay Merchant ID
5. **Configure Environment Variables**:
   ```env
   # Frontend
   NEXT_PUBLIC_GOOGLE_PAY_MERCHANT_ID=your-merchant-id
   
   # Backend
   GOOGLE_PAY_MERCHANT_ID=your-merchant-id
   ```

### PayPal Setup

1. **Create PayPal Developer Account**: Go to [PayPal Developer](https://developer.paypal.com/)
2. **Create Application**: In your PayPal developer dashboard
3. **Get API Credentials**: Copy Client ID and Client Secret
4. **Configure Webhooks**: Set up webhook endpoint for payment notifications
5. **Configure Environment Variables**:
   ```env
   # Backend
   PAYPAL_CLIENT_ID=your-paypal-client-id
   PAYPAL_CLIENT_SECRET=your-paypal-client-secret
   PAYPAL_MODE=sandbox  # Use 'live' for production
   ```

### Payment Testing

- **Google Pay**: Use test cards provided in Google Pay documentation
- **PayPal**: Use PayPal sandbox accounts for testing
- **Demo Page**: Visit `/demos` to test payment integrations
- **Analytics**: View transaction data in `/analytics` dashboard

## 🚀 Deployment

### Frontend (Next.js)

**Vercel Deployment:**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy from apps/frontend directory
cd apps/frontend
vercel --prod
```

**Environment Variables for Production:**
```env
NEXT_PUBLIC_API_BASE_URL=https://your-api-domain.com
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
NEXT_PUBLIC_RECAPTCHA_SITE_KEY=your-recaptcha-site-key
NEXT_PUBLIC_GOOGLE_PAY_MERCHANT_ID=your-google-pay-merchant-id
```

### Backend (Django)

**Production Environment Variables:**
```env
# Security
SECRET_KEY=your-production-secret-key-min-50-chars
DEBUG=False
ALLOWED_HOSTS=your-api-domain.com,your-frontend-domain.com

# reCAPTCHA
RECAPTCHA_SECRET_KEY=your-recaptcha-secret-key
RECAPTCHA_ENABLED=true
RECAPTCHA_MIN_SCORE=0.5

# CORS/CSRF
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
CSRF_TRUSTED_ORIGINS=https://your-frontend-domain.com
CORS_ALLOW_ALL_ORIGINS=False

# Cookies (HTTPS only)
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# JWT Token Lifetimes
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=15
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# Email Service
SENDINBLUE_API_KEY=your-sendinblue-api-key

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com

# Payment Processing
GOOGLE_PAY_MERCHANT_ID=your-google-pay-merchant-id
PAYPAL_CLIENT_ID=your-paypal-client-id
PAYPAL_CLIENT_SECRET=your-paypal-client-secret
PAYPAL_MODE=live
```

**Database Configuration:**
For production, update `DATABASES` in `settings.py` to use PostgreSQL or MySQL instead of SQLite.

## 🔒 Security Features

### 🛡️ Authentication Security
- **JWT in HTTP-only Cookies**: Tokens stored securely, protected from XSS attacks
- **Automatic Token Refresh**: 15-minute access tokens with 7-day refresh tokens
- **Token Blacklisting**: Refresh tokens are blacklisted on logout
- **Server-side Google Verification**: Google credentials validated on backend

### 🌐 Web Security
- **CORS Protection**: Configurable allowed origins for cross-domain requests
- **CSRF Protection**: Compatible with modern SPA applications
- **Secure Cookies**: HTTP-only, SameSite, and Secure flags for production
- **Input Validation**: Comprehensive validation on both frontend (Zod) and backend (DRF serializers)

### 🔐 Password Security
- **Django Password Validators**: Minimum length, complexity, and common password checks
- **Secure Password Reset**: Token-based reset with email verification
- **Password Hashing**: Django's built-in PBKDF2 password hashing

## 🆘 Troubleshooting

### Common Issues

**🔍 Google Authentication Issues**
```bash
# Check environment variables are set
# Frontend: NEXT_PUBLIC_GOOGLE_CLIENT_ID
# Backend: GOOGLE_CLIENT_ID

# Restart both servers after adding environment variables
npm run dev:backend
npm run dev:frontend
```

**🌐 CORS/Network Errors**
```bash
# Verify backend CORS settings in apps/backend/.env
CORS_ALLOWED_ORIGINS=http://localhost:3007
CSRF_TRUSTED_ORIGINS=http://localhost:3007

# Check frontend API URL in apps/frontend/.env.local
NEXT_PUBLIC_API_BASE_URL=http://localhost:8007
```

**💾 Database Issues**
```bash
# Apply migrations
npm run migrate

# Reset database if needed
cd apps/backend
rm db.sqlite3
.venv/Scripts/python manage.py migrate
```

**📧 Email Service Issues**
```bash
# SendinBlue API key is optional for development
# Password reset emails will print to console if SendinBlue fails
# Check backend logs for email delivery status
```

### Debug Mode

**Frontend Debug Logging**
The frontend includes environment debug logging in the browser console. Check for:
- API Base URL configuration
- Google Client ID presence and length
- Network request/response details

**Backend Debug Logging**
Django logging is configured for the authentication app. Check terminal output for:
- Authentication attempts
- Google credential verification
- Email sending status
- JWT token operations

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📚 Documentation

- **[Project Structure](docs/folder-structure.md)** - Detailed explanation of the codebase organization
- **[Google OAuth Setup](docs/google-oauth-setup.md)** - Complete guide for configuring Google authentication
- **[reCAPTCHA Setup](docs/recaptcha-setup.md)** - Complete guide for configuring reCAPTCHA protection
- **[Payment Integration](docs/payment-setup.md)** - Complete guide for Google Pay and PayPal integration
- **[Docker Setup](docs/docker-setup.md)** - Complete containerization guide with Docker and Docker Compose
- **API Documentation** - Comprehensive REST API reference (see API Endpoints section above)

## 🤝 Contributing

1. **Fork the repository** and clone your fork
2. **Set up development environment** using the Quick Start guide
3. **Create a feature branch**: `git checkout -b feature/amazing-feature`
4. **Make your changes** with proper TypeScript types and tests
5. **Test thoroughly** on both frontend and backend
6. **Submit a pull request** with a clear description

### Development Guidelines

- **TypeScript**: Maintain type safety throughout the codebase
- **Code Style**: Follow existing patterns and use Prettier for formatting
- **Security**: Follow security best practices for authentication systems
- **Testing**: Add tests for new features and bug fixes
- **Documentation**: Update documentation for any API or configuration changes

## 🏗️ Architecture Decisions

### Why This Stack?

- **Next.js 14**: Modern React framework with excellent TypeScript support and App Router
- **Django 5.0**: Mature, secure web framework with excellent authentication features
- **JWT in Cookies**: Balances security (HTTP-only) with ease of use (automatic inclusion)
- **Monorepo Structure**: Simplified development while maintaining clear separation
- **TypeScript Throughout**: Type safety reduces bugs and improves developer experience

### Key Design Principles

1. **Security First**: All authentication decisions prioritize security over convenience
2. **Developer Experience**: Simple setup and clear documentation
3. **Production Ready**: Configured for real-world deployment scenarios
4. **Type Safety**: Comprehensive TypeScript usage prevents runtime errors
5. **Maintainability**: Clean architecture and separation of concerns

---

**Built with ❤️ using Next.js 14, Django 5.0, TypeScript, and modern web security practices.**