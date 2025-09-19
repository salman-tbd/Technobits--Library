import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Google Pay Integration',
  description: 'Google Pay payment integration demo',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <script src="https://pay.google.com/gp/p/js/pay.js" async></script>
      </head>
      <body style={{ margin: 0, fontFamily: 'Arial, sans-serif' }}>
        {children}
      </body>
    </html>
  )
}
