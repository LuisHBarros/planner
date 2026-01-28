import type { ReactNode } from "react";
import "../app/globals.css";

export const metadata = {
  title: "Planner Multiplayer",
  description: "Role-first, dependency aware planning with Claude-style UX"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body>{children}</body>
    </html>
  );
}

