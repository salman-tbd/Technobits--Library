# 🚀 Technobtis Libraries

**A comprehensive collection of production-ready web application libraries for modern full-stack development**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Django](https://img.shields.io/badge/Django-5.0-green.svg)](https://djangoproject.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue.svg)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org/)

---

## 📚 Library Overview

Technobtis Libraries provides three essential full-stack components for modern web applications, each built with **Django REST Framework** backends and **Next.js TypeScript** frontends:

| 🔐 **Authentication** | 💳 **Google Pay** | 💰 **PayPal Payments** |
|----------------------|-------------------|------------------------|
| Complete auth system with Google OAuth | Google Pay API integration | PayPal Orders API v2 integration |
| JWT tokens + Email services | Test & Production ready | Webhook support + Admin panel |
| [📖 Documentation](./Google-SignIn-SignUp/README.md) | [📖 Documentation](./Gpay_Payment_Gateway/README.md) | [📖 Documentation](./Paypal_Payment_Gateway/README.md) |

---

## 🎯 Quick Start

### 🔧 Prerequisites
- **Node.js 18+** and **npm**
- **Python 3.11+** with **pip**
- **Git** for version control

### ⚡ Installation

```bash
# Clone the repository
git clone <your-repository-url>
cd Technobtis-Libraries

# Choose your library and follow its specific setup guide:
```

**🔐 For Authentication:**
```bash
cd Google-SignIn-SignUp
npm run setup:backend
npm run install:frontend
npm run dev  # Starts both servers
```

**💳 For Google Pay:**
```bash
cd Gpay_Payment_Gateway
# Backend setup
cd backend && python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt && python manage.py migrate

# Frontend setup  
cd ../frontend && npm install && npm run dev
```

**💰 For PayPal:**
```bash
cd Paypal_Payment_Gateway
# Backend setup
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt && python manage.py migrate

# Frontend setup
cd frontend && npm install && npm run dev
```

---

## 📋 Library Details

### 🔐 **Google SignIn/SignUp Authentication System**

**🎯 Purpose:** Complete authentication solution with Google OAuth integration

**✨ Key Features:**
- **Multi-Auth Support**: Email/password + Google Sign-In
- **Security First**: JWT in HTTP-only cookies, reCAPTCHA v3, CORS/CSRF protection
- **Email Integration**: Welcome emails, password reset with SendinBlue API
- **Modern UI**: Responsive design with Tailwind CSS, form validation
- **Developer Experience**: TypeScript throughout, single-command workflow

**🛠️ Tech Stack:**
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, React Hook Form, Zod
- **Backend**: Django 5.0, Django REST Framework, SimpleJWT, Google Auth Library

**📊 API Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register/` | Email/password registration |
| POST | `/auth/login/` | Email/password login |
| POST | `/auth/google/` | Google OAuth login/register |
| GET | `/auth/me/` | Get current user info |
| POST | `/auth/refresh/` | Refresh JWT tokens |
| POST | `/auth/logout/` | Logout user |
| POST | `/auth/password-reset/` | Request password reset |

---

### 💳 **Google Pay Payment Gateway**

**🎯 Purpose:** Complete Google Pay integration following official API best practices

**✨ Key Features:**
- **Official API**: Uses Google Pay API v2.0 with proper tokenization
- **Environment Support**: TEST and PRODUCTION configurations
- **Security**: Environment-based configuration, input validation
- **Payment Flow**: Create order → Google Pay approval → Backend processing
- **Transaction Logging**: Database storage with audit trail

**🛠️ Tech Stack:**
- **Frontend**: Next.js, TypeScript, Google Pay API
- **Backend**: Django, Google Pay API integration, SQLite/PostgreSQL

**💳 Payment Configuration:**
- **Supported Cards**: VISA, MASTERCARD
- **Auth Methods**: PAN_ONLY, CRYPTOGRAM_3DS
- **Currency**: INR (configurable)
- **Environment**: TEST/PRODUCTION via environment variables

**🔧 Environment Variables:**
```bash
# Frontend
NEXT_PUBLIC_GOOGLE_PAY_MERCHANT_ID=your_merchant_id
NEXT_PUBLIC_GOOGLE_PAY_ENVIRONMENT=TEST

# Backend
GOOGLE_PAY_MERCHANT_ID=your_merchant_id
```

---

### 💰 **PayPal Payment Gateway**

**🎯 Purpose:** Production-ready PayPal checkout integration with complete order lifecycle

**✨ Key Features:**
- **PayPal Orders API v2**: Complete order lifecycle (create → capture)
- **Webhook Support**: Real-time payment notifications
- **Admin Interface**: Transaction management and monitoring
- **Error Handling**: Comprehensive error handling and user feedback
- **TypeScript**: Full type safety throughout the frontend

**🛠️ Tech Stack:**
- **Frontend**: Next.js, TypeScript, PayPal SDK, Tailwind CSS
- **Backend**: Django REST Framework, PayPal API v2, PostgreSQL/SQLite

**📊 Payment Flow:**
1. **Create Order**: Frontend requests order creation via Django API
2. **PayPal Approval**: User approves payment in PayPal popup
3. **Capture Payment**: Backend captures the approved payment
4. **Webhook Processing**: Real-time payment status updates
5. **Database Storage**: Transaction audit trail and reporting

**🔧 Environment Variables:**
```bash
# Backend
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_SECRET_KEY=your_paypal_secret_key
PAYPAL_ENVIRONMENT=sandbox  # or 'production'

# Frontend
NEXT_PUBLIC_PAYPAL_CLIENT_ID=your_paypal_client_id
```

**📊 API Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/paypal/create-order/` | Create PayPal order |
| POST | `/api/paypal/capture-order/` | Capture approved payment |
| POST | `/api/paypal/webhook/` | Handle PayPal webhooks |
| GET | `/api/paypal/transactions/` | List transactions |

---

## 🏗️ Architecture Overview

### **🎯 Design Philosophy**
- **Full-Stack TypeScript**: Type safety from frontend to API contracts
- **API-First**: RESTful APIs with comprehensive documentation
- **Security-First**: JWT tokens, CORS/CSRF, input validation, environment isolation
- **Production-Ready**: Error handling, logging, monitoring, webhook support

### **📁 Project Structure**
```
Technobtis-Libraries/
├── Google-SignIn-SignUp/          # 🔐 Authentication System
│   ├── apps/
│   │   ├── frontend/              # Next.js TypeScript app
│   │   └── backend/               # Django REST API
│   └── docs/                      # Setup guides & documentation
├── Gpay_Payment_Gateway/          # 💳 Google Pay Integration
│   ├── frontend/                  # Next.js payment interface
│   └── backend/                   # Django payment processing
└── Paypal_Payment_Gateway/        # 💰 PayPal Integration
    ├── frontend/                  # Next.js checkout flow
    ├── payments/                  # Django payment services
    └── PRODUCTION_WEBHOOK_SETUP.md
```

### **🔧 Common Technologies**
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, React Hook Form
- **Backend**: Django 5.0, Django REST Framework, PostgreSQL/SQLite
- **Authentication**: JWT tokens, OAuth 2.0, HTTP-only cookies
- **Payment Processing**: Official APIs (Google Pay, PayPal Orders API v2)
- **Development**: Hot reload, environment isolation, comprehensive logging

---

## 🚀 Development Guidelines

### **📝 Environment Setup**
Each library includes comprehensive environment setup guides:
- **Google SignIn**: [Setup Guide](./Google-SignIn-SignUp/docs/google-oauth-setup.md)
- **Google Pay**: [Environment Setup](./Gpay_Payment_Gateway/ENVIRONMENT_SETUP.md)
- **PayPal**: [Production Setup](./Paypal_Payment_Gateway/PRODUCTION_WEBHOOK_SETUP.md)

### **🔒 Security Best Practices**
- ✅ Environment variables for all secrets and API keys
- ✅ JWT tokens stored in HTTP-only cookies (XSS protection)
- ✅ CORS/CSRF protection configured
- ✅ Input validation and sanitization
- ✅ Rate limiting and bot protection (reCAPTCHA)
- ✅ Comprehensive error handling without information disclosure

### **🧪 Testing & Development**
- **Authentication**: Test with Google OAuth sandbox
- **Google Pay**: Use Google Pay test cards and TEST environment
- **PayPal**: PayPal sandbox with test accounts and webhooks

---

## 📖 Documentation

### **📚 Individual Library Docs**
- **🔐 Authentication**: [Complete Setup Guide](./Google-SignIn-SignUp/README.md)
- **💳 Google Pay**: [Integration Guide](./Gpay_Payment_Gateway/README.md)
- **💰 PayPal**: [Implementation Guide](./Paypal_Payment_Gateway/README.md)

### **🔧 Setup Guides**
- [Google OAuth Configuration](./Google-SignIn-SignUp/docs/google-oauth-setup.md)
- [reCAPTCHA Setup](./Google-SignIn-SignUp/docs/recaptcha-setup.md)
- [Google Pay Environment Setup](./Gpay_Payment_Gateway/ENVIRONMENT_SETUP.md)
- [PayPal Webhook Configuration](./Paypal_Payment_Gateway/PRODUCTION_WEBHOOK_SETUP.md)

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### **📋 Development Standards**
- Follow TypeScript best practices
- Write comprehensive tests
- Update documentation for new features
- Follow Django REST Framework conventions
- Ensure security best practices

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🏢 About Technobtis

**Technobtis Libraries** is a collection of production-ready, full-stack web application components designed to accelerate modern web development. Each library is built with security, scalability, and developer experience in mind.

### **🎯 Our Mission**
To provide developers with robust, well-documented, and secure building blocks for modern web applications, reducing development time while maintaining high quality standards.

### **💡 Why Choose Technobtis Libraries?**
- ✅ **Production-Ready**: Comprehensive error handling, security, and monitoring
- ✅ **Modern Stack**: Latest versions of Django, Next.js, and TypeScript
- ✅ **Type-Safe**: Full TypeScript support throughout
- ✅ **Well-Documented**: Comprehensive guides and API documentation
- ✅ **Security-First**: JWT tokens, OAuth 2.0, input validation, CORS/CSRF protection
- ✅ **Developer Experience**: Hot reload, single-command workflows, clear error messages

---

## 📞 Support

- **📧 Email**: [support@technobtis.com](mailto:support@technobtis.com)
- **📖 Documentation**: Comprehensive guides included with each library
- **🐛 Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)

---

<div align="center">

**🚀 Built with ❤️ by the Technobtis Team**

[⭐ Star this repo](https://github.com/your-repo) | [🍴 Fork it](https://github.com/your-repo/fork) | [📖 Read the docs](./docs/)

</div>
