"use client";

import "../app/globals.css";
import React from "react";
import { ReactQueryProvider } from "../lib/ReactQueryProvider";
import { ToastProvider } from "../components/ToastProvider";

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gradient-to-br from-stone-50 via-amber-50 to-orange-50">
        <ReactQueryProvider>
          <ToastProvider>{children}</ToastProvider>
        </ReactQueryProvider>
      </body>
    </html>
  );
}

