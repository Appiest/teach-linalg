import type { Metadata } from "next";
import { Hanken_Grotesk } from "next/font/google";
import "./globals.css";

const hanken = Hanken_Grotesk({ subsets: ["latin"], variable: "--font-hanken" });

export const metadata: Metadata = {
  title: "Linear algebra, one idea a morning",
  description: "Short animated lessons and notes that walk through a full linear algebra course, one concept per day.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${hanken.variable} antialiased`}>
      <body className="min-h-dvh bg-surface font-sans text-text">{children}</body>
    </html>
  );
}
