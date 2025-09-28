import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Intellicket Admin Dashboard',
  description: 'Unified management for CSDAIv2 Backend & Intellicket Frontend',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-slate-900 text-slate-100 min-h-screen antialiased">
        {children}
      </body>
    </html>
  )
}