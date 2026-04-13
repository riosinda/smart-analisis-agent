import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Rappi · Operations Assistant',
  description: 'Asistente conversacional de análisis operacional para Rappi',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body className={`${inter.className} antialiased h-full`}>{children}</body>
    </html>
  );
}
