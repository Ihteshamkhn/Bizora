import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Bizora — AI Business Manager",
  description:
    "Upload your business data, get a dashboard, insights, forecasts and an AI manager.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
