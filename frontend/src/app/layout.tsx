"use client";

import "../app/globals.css";
import React from "react";

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gradient-to-br from-stone-50 via-amber-50 to-orange-50">
        {children}
      </body>
    </html>
  );
}

