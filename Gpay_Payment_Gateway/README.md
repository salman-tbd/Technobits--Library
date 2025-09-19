# Google Pay Integration

A complete Google Pay integration following Google Pay API best practices with Django backend and Next.js frontend.

## Project Structure

```
Gpay_Payment_Gateway/
├── backend/                 # Django backend
│   ├── manage.py
│   ├── requirements.txt
│   ├── gpay_backend/       # Django project settings
│   └── payments/           # Payments app with API
└── frontend/               # Next.js frontend
    ├── package.json
    ├── app/
    │   ├── layout.tsx
    │   └── page.tsx        # Main payment page
    ├── next.config.js
    └── tsconfig.json
```

## Setup Instructions

### 1. Environment Configuration

**IMPORTANT**: Set up environment variables before running the application.

See [ENVIRONMENT_SETUP.md](./ENVIRONMENT_SETUP.md) for detailed instructions.

### 2. Backend (Django)

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file with your configuration (see ENVIRONMENT_SETUP.md)

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Start Django server:
   ```bash
   python manage.py runserver
   ```

Backend will run on `http://localhost:8000`

### 3. Frontend (Next.js)

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create `.env.local` file with your configuration (see ENVIRONMENT_SETUP.md)

4. Start development server:
   ```bash
   npm run dev
   ```

Frontend will run on `http://localhost:3000`

## Features

- **Frontend**: Clean payment interface with amount input and official Google Pay button
- **Backend**: RESTful API endpoint at `/api/process-payment/` for payment processing
- **Google Pay Integration**: Uses official Google Pay API following best practices
- **Environment Variables**: Secure configuration management
- **CORS Enabled**: Backend configured to accept requests from frontend
- **Error Handling**: Comprehensive error handling and user feedback
- **Token Processing**: Receives and logs Google Pay payment tokens

## Testing

1. Start both backend and frontend servers
2. Open `http://localhost:3000`
3. Enter an amount and click "Pay with Google Pay"
4. Use test cards provided by Google Pay for testing

## Configuration

### Google Pay Settings
- **Merchant ID**: Set via `NEXT_PUBLIC_GOOGLE_PAY_MERCHANT_ID` environment variable
- **Environment**: `TEST` for development, `PRODUCTION` for live
- **Supported Cards**: VISA, MASTERCARD
- **Currency**: INR
- **Auth Methods**: PAN_ONLY, CRYPTOGRAM_3DS

### Security Features
- Environment variable configuration
- Input validation and sanitization
- Comprehensive error handling
- Secure token processing

## Implementation Guide

### Google Pay API Method Used

This implementation follows the official Google Pay API for Web pattern:

1. **Base Configuration**: Uses `baseRequest` with API version 2.0
2. **Card Networks**: Configurable allowed networks (VISA, MASTERCARD)
3. **Auth Methods**: Supports PAN_ONLY and CRYPTOGRAM_3DS
4. **Tokenization**: Proper gateway tokenization specification
5. **Official Button**: Uses `createButton()` method for authentic Google Pay button
6. **Environment Support**: Configurable for TEST/PRODUCTION environments

### Payment Flow

1. User enters amount
2. Google Pay button is dynamically created
3. User clicks button and completes payment
4. Token is sent to backend
5. Backend receives and logs the payment token
6. Success response sent back to frontend

### Current Implementation

This implementation:
- Receives Google Pay payment tokens from the frontend
- Validates the payment data
- Logs payment information for testing
- Returns success responses
- **Does not process actual payments** - you'll need to integrate with your payment processor

### Next Steps for Production

- Configure your actual Google Pay merchant ID
- Integrate with your preferred payment processor (Stripe, Adyen, etc.)
- Add payment validation and processing logic
- Implement webhook handling for payment confirmations
- Add payment history and receipt generation
- Set up production monitoring and logging

### Production Checklist

- [ ] Replace TEST merchant ID with production ID
- [ ] Integrate with payment processor
- [ ] Set up SSL/HTTPS
- [ ] Implement webhook endpoints
- [ ] Add comprehensive logging
- [ ] Set up monitoring and alerts
- [ ] Test with real payment methods
