'use client';

import type { ReactNode } from 'react';
import Link from 'next/link';

type AppShellProps = {
  children: ReactNode;
  rightPanel?: ReactNode;
};

export function AppShell({ children, rightPanel }: AppShellProps) {
  return (
    <div className="app-shell">
      <header className="border-b border-borderSubtle bg-surface px-5 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="h-7 w-7 rounded-md bg-accentSoft flex items-center justify-center text-[11px] font-semibold text-accentMuted">
              PL
            </div>
            <div className="flex flex-col">
              <span className="text-[13px] font-semibold tracking-tight">
                Planner Multiplayer
              </span>
              <span className="text-[11px] text-textSecondary">
                What should I work on next?
              </span>
            </div>
          </div>

          <div className="hidden md:flex items-center gap-2 text-[11px] text-textSecondary">
            <button className="rounded-pill border border-borderSubtle bg-surfaceSubtle px-2.5 py-1">
              Company ▾
            </button>
            <button className="rounded-pill border border-borderSubtle bg-surfaceSubtle px-2.5 py-1">
              Team ▾
            </button>
            <button className="rounded-pill border border-borderSubtle bg-surfaceSubtle px-2.5 py-1">
              Project ▾
            </button>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-2 text-[11px] text-textSecondary">
            <input
              className="pill-input"
              placeholder="Search tasks, roles, projects…"
            />
          </div>
          <button className="rounded-pill border border-borderSubtle bg-surfaceSubtle px-2.5 py-1.5 text-[11px] text-textSecondary flex items-center gap-1.5">
            <span className="inline-flex h-5 w-5 items-center justify-center rounded-full bg-accentSoft text-[10px] text-accentMuted">
              L
            </span>
            <span>Luís • Backend Senior</span>
          </button>
        </div>
      </header>

      <nav className="border-b border-borderSubtle bg-surface px-5 flex items-center gap-4 text-[12px] text-textSecondary">
        <Link
          href="/app"
          className="py-2 border-b-2 border-accent text-textPrimary"
        >
          My Tasks
        </Link>
        <button className="py-2 hover:text-textPrimary">Projects</button>
        <button className="py-2 hover:text-textPrimary">Roles</button>
        <button className="py-2 hover:text-textPrimary">Dashboard</button>
      </nav>

      <main className="app-shell-main">
        <section className="flex-1 flex overflow-hidden">
          <div className="flex-1 flex flex-col overflow-hidden">{children}</div>
          {rightPanel && (
            <aside className="app-shell-context hidden xl:flex flex-col px-4 py-4 gap-3">
              {rightPanel}
            </aside>
          )}
        </section>
      </main>
    </div>
  );
}

