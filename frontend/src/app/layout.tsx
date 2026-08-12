import type { Metadata } from "next";
import { Inter, Space_Grotesk, JetBrains_Mono } from "next/font/google";
import { ThemeProvider } from "next-themes";
import "./globals.css";

import { AuthProvider } from "../context/AuthContext";
import { WebSocketProvider } from "@/context/WebSocketContext";
import { Toaster } from "@/components/ui/toaster";
import { OfflineBanner } from "@/components/ui/offline-banner";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const spaceGrotesk = Space_Grotesk({ subsets: ["latin"], variable: "--font-space-grotesk" });
const jetbrainsMono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-jetbrains-mono" });

export const metadata: Metadata = {
  title: "Veridex - AI Platform",
  description: "Enterprise-grade orchestration for multi-agent LLM systems.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} ${spaceGrotesk.variable} ${jetbrainsMono.variable} dark h-full`}>
      <body className="min-h-full h-screen overflow-hidden flex bg-[#0B0E12] text-[#F6F4EF] antialiased">
        <ThemeProvider attribute="class" defaultTheme="dark" enableSystem={false}>
          <AuthProvider>
            <WebSocketProvider>
              <div className="flex-1 overflow-auto">
                {children}
                <Toaster />
                <OfflineBanner />
              </div>
            </WebSocketProvider>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
