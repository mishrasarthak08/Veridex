import type { Metadata } from "next";
import { Poppins, Inter, Geist_Mono } from "next/font/google";
import "./globals.css";

const poppins = Poppins({
  variable: "--font-poppins",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

const inter = Inter({
  variable: "--font-liberation-sans", // using Inter as fallback for Liberation Sans
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-dejavu-mono", // using Geist Mono as fallback for DejaVu Sans Mono
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Veridex Orchestration Console",
  description: "A visual direction for Veridex's operator console",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${poppins.variable} ${inter.variable} ${geistMono.variable} h-full`}
    >
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
