# Project Structure Documentation

This document explains the comprehensive folder structure of the Google Sign-In/Sign-Up Authentication & Payment System - a production-ready authentication and payment processing solution with React frontend and Django backend.

## 📁 Root Level

```
Google-SignIn-SignUp/
├── .gitignore              # Git ignore rules
├── .nvmrc                  # Node.js version specification
├── LICENSE                 # MIT license
├── README.md               # Main project documentation
├── package.json            # Root development orchestration scripts
├── apps/                   # Frontend and backend applications
└── docs/                   # Documentation
```

## 🚀 Applications (`/apps`)

### Frontend App (`/apps/frontend`)
Next.js 14 application with TypeScript, React Hook Form, and Tailwind CSS.

```
apps/frontend/
├── next.config.js          # Next.js configuration
├── next-env.d.ts           # Next.js TypeScript declarations
├── package.json            # Frontend dependencies and scripts
├── postcss.config.js       # PostCSS configuration for Tailwind
├── tailwind.config.js      # Tailwind CSS configuration
├── tsconfig.json           # TypeScript configuration
├── node_modules/           # Frontend dependencies
└── src/
    ├── app/                # Next.js App Router pages
    │   ├── globals.css     # Global styles and Tailwind imports
    │   ├── layout.tsx      # Root layout with AuthProvider
    │   ├── page.tsx        # Home page with auth status
    │   ├── login/
    │   │   └── page.tsx    # Login page with email/password and Google
    │   ├── signup/
    │   │   └── page.tsx    # Registration page
    │   ├── reset-password/
    │   │   └── page.tsx    # Password reset page
    │   ├── debug-google/   # Google OAuth debugging utilities
    │   └── test-google/    # Google OAuth testing utilities
    ├── components/         # Reusable React components
    │   ├── LoginForm.tsx   # Email/password login form with validation
    │   ├── SignupForm.tsx  # Registration form with validation
    │   ├── ForgotPasswordForm.tsx  # Password reset request form
    │   └── SimpleGoogleButton.tsx # Google Sign-In button component
    ├── contexts/           # React Context providers
    │   └── AuthContext.tsx # Authentication state management
    └── lib/                # Utility libraries
        ├── api.ts          # API client for backend communication
        ├── types.ts        # TypeScript type definitions
        └── validation.ts   # Zod schemas for form validation
```

### Backend App (`/apps/backend`)
Django 5.0 REST API with JWT authentication, Google OAuth, and email services.

```
apps/backend/
├── manage.py               # Django management script
├── package.json            # Development scripts for root orchestration
├── requirements.txt        # Python dependencies (Django, DRF, JWT, etc.)
├── run_server.py           # Custom server runner
├── db.sqlite3              # SQLite database (development)
├── backend/                # Django project configuration
│   ├── __init__.py         # Python package marker
│   ├── asgi.py            # ASGI configuration for async support
│   ├── settings.py        # Django settings with JWT, CORS, Google OAuth
│   ├── urls.py            # Main URL configuration
│   └── wsgi.py            # WSGI configuration for deployment
└── authentication/        # Django app for auth functionality
    ├── __init__.py         # Python package marker
    ├── admin.py           # Django admin configuration
    ├── apps.py            # App configuration
    ├── authentication.py  # Custom JWT cookie authentication
    ├── email_service.py   # SendinBlue email service integration
    ├── models.py          # Database models (uses default User model)
    ├── serializers.py     # DRF serializers for API data validation
    ├── tests.py           # Unit tests
    ├── urls.py            # Authentication URL patterns
    ├── utils.py           # JWT cookie helpers and Google verification
    ├── views.py           # API endpoints for authentication
    ├── management/        # Custom Django management commands
    │   └── commands/
    │       └── runserver.py  # Custom runserver command
    └── migrations/        # Database migrations
        └── __init__.py
```

## 📚 Documentation (`/docs`)

```
docs/
├── folder-structure.md    # This file - explains the structure
├── google-oauth-setup.md  # Google OAuth configuration guide
├── recaptcha-setup.md     # reCAPTCHA configuration guide
├── payment-setup.md       # Payment integration guide (Google Pay & PayPal)
└── docker-setup.md        # Docker containerization guide
```

## 🎯 Key Design Principles

### 1. **Simplicity First**
- Clean, minimal structure with only essential files
- No complex build systems or monorepo configurations
- Direct, straightforward development workflow

### 2. **Clear Separation**
- `apps/frontend/` contains the React/Next.js application
- `apps/backend/` contains the Django REST API
- `docs/` contains all documentation

### 3. **Self-Contained Applications**
- Frontend includes all React components and auth logic
- Backend includes all Django models, views, and auth endpoints
- No external package dependencies within the project

### 4. **Easy Development**
- Simple npm/pip commands to get started
- Standard Next.js and Django development patterns
- Clear environment configuration

## 🚀 Development Workflow

### Getting Started
```bash
# Install dependencies
npm run install:frontend
npm run install:backend

# Set up database
npm run migrate

# Start development servers
npm run dev:frontend    # Terminal 1
npm run dev:backend     # Terminal 2
```

### Available Commands
```bash
# Frontend
npm run dev:frontend          # Start Next.js dev server
npm run install:frontend      # Install frontend dependencies
npm run build:frontend        # Build for production

# Backend
npm run dev:backend           # Start Django dev server
npm run install:backend       # Install Python dependencies
npm run migrate               # Run database migrations
npm run createsuperuser       # Create admin user
```

## 📂 File Purposes

### Root Files
- `package.json` - Development orchestration scripts for managing both apps
- `.nvmrc` - Node.js version specification for consistent development environment
- `README.md` - Main project documentation and setup instructions
- `LICENSE` - MIT license for the project
- `.gitignore` - Specifies files to ignore in version control

### Frontend Files
- `src/app/layout.tsx` - Root layout with AuthProvider and environment debug logging
- `src/app/page.tsx` - Home page displaying authentication status and user info
- `src/app/login/page.tsx` - Login page with email/password and Google Sign-In
- `src/app/signup/page.tsx` - Registration page with form validation
- `src/app/reset-password/page.tsx` - Password reset page with token validation
- `src/components/LoginForm.tsx` - Reusable login form with React Hook Form and Zod
- `src/components/SimpleGoogleButton.tsx` - Google Sign-In button with credential handling
- `src/contexts/AuthContext.tsx` - Authentication state management and API integration
- `src/lib/api.ts` - Type-safe API client for backend communication
- `src/lib/validation.ts` - Zod schemas for form validation and type safety

### Backend Files
- `backend/settings.py` - Comprehensive Django settings with JWT, CORS, Google OAuth, and email configuration
- `authentication/views.py` - API endpoints for register, login, Google auth, password reset, etc.
- `authentication/serializers.py` - DRF serializers for data validation and transformation
- `authentication/utils.py` - JWT cookie helpers and Google credential verification utilities
- `authentication/email_service.py` - SendinBlue integration for welcome and password reset emails
- `authentication/authentication.py` - Custom JWT cookie authentication class
- `requirements.txt` - Python dependencies including Django 5.0, DRF, JWT, Google Auth, SendinBlue

## 🔧 Configuration Files

### Environment Configuration
Environment variables are configured directly in development (no .env.example templates provided):
- **Frontend**: Create `apps/frontend/.env.local` with `NEXT_PUBLIC_API_BASE_URL` and `NEXT_PUBLIC_GOOGLE_CLIENT_ID`
- **Backend**: Create `apps/backend/.env` with `SECRET_KEY`, `GOOGLE_CLIENT_ID`, `CORS_ALLOWED_ORIGINS`, etc.

### Build Configurations
- `apps/frontend/next.config.js` - Next.js build and development configuration
- `apps/frontend/tsconfig.json` - TypeScript configuration with strict mode enabled
- `apps/frontend/tailwind.config.js` - Tailwind CSS configuration with custom theme
- `apps/frontend/postcss.config.js` - PostCSS configuration for Tailwind processing
- `apps/backend/package.json` - Development scripts for root package.json integration
- `.nvmrc` - Node.js version specification for consistent development environments

## 🎯 Benefits of This Structure

### ✅ **Production-Ready Architecture**
- Secure JWT authentication with HTTP-only cookies
- Comprehensive error handling and validation
- CORS/CSRF protection configured for deployment
- Email service integration for user communications

### ✅ **Modern Development Stack**
- Next.js 14 with App Router and TypeScript
- Django 5.0 with Django REST Framework
- React Hook Form with Zod validation
- Tailwind CSS for responsive design

### ✅ **Developer Experience**
- Single-command development workflow via root package.json
- Type safety throughout the entire stack
- Comprehensive debugging and testing utilities
- Clear separation of concerns and modular architecture

### ✅ **Scalability & Maintainability**
- Modular component architecture in frontend
- Django app structure for backend extensibility
- Clean API design with consistent patterns
- Easy to add new authentication providers or features

This production-ready structure provides a solid foundation for authentication systems while maintaining clean architecture principles and modern development practices.