import { AppShell } from "@/components/AppShell";

type BoardTask = {
  id: string;
  title: string;
  project: string;
  role: "Backend Senior" | "Frontend" | "Product Manager";
  status: "Todo" | "In Progress" | "Blocked" | "Done";
  priority: "Low" | "Medium" | "High" | "Critical";
  progress: number;
  blockedBy?: string;
};

const MOCK_TASKS: BoardTask[] = [
  {
    id: "T-101",
    title: "Fix critical payment bug",
    project: "Payments",
    role: "Backend Senior",
    status: "In Progress",
    priority: "Critical",
    progress: 40
  },
  {
    id: "T-102",
    title: "Implement OAuth2 provider",
    project: "Auth",
    role: "Backend Senior",
    status: "Todo",
    priority: "High",
    progress: 10,
    blockedBy: "T-101"
  },
  {
    id: "T-201",
    title: "Dashboard layout for payments",
    project: "Dashboard",
    role: "Frontend",
    status: "Blocked",
    priority: "High",
    progress: 20,
    blockedBy: "T-101"
  },
  {
    id: "T-301",
    title: "Define Q2 priorities",
    project: "Planning",
    role: "Product Manager",
    status: "In Progress",
    priority: "Medium",
    progress: 65
  },
  {
    id: "T-302",
    title: "Write release notes",
    project: "DX",
    role: "Product Manager",
    status: "Todo",
    priority: "Low",
    progress: 0
  }
];

const STATUSES: BoardTask["status"][] = ["Todo", "In Progress", "Blocked", "Done"];

export default function WorkspacePage() {
  return (
    <AppShell
      rightPanel={
        <div className="flex flex-col gap-3 text-xs">
          <section className="rounded-2xl border border-borderSubtle/80 bg-surfaceSubtle/80 px-3 py-2.5 space-y-2">
            <header className="flex items-center justify-between">
              <span className="text-[11px] font-medium text-textSecondary/80">
                Workload by role
              </span>
              <span className="rounded-full bg-warning/20 px-2 py-0.5 text-[10px] text-warning border border-warning/40">
                Attention
              </span>
            </header>
            <ul className="space-y-1.5">
              <li className="flex items-center justify-between">
                <span className="text-textSecondary/80">Backend Senior</span>
                <span className="flex items-center gap-1.5">
                  <span className="h-1.5 w-1.5 rounded-full bg-danger" />
                  <span className="text-danger text-[11px]">Impossível</span>
                </span>
              </li>
              <li className="flex items-center justify-between">
                <span className="text-textSecondary/80">Frontend</span>
                <span className="flex items-center gap-1.5">
                  <span className="h-1.5 w-1.5 rounded-full bg-success" />
                  <span className="text-success text-[11px]">Saudável</span>
                </span>
              </li>
              <li className="flex items-center justify-between">
                <span className="text-textSecondary/80">Product Manager</span>
                <span className="flex items-center gap-1.5">
                  <span className="h-1.5 w-1.5 rounded-full bg-warning" />
                  <span className="text-warning text-[11px]">Quase limite</span>
                </span>
              </li>
            </ul>
          </section>

          <section className="rounded-2xl border border-borderSubtle/80 bg-surfaceSubtle/80 px-3 py-2.5 space-y-2">
            <header className="flex items-center justify-between">
              <span className="text-[11px] font-medium text-textSecondary/80">
                Dependencies snapshot
              </span>
            </header>
            <div className="space-y-2">
              <div className="rounded-xl bg-surface px-2.5 py-2 border border-borderSubtle/70">
                <div className="text-[11px] text-textSecondary/80 mb-1.5">
                  Payments &amp; Dashboard
                </div>
                <ol className="space-y-1.5 text-[11px] text-textSecondary/90">
                  <li>1. T-101 Fix critical payment bug (in progress)</li>
                  <li>2. T-201 Dashboard layout for payments (blocked)</li>
                </ol>
              </div>
            </div>
          </section>
        </div>
      }
    >
      <div className="flex-1 flex flex-col h-full">
        <div className="flex items-center justify-between px-6 py-3 border-b border-borderSubtle">
          <div className="flex items-center gap-2 text-xs text-textSecondary/80">
            <span className="rounded-pill border border-borderSubtle bg-surfaceSubtle/80 px-3 py-1">
              View: Board
            </span>
            <button className="rounded-pill border border-borderSubtle/60 bg-surface px-2 py-1 hover:border-accent/70 hover:text-textPrimary transition-colors">
              Table
            </button>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <button className="rounded-pill border border-borderSubtle bg-surfaceSubtle/80 px-3 py-1 text-textSecondary hover:border-accent/70 hover:text-textPrimary transition-colors">
              Filter by project
            </button>
            <button className="rounded-pill bg-accent text-white px-3 py-1 shadow-card text-xs hover:bg-accent/90 transition-colors">
              + New task
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-x-auto px-4 py-4">
          <div className="flex gap-4 min-w-max">
            {STATUSES.map((status) => {
              const columnTasks = MOCK_TASKS.filter((task) => task.status === status);
              return (
                <section
                  key={status}
                  className="w-72 rounded-2xl border border-borderSubtle/80 bg-surface/80 px-3 py-3 flex flex-col gap-3"
                >
                  <header className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <span
                        className={`h-1.5 w-1.5 rounded-full ${
                          status === "Blocked"
                            ? "bg-danger"
                            : status === "Done"
                            ? "bg-success"
                            : "bg-accent"
                        }`}
                      />
                      <span className="font-medium">{status}</span>
                    </div>
                    <span className="text-[11px] text-textSecondary/80">
                      {columnTasks.length} items
                    </span>
                  </header>

                  <div className="flex-1 flex flex-col gap-2 text-xs">
                    {columnTasks.map((task) => (
                      <article
                        key={task.id}
                        className="rounded-xl bg-surfaceSubtle/90 border border-borderSubtle/80 px-3 py-2 space-y-1 cursor-pointer hover:border-accent/70 transition-colors"
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-[11px] text-textSecondary/70">
                            {task.id}
                          </span>
                          <span
                            className={`rounded-full px-2 py-0.5 text-[10px] ${
                              task.priority === "Critical"
                                ? "bg-danger/20 text-danger border border-danger/40"
                                : task.priority === "High"
                                ? "bg-warning/20 text-warning border border-warning/40"
                                : "bg-surface text-textSecondary border border-borderSubtle/70"
                            }`}
                          >
                            {task.priority}
                          </span>
                        </div>
                        <div className="text-[13px] font-medium">{task.title}</div>
                        <div className="text-[11px] text-textSecondary/80">
                          {task.project} • {task.role}
                        </div>
                        <div className="flex items-center justify-between text-[10px] text-textSecondary/80 mt-1">
                          <span>{task.progress}% complete</span>
                          {task.blockedBy && status === "Blocked" && (
                            <span className="text-danger">Blocked by {task.blockedBy}</span>
                          )}
                        </div>
                      </article>
                    ))}
                    {columnTasks.length === 0 && (
                      <div className="rounded-xl border border-dashed border-borderSubtle/70 px-3 py-4 text-[11px] text-textSecondary/70 text-center">
                        No tasks in this column.
                      </div>
                    )}
                  </div>
                </section>
              );
            })}
          </div>
        </div>
      </div>
    </AppShell>
  );
}

