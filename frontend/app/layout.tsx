import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import ImageContainer from './imageContainer'


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
          {children}
          </body>
        </html>
      </>
  );
}
