import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import DashboardLayout from './payments/components/dashboard-layout'
import TopNavigation from '@/components/top-navigation'

export const metadata: Metadata = {
  title: 'v0 App',
  description: 'Created with v0',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <DashboardLayout>
          {children}
        </DashboardLayout>
      </body>
    </html>
  )
}
