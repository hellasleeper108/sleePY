import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { NotificationProvider } from "@/components/NotificationContainer";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "PyQuest - Gamified Python Learning",
  description: "Level up your Python skills with coding challenges, XP, achievements, and more!",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <NotificationProvider>
          {children}
        </NotificationProvider>
      </body>
    </html>
  );
}
