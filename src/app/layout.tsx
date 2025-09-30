import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { BackendProvider } from "@/contexts/BackendContext";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
  fallback: ["system-ui", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
  display: "swap",
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
  fallback: ["ui-monospace", "SFMono-Regular", "Menlo", "Monaco", "Consolas", "Liberation Mono", "Courier New", "monospace"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Intellicket - Intelligent Cybersecurity Support Platform",
  description: "AI-powered cybersecurity log analysis and support platform. Expert analysis for your security products with intelligent ticket resolution and advanced threat detection.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <BackendProvider>
          {children}
        </BackendProvider>
      </body>
    </html>
  );
}
