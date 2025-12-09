import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Face Recognition App',
  description: 'Real-time face recognition using DeepFace',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
