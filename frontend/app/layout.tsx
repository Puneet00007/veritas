import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Veritas — Fact-Check Anything",
  description:
    "Multi-agent fact-checking. Paste a link, claim, image, or social post and get a scored, sourced verdict in seconds.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
