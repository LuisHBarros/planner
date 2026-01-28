import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background text-textPrimary flex items-center justify-center px-4">
      <div className="max-w-xl w-full space-y-6">
        <div className="space-y-2 text-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-borderSubtle/80 bg-surfaceSubtle/80 px-3 py-1 text-[11px] text-textSecondary/80">
            <span className="h-1.5 w-1.5 rounded-full bg-success" />
            <span>Demo workspace • Seeded backend</span>
          </div>
          <h1 className="text-3xl font-semibold tracking-tight">
            Planner Multiplayer
          </h1>
          <p className="text-sm text-textSecondary">
            Role-first ownership, manager-defined execution order, and dependency-aware
            task management in a Claude-style interface.
          </p>
        </div>

        <div className="rounded-2xl border border-borderSubtle/80 bg-surface/80 px-4 py-3 space-y-3 text-sm">
          <div className="flex items-center justify-between">
            <span className="text-textSecondary/90">Demo company</span>
            <span className="rounded-full bg-accentSoft/40 px-2 py-0.5 text-[11px] text-accentMuted">
              AI enabled
            </span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-xs text-textSecondary/90">
            <div className="rounded-xl bg-surfaceSubtle/70 px-3 py-2 border border-borderSubtle/70">
              <div className="font-medium text-[11px] mb-1">Core Product</div>
              <div>Backend Senior, Frontend, Product Manager</div>
            </div>
            <div className="rounded-xl bg-surfaceSubtle/70 px-3 py-2 border border-borderSubtle/70">
              <div className="font-medium text-[11px] mb-1">Projects</div>
              <div>Payments, Auth, Dashboard</div>
            </div>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row gap-3">
          <Link
            href="/app"
            className="flex-1 rounded-pill bg-accent text-center text-sm font-medium py-2 shadow-card hover:bg-accent/90 transition-colors"
          >
            Enter workspace
          </Link>
          <button className="flex-1 rounded-pill border border-borderSubtle bg-surfaceSubtle/70 text-sm text-textSecondary py-2 hover:border-accent/70 hover:text-textPrimary transition-colors">
            Configure company & teams (coming soon)
          </button>
        </div>
      </div>
    </div>
  );
}

