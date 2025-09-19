/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: false, // Disabled to prevent double mounting issues with PayPal SDK
  swcMinify: true,
  env: {
    PAYPAL_CLIENT_ID: process.env.PAYPAL_CLIENT_ID,
    DJANGO_API_URL: process.env.DJANGO_API_URL || 'http://localhost:8000',
  },
}

module.exports = nextConfig
