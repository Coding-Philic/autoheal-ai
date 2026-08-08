import type { Metadata } from "next";
import "./globals.css";
import Cursor from "@/components/Cursor";

export const metadata: Metadata = {
  title: "AutoHeal AI | Autonomous Self-Healing Software Engine",
  description: "AutoHeal AI is a language-agnostic CLI tool that detects errors in real-time and automatically diagnoses and fixes them using AI.",
  openGraph: {
    title: "AutoHeal AI",
    description: "Install once, self-heal forever.",
  }
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" style={{ scrollBehavior: "smooth" }}>
      <body>
        <Cursor />
        {children}
      </body>
    </html>
  );
}
