# Stripe Payment Gateway - Frontend

A simple, focused React/Next.js frontend for Stripe payment processing. Clean and minimal design focused purely on payment functionality.

## 🚀 Features

### Core Features
- **Secure Payment Processing** - Full Stripe integration with checkout sessions
- **Simple Payment Form** - Amount and description input with real-time validation
- **Success/Cancel Pages** - Proper payment flow handling
- **Responsive Design** - Mobile-first design that works on all devices
- **Real-time Notifications** - Toast notifications for user feedback

### UI/UX Features
- **Clean Design** - Minimal, professional interface focused on payments
- **Loading States** - Payment processing indicators
- **Test Mode Support** - Built-in test card information
- **Security Badges** - Trust indicators and security information
- **Smooth Animations** - Subtle transitions and feedback

### Technical Features
- **TypeScript** - Full type safety throughout the application
- **Tailwind CSS** - Utility-first CSS framework for rapid development
- **Component Library** - Reusable UI components with shadcn/ui
- **Configuration Management** - Environment-based configuration system
- **Performance Optimized** - Lightweight and fast

## 📁 Project Structure

```
src/
├── app/                    # Next.js app router pages
│   ├── payment/           # Success/cancel pages
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Main payment page
├── components/           # Reusable components
│   ├── payments/         # Payment-specific components
│   └── ui/              # Base UI components
├── lib/                 # Utilities and configuration
│   ├── api/             # API client functions
│   └── config.ts        # App configuration
└── types/               # TypeScript type definitions
```

## 🛠️ Setup & Installation

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Stripe account with API keys

### Installation

1. **Clone and navigate to the frontend directory**
   ```bash
   cd Stripe_Payment_Gateway/frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Environment Configuration**
   Create a `.env.local` file with your configuration:
   ```env
   # Stripe Configuration
   NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
   
   # API Configuration  
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
   
   # App Configuration
   NEXT_PUBLIC_APP_NAME=Stripe Payment Gateway
   NEXT_PUBLIC_APP_URL=http://localhost:3000
   ```

4. **Start the development server**
   ```bash
   npm run dev
   ```

5. **Open your browser**
   Navigate to `http://localhost:3000`

## 🎨 UI Components

### Navigation
- **Responsive Header** - Adaptive navigation with mobile menu
- **User Menu** - Profile dropdown with authentication state
- **Security Badge** - Trust indicators for payment security

### Payment Components
- **StripeCheckout** - Complete payment form with validation
- **Payment History** - Sortable, filterable transaction table
- **Payment Dashboard** - Analytics and quick actions

### Authentication
- **Login Form** - Secure login with validation and demo credentials
- **Registration Form** - Multi-step registration with password strength
- **Profile Management** - User profile and settings (coming soon)

### UI Elements
- **Loading States** - Spinners, skeletons, and progress indicators
- **Error Handling** - Error boundaries and user-friendly error pages
- **Notifications** - Toast notifications for user feedback
- **Cards & Layouts** - Consistent card-based design system

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | Stripe publishable key | Yes |
| `NEXT_PUBLIC_API_BASE_URL` | Backend API URL | Yes |
| `NEXT_PUBLIC_APP_NAME` | Application name | No |
| `NEXT_PUBLIC_APP_URL` | Application URL | No |

### Feature Flags

Enable/disable features using environment variables:
- `NEXT_PUBLIC_ENABLE_ANALYTICS` - Analytics integration
- `NEXT_PUBLIC_ENABLE_NOTIFICATIONS` - Push notifications
- `NEXT_PUBLIC_ENABLE_DEBUG` - Debug mode

## 🎯 Usage Examples

### Basic Payment Flow
```tsx
import { StripeCheckout } from '@/components/payments/StripeCheckout';

<StripeCheckout
  amount={29.99}
  currency="USD"
  description="Premium Service"
  onSuccess={(sessionId) => console.log('Success:', sessionId)}
  onError={(error) => console.error('Error:', error)}
/>
```

### Navigation with Authentication
```tsx
import Navigation from '@/components/ui/navigation';

<Navigation 
  user={{ name: 'John Doe', email: 'john@example.com' }}
  isAuthenticated={true}
  onLogout={() => handleLogout()}
/>
```

### Error Handling
```tsx
import { ErrorBoundary } from '@/components/ui/error-boundary';

<ErrorBoundary>
  <YourComponent />
</ErrorBoundary>
```

## 🚀 Deployment

### Build for Production
```bash
npm run build
npm start
```

### Deploy to Vercel
```bash
npm install -g vercel
vercel --prod
```

### Environment Setup
Ensure all environment variables are configured in your deployment platform.

## 🔒 Security Features

- **PCI DSS Compliance** - Stripe handles sensitive card data
- **HTTPS Enforcement** - Secure data transmission
- **Input Validation** - Client and server-side validation
- **Error Boundaries** - Prevent application crashes
- **CSP Headers** - Content Security Policy implementation

## 📱 Mobile Experience

- **Responsive Design** - Works on all screen sizes
- **Touch Optimized** - Mobile-friendly interactions
- **Fast Loading** - Optimized for mobile networks
- **Offline Support** - Basic offline functionality (planned)

## 🧪 Testing

### Run Tests
```bash
npm run test
npm run test:watch
npm run test:coverage
```

### E2E Testing
```bash
npm run test:e2e
```

## 📈 Performance

- **Code Splitting** - Automatic route-based splitting
- **Image Optimization** - Next.js image optimization
- **Bundle Analysis** - `npm run analyze`
- **Lighthouse Score** - 95+ performance score

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation** - Check this README and inline comments
- **Issues** - Create GitHub issues for bugs
- **Discussions** - Use GitHub discussions for questions
- **Email** - Contact support@example.com

## 🔄 Changelog

### v1.0.0 (Current)
- ✅ Complete UI overhaul with modern design
- ✅ Responsive navigation with user authentication
- ✅ Comprehensive dashboard with analytics
- ✅ Payment history with advanced filtering
- ✅ Error boundaries and loading states
- ✅ Toast notifications system
- ✅ TypeScript integration
- ✅ Mobile-first responsive design

### Planned Features
- 🔄 Dark mode support
- 🔄 Advanced analytics charts
- 🔄 Bulk payment operations
- 🔄 Export functionality
- 🔄 Real-time notifications
- 🔄 Progressive Web App (PWA)

---

Built with ❤️ using Next.js, TypeScript, Tailwind CSS, and Stripe API.
