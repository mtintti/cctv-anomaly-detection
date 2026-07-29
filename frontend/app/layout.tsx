import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import ImageContainer from './imageContainer'
import Providers from './providers/tanstack'
import {
  useQuery,
  useMutation,
  useQueryClient,
  QueryClient,
  QueryClientProvider,
} from '@tanstack/react-query'


export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
      <>
        <html
          lang="en">
          <body className="min-h-full flex flex-col">
              <Providers>
                {children}
              </Providers>
          </body>
        </html>
      </>
  );
}
