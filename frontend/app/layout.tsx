import type { Metadata } from 'next'
import './globals.css'
import { TopNavigation } from '@/components/top-navigation'
import { Toaster } from '@/components/ui/toaster'

export const metadata: Metadata = {
  title: 'Investment Dashboard',
  description: 'Payment Management for 401k Plans',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50">
        <div className="flex flex-col h-screen">
          <TopNavigation />
          {children}
          <Toaster />
        </div>
      </body>
    </html>
  )
}