"use client";

import React, { useEffect, useMemo, useState } from "react";
import {
  Calendar,
  Users,
  AlertTriangle,
  Clock,
  GitBranch,
  Plus,
  Check,
  Activity,
  ListChecks,
  LayoutDashboard,
  Mail,
  Share2
} from "lucide-react";
import {
  api,
  CompanyResponse,
  ProjectResponse,
  RoleResponse,
  TaskResponse,
  TeamResponse,
  TimelineTask,
  DependencyGraphNode,
  DependencyGraphEdge,
  MeTeamResponse,
  TeamInviteResponse
} from "../lib/api";

const DEMO_COMPANY_ID = "ba765b1f-756e-49a0-bc74-56616b87a7f0";
const DEMO_TEAM_ID = "19d98d69-8368-4271-8b19-0dfd6dd092f1";
const DEMO_PROJECT_ID = "33236406-3078-4db6-b36a-822724871e88";

type TabId =
  | "overview"
  | "companies"
  | "teams"
  | "roles"
  | "projects"
  | "tasks"
  | "timeline"
  | "graph"
  | "invites"
  | "me";

export const AppShell: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabId>("overview");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [companies, setCompanies] = useState<CompanyResponse[]>([]);
  const [teams, setTeams] = useState<TeamResponse[]>([]);
  const [roles, setRoles] = useState<RoleResponse[]>([]);
  const [projects, setProjects] = useState<ProjectResponse[]>([]);
  const [tasks, setTasks] = useState<TaskResponse[]>([]);
  const [timeline, setTimeline] = useState<TimelineTask[]>([]);
  const [graphNodes, setGraphNodes] = useState<DependencyGraphNode[]>([]);
  const [graphEdges, setGraphEdges] = useState<DependencyGraphEdge[]>([]);
  const [myTeams, setMyTeams] = useState<MeTeamResponse[]>([]);
  const [lastInvite, setLastInvite] = useState<TeamInviteResponse | null>(null);

  const [demoUserId, setDemoUserId] = useState(
    "00000000-0000-0000-0000-000000000001"
  );

  const blockedCount = useMemo(
    () => tasks.filter((t) => t.status === "blocked").length,
    [tasks]
  );
  const doneCount = useMemo(
    () => tasks.filter((t) => t.status === "done").length,
    [tasks]
  );

  const estimatedHours = useMemo(
    () => tasks.length * 4,
    [tasks]
  );

  const loadInitial = async () => {
    setLoading(true);
    setError(null);
    try {
      const [
        companiesRes,
        teamsRes,
        rolesRes,
        projectsRes,
        tasksRes,
        timelineRes,
        graphRes
      ] = await Promise.all([
        api.listCompanies(),
        api.listTeams(DEMO_COMPANY_ID),
        api.listRoles(DEMO_TEAM_ID),
        api.listProjects(DEMO_TEAM_ID),
        api.getProjectTasks(DEMO_PROJECT_ID),
        api.getProjectTimeline(DEMO_PROJECT_ID),
        api.getProjectDependencyGraph(DEMO_PROJECT_ID)
      ]);
      setCompanies(companiesRes.companies);
      setTeams(teamsRes.teams);
      setRoles(rolesRes.roles);
      setProjects(projectsRes.projects);
      setTasks(tasksRes.tasks);
      setTimeline(timelineRes.tasks);
      setGraphNodes(graphRes.nodes);
      setGraphEdges(graphRes.edges);
    } catch (e: any) {
      setError(e?.message ?? "Failed to load data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadInitial();
  }, []);

  const handleClaimTask = async (task: TaskResponse) => {
    setError(null);
    try {
      const updated = await api.claimTask(task.id, demoUserId);
      setTasks((prev) => prev.map((t) => (t.id === task.id ? updated : t)));
    } catch (e: any) {
      setError(e?.message ?? "Failed to claim task");
    }
  };

  const handleStatusChange = async (
    task: TaskResponse,
    status: TaskResponse["status"]
  ) => {
    setError(null);
    try {
      const updated = await api.updateTaskStatus(task.id, status, demoUserId);
      setTasks((prev) => prev.map((t) => (t.id === task.id ? updated : t)));
    } catch (e: any) {
      setError(e?.message ?? "Failed to update status");
    }
  };

  const handleProgressChange = async (
    task: TaskResponse,
    percentage: number
  ) => {
    setError(null);
    try {
      const updated = await api.updateTaskProgress(
        task.id,
        percentage,
        demoUserId
      );
      setTasks((prev) => prev.map((t) => (t.id === task.id ? updated : t)));
    } catch (e: any) {
      setError(e?.message ?? "Failed to update progress");
    }
  };

  const handleRankTasks = async () => {
    setError(null);
    try {
      const sorted = [...tasks].sort((a, b) => a.rank_index - b.rank_index);
      const reversed = sorted.map((t) => t.id).reverse();
      const res = await api.rankProjectTasks(DEMO_PROJECT_ID, reversed);
      setTasks(res.tasks);
    } catch (e: any) {
      setError(e?.message ?? "Failed to rank tasks");
    }
  };

  const handleReloadMyTeams = async () => {
    setError(null);
    try {
      const res = await api.getMyTeams(demoUserId);
      setMyTeams(res.teams);
      setActiveTab("me");
    } catch (e: any) {
      setError(e?.message ?? "Failed to load /me/teams");
    }
  };

  const handleCreateInvite = async () => {
    setError(null);
    try {
      const res = await api.createTeamInvite(DEMO_TEAM_ID, {
        created_by_user_id: demoUserId,
        role: "member",
        expires_at: null
      });
      setLastInvite(res);
      setActiveTab("invites");
    } catch (e: any) {
      setError(e?.message ?? "Failed to create invite");
    }
  };

  const tabs: { id: TabId; label: string; icon: React.ReactNode }[] = [
    { id: "overview", label: "Overview", icon: <LayoutDashboard className="w-4 h-4" /> },
    { id: "companies", label: "Companies", icon: <Activity className="w-4 h-4" /> },
    { id: "teams", label: "Teams", icon: <Users className="w-4 h-4" /> },
    { id: "roles", label: "Roles", icon: <ListChecks className="w-4 h-4" /> },
    { id: "projects", label: "Projects", icon: <Calendar className="w-4 h-4" /> },
    { id: "tasks", label: "Tasks", icon: <Check className="w-4 h-4" /> },
    { id: "timeline", label: "Timeline", icon: <Clock className="w-4 h-4" /> },
    { id: "graph", label: "Dependencies", icon: <GitBranch className="w-4 h-4" /> },
    { id: "invites", label: "Invites", icon: <Share2 className="w-4 h-4" /> },
    { id: "me", label: "/me", icon: <Mail className="w-4 h-4" /> }
  ];

  return (
    <div className="min-h-screen bg-background text-text-primary">
      <header className="border-b border-border-subtle bg-surface/80 backdrop-blur-sm sticky top-0 z-20">
        <div className="max-w-[1800px] mx-auto px-8 py-5 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-light text-text-primary tracking-tight mb-1">
              Planner MVP
            </h1>
            <p className="text-sm text-text-secondary">
              Connected to backend API • Company, teams, roles, projects, tasks & invites
            </p>
          </div>
          <div className="flex items-center gap-3">
            <input
              value={demoUserId}
              onChange={(e) => setDemoUserId(e.target.value)}
              className="px-3 py-2 text-xs border border-border-subtle rounded-md focus:ring-2 focus:ring-brand focus:border-transparent outline-none w-64 bg-card text-text-primary placeholder:text-text-secondary/70"
              placeholder="Demo user_id for /me and task actions"
            />
            <button
              onClick={handleReloadMyTeams}
              className="px-4 py-2 bg-card text-text-primary border border-border-subtle rounded-md font-medium text-xs hover:bg-surface transition-all flex items-center gap-2"
            >
              <Users className="w-4 h-4" />
              Load /me/teams
            </button>
            <button
              onClick={handleCreateInvite}
              className="px-4 py-2 bg-brand text-white rounded-md font-medium text-xs hover:brightness-110 transition-all shadow-sm hover:shadow-md flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Create Team Invite
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-[1800px] mx-auto px-8 py-8">
        <div className="flex gap-6">
          <nav className="w-56 flex-shrink-0">
            <div className="bg-surface/90 backdrop-blur-sm rounded-2xl shadow-sm border border-border-subtle p-3 space-y-1">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-left transition-all ${
                    activeTab === tab.id
                      ? "bg-card text-text-primary shadow-sm"
                      : "text-text-secondary hover:bg-surface"
                  }`}
                >
                  {tab.icon}
                  <span>{tab.label}</span>
                </button>
              ))}
            </div>

            <div className="mt-4 text-xs text-text-secondary">
              <div className="font-semibold mb-1">Demo IDs</div>
              <div>Company: {DEMO_COMPANY_ID}</div>
              <div>Team: {DEMO_TEAM_ID}</div>
              <div>Project: {DEMO_PROJECT_ID}</div>
            </div>
          </nav>

          <section className="flex-1 space-y-6">
            {error && (
              <div className="bg-red-50/90 border border-red-300 text-red-900 text-sm rounded-lg px-4 py-3">
                {error}
              </div>
            )}

            {loading && (
              <div className="bg-surface rounded-xl border border-border-subtle p-4 text-sm text-text-secondary">
                Loading data from API…
              </div>
            )}

            {activeTab === "overview" && (
              <div className="space-y-6">
                <div className="grid grid-cols-4 gap-4">
                  <StatCard
                    icon={<Calendar className="w-4 h-4 text-amber-700" />}
                    label="Total Tasks"
                    value={tasks.length}
                  />
                  <StatCard
                    icon={
                      <AlertTriangle className="w-4 h-4 text-red-600" />
                    }
                    label="Blocked"
                    value={blockedCount}
                  />
                  <StatCard
                    icon={<Check className="w-4 h-4 text-emerald-700" />}
                    label="Done"
                    value={doneCount}
                  />
                  <StatCard
                    icon={<Clock className="w-4 h-4 text-emerald-700" />}
                    label="Est. Hours"
                    value={`${estimatedHours}h`}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <Panel title="Tasks in Project">
                    <TasksTable
                      tasks={tasks}
                      onClaim={handleClaimTask}
                      onStatusChange={handleStatusChange}
                      onProgressChange={handleProgressChange}
                    />
                    <div className="mt-3 flex justify-end">
                      <button
                        onClick={handleRankTasks}
                        className="px-3 py-1.5 text-xs rounded-md bg-white border border-amber-300 text-amber-800 hover:bg-amber-50 flex items-center gap-1"
                      >
                        <GitBranch className="w-3 h-3" />
                        Rank tasks (reverse)
                      </button>
                    </div>
                  </Panel>
                  <Panel title="Project Timeline">
                    <TimelineTable tasks={timeline} />
                  </Panel>
                </div>
              </div>
            )}

            {activeTab === "companies" && (
              <Panel title="Companies">
                <SimpleTable
                  headers={["Name", "Slug", "Plan", "Billing Email"]}
                  rows={companies.map((c) => [
                    c.name,
                    c.slug,
                    c.plan,
                    c.billing_email
                  ])}
                />
              </Panel>
            )}

            {activeTab === "teams" && (
              <Panel title="Teams">
                <SimpleTable
                  headers={["Name", "Company", "Default Language"]}
                  rows={teams.map((t) => [
                    t.name,
                    t.company_id,
                    t.default_language
                  ])}
                />
              </Panel>
            )}

            {activeTab === "roles" && (
              <Panel title="Roles">
                <SimpleTable
                  headers={["Name", "Level", "Base Capacity", "Team"]}
                  rows={roles.map((r) => [
                    r.name,
                    r.level,
                    r.base_capacity.toString(),
                    r.team_id
                  ])}
                />
              </Panel>
            )}

            {activeTab === "projects" && (
              <Panel title="Projects">
                <SimpleTable
                  headers={["Name", "Team", "Status"]}
                  rows={projects.map((p) => [p.name, p.team_id, p.status])}
                />
              </Panel>
            )}

            {activeTab === "tasks" && (
              <Panel title="Tasks in Project">
                <TasksTable
                  tasks={tasks}
                  onClaim={handleClaimTask}
                  onStatusChange={handleStatusChange}
                  onProgressChange={handleProgressChange}
                />
              </Panel>
            )}

            {activeTab === "timeline" && (
              <Panel title="Project Timeline">
                <TimelineTable tasks={timeline} />
              </Panel>
            )}

            {activeTab === "graph" && (
              <Panel title="Project Dependency Graph">
                <DependencyGraphView nodes={graphNodes} edges={graphEdges} />
              </Panel>
            )}

            {activeTab === "invites" && (
              <Panel title="Team Invites">
                {lastInvite ? (
                  <div className="text-sm space-y-2">
                    <div>
                      <span className="font-semibold">Token: </span>
                      <code className="px-2 py-1 bg-stone-100 rounded text-xs">
                        {lastInvite.token}
                      </code>
                    </div>
                    <div>Role: {lastInvite.role}</div>
                    <div>Expires at: {lastInvite.expires_at}</div>
                  </div>
                ) : (
                  <p className="text-sm text-stone-500">
                    Use “Create Team Invite” in the header to generate an
                    invite.
                  </p>
                )}
              </Panel>
            )}

            {activeTab === "me" && (
              <Panel title="/me/teams">
                {myTeams.length === 0 ? (
                  <p className="text-sm text-stone-500">
                    No teams for this user yet. Use different demo ids or
                    invites.
                  </p>
                ) : (
                  <SimpleTable
                    headers={["Name", "Team ID", "Joined"]}
                    rows={myTeams.map((t) => [
                      t.name,
                      t.id,
                      new Date(t.created_at).toLocaleString()
                    ])}
                  />
                )}
              </Panel>
            )}
          </section>
        </div>
      </main>
    </div>
  );
};

const StatCard: React.FC<{
  icon: React.ReactNode;
  label: string;
  value: React.ReactNode;
}> = ({ icon, label, value }) => (
  <div className="bg-card/95 backdrop-blur-sm border border-border-subtle rounded-lg p-3">
    <div className="flex items-center gap-3">
      <div className="w-9 h-9 rounded-lg bg-brand/10 flex items-center justify-center flex-shrink-0 text-brand">
        {icon}
      </div>
      <div>
        <div className="text-xl font-semibold text-text-primary">{value}</div>
        <div className="text-xs text-text-secondary">{label}</div>
      </div>
    </div>
  </div>
);

const Panel: React.FC<{ title: string; children: React.ReactNode }> = ({
  title,
  children
}) => (
  <div className="bg-surface/95 backdrop-blur-sm rounded-2xl shadow-sm border border-border-subtle p-4">
    <div className="flex items-center justify-between mb-3">
      <h2 className="text-sm font-semibold text-text-primary">{title}</h2>
    </div>
    <div>{children}</div>
  </div>
);

const SimpleTable: React.FC<{
  headers: string[];
  rows: (string | number | React.ReactNode)[][];
}> = ({ headers, rows }) => (
  <div className="border border-border-subtle rounded-xl overflow-hidden bg-surface">
    <table className="min-w-full text-sm">
      <thead className="bg-card/80">
        <tr>
          {headers.map((h) => (
            <th
              key={h}
              className="px-3 py-2 text-left text-xs font-semibold text-text-secondary"
            >
              {h}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map((row, i) => (
          <tr
            key={i}
            className={i % 2 === 0 ? "bg-card" : "bg-surface"}
          >
            {row.map((cell, j) => (
              <td key={j} className="px-3 py-2 text-xs text-text-secondary">
                {cell}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

const TasksTable: React.FC<{
  tasks: TaskResponse[];
  onClaim: (t: TaskResponse) => void;
  onStatusChange: (t: TaskResponse, s: TaskResponse["status"]) => void;
  onProgressChange: (t: TaskResponse, pct: number) => void;
}> = ({ tasks, onClaim, onStatusChange, onProgressChange }) => (
  <div className="border border-border-subtle rounded-xl overflow-hidden bg-surface">
    <table className="min-w-full text-xs">
      <thead className="bg-card/80">
        <tr>
          <th className="px-2 py-2 text-left font-semibold text-text-secondary">
            Title
          </th>
          <th className="px-2 py-2 text-left font-semibold text-stone-600">
            Status
          </th>
          <th className="px-2 py-2 text-left font-semibold text-stone-600">
            Priority
          </th>
          <th className="px-2 py-2 text-left font-semibold text-stone-600">
            Progress
          </th>
          <th className="px-2 py-2 text-left font-semibold text-stone-600">
            Actions
          </th>
        </tr>
      </thead>
      <tbody>
        {tasks.map((t, i) => (
          <tr
            key={t.id}
            className={i % 2 === 0 ? "bg-card" : "bg-surface"}
          >
            <td className="px-2 py-2 text-text-primary">{t.title}</td>
            <td className="px-2 py-2 capitalize text-text-secondary">{t.status}</td>
            <td className="px-2 py-2 capitalize text-text-secondary">{t.priority}</td>
            <td className="px-2 py-2">
              <input
                type="range"
                min={0}
                max={100}
                value={t.completion_percentage ?? 0}
                onChange={(e) =>
                  onProgressChange(t, Number.parseInt(e.target.value, 10))
                }
              />
              <span className="ml-2 text-text-secondary">
                {t.completion_percentage ?? 0}
                %
              </span>
            </td>
            <td className="px-2 py-2">
              <div className="flex flex-wrap gap-1">
                <button
                  onClick={() => onClaim(t)}
                  className="px-2 py-1 border border-brand/40 rounded-md text-[10px] text-brand hover:bg-brand/10"
                >
                  Claim
                </button>
                {["todo", "doing", "blocked", "done"].map((s) => (
                  <button
                    key={s}
                    onClick={() => onStatusChange(t, s as TaskResponse["status"])}
                    className={`px-2 py-1 rounded-md text-[10px] border ${
                      t.status === s
                        ? "bg-brand text-white border-brand"
                        : "border-border-subtle text-text-secondary hover:bg-surface"
                    }`}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

const TimelineTable: React.FC<{ tasks: TimelineTask[] }> = ({ tasks }) => (
  <div className="border border-border-subtle rounded-xl overflow-hidden bg-surface max-h-96 overflow-y-auto">
    <table className="min-w-full text-xs">
      <thead className="bg-card/80">
        <tr>
          <th className="px-2 py-2 text-left font-semibold text-text-secondary">
            Title
          </th>
          <th className="px-2 py-2 text-left font-semibold text-stone-600">
            Expected
          </th>
          <th className="px-2 py-2 text-left font-semibold text-stone-600">
            Actual
          </th>
          <th className="px-2 py-2 text-left font-semibold text-stone-600">
            Delayed
          </th>
          <th className="px-2 py-2 text-left font-semibold text-stone-600">
            Blocking deps
          </th>
        </tr>
      </thead>
      <tbody>
        {tasks.map((t, i) => (
          <tr
            key={t.id}
            className={i % 2 === 0 ? "bg-card" : "bg-surface"}
          >
            <td className="px-2 py-2 text-text-primary">{t.title}</td>
            <td className="px-2 py-2">
              {t.expected_start_date ?? "—"} →{" "}
              {t.expected_end_date ?? "—"}
            </td>
            <td className="px-2 py-2">
              {t.actual_start_date ?? "—"} → {t.actual_end_date ?? "—"}
            </td>
            <td className="px-2 py-2">
              {t.is_delayed ? (
              <span className="text-red-500 font-semibold">Yes</span>
              ) : (
                "No"
              )}
            </td>
            <td className="px-2 py-2">{t.blocking_dependencies}</td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

const DependencyGraphView: React.FC<{
  nodes: DependencyGraphNode[];
  edges: DependencyGraphEdge[];
}> = ({ nodes, edges }) => (
  <div className="grid grid-cols-2 gap-4">
    <div>
      <h3 className="text-xs font-semibold text-text-secondary mb-2">
        Nodes
      </h3>
      <div className="border border-border-subtle rounded-xl bg-surface max-h-80 overflow-y-auto">
        <table className="min-w-full text-xs">
      <thead className="bg-card/80">
            <tr>
              <th className="px-2 py-2 text-left text-text-secondary">Task</th>
              <th className="px-2 py-2 text-left text-text-secondary">Status</th>
            </tr>
          </thead>
          <tbody>
            {nodes.map((n, i) => (
              <tr
                key={n.task_id}
                className={i % 2 === 0 ? "bg-card" : "bg-surface"}
              >
                <td className="px-2 py-1.5 text-text-primary">{n.title}</td>
                <td className="px-2 py-1.5 capitalize text-text-secondary">
                  {n.status}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
    <div>
      <h3 className="text-xs font-semibold text-text-secondary mb-2">
        Edges
      </h3>
      <div className="border border-border-subtle rounded-xl bg-surface max-h-80 overflow-y-auto">
        <table className="min-w-full text-xs">
      <thead className="bg-card/80">
            <tr>
              <th className="px-2 py-2 text-left text-text-secondary">From</th>
              <th className="px-2 py-2 text-left text-text-secondary">To</th>
              <th className="px-2 py-2 text-left text-text-secondary">Type</th>
            </tr>
          </thead>
          <tbody>
            {edges.map((e, i) => (
              <tr
                key={`${e.from_task_id}-${e.to_task_id}-${i}`}
                className={i % 2 === 0 ? "bg-card" : "bg-surface"}
              >
                <td className="px-2 py-1.5 text-text-primary">
                  {e.from_task_id}
                </td>
                <td className="px-2 py-1.5 text-text-primary">
                  {e.to_task_id}
                </td>
                <td className="px-2 py-1.5 text-text-secondary">{e.type}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  </div>
);

