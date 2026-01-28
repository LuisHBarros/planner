import React from "react";
import {
  AlertTriangle,
  CheckCircle2,
  Loader2,
  PlayCircle
} from "lucide-react";

export type TaskStatus = "ready" | "blocked" | "in_progress" | "done";

type Props = {
  status: TaskStatus;
  className?: string;
  "aria-label"?: string;
};

const statusConfig: Record<
  TaskStatus,
  {
    label: string;
    icon: React.ReactNode;
    badgeClass: string;
    pillClass: string;
  }
> = {
  ready: {
    label: "Ready",
    icon: <PlayCircle className="h-3.5 w-3.5" aria-hidden="true" />,
    badgeClass:
      "bg-status-ready-soft text-white dark:text-black border border-status-ready",
    pillClass: "bg-status-ready text-white"
  },
  blocked: {
    label: "Blocked",
    icon: <AlertTriangle className="h-3.5 w-3.5" aria-hidden="true" />,
    badgeClass:
      "bg-status-blocked text-white border border-status-blocked shadow-sm",
    pillClass: "bg-status-blocked text-white"
  },
  in_progress: {
    label: "In progress",
    icon: (
      <Loader2
        className="h-3.5 w-3.5 animate-spin-slow"
        aria-hidden="true"
      />
    ),
    badgeClass:
      "bg-status-in-progress-soft text-status-in-progress border border-status-in-progress",
    pillClass: "bg-status-in-progress text-black"
  },
  done: {
    label: "Done",
    icon: <CheckCircle2 className="h-3.5 w-3.5" aria-hidden="true" />,
    badgeClass:
      "bg-status-done-soft text-status-done border border-status-done",
    pillClass: "bg-status-done text-white"
  }
};

export const StatusBadge: React.FC<Props> = ({
  status,
  className = "",
  "aria-label": ariaLabel
}) => {
  const config = statusConfig[status];

  return (
    <span
      role="status"
      aria-label={ariaLabel ?? config.label}
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-semibold tracking-wide uppercase ${config.badgeClass} ${className}`}
    >
      {config.icon}
      <span>{config.label}</span>
    </span>
  );
};

export const StatusPill: React.FC<Props> = ({
  status,
  className = "",
  "aria-label": ariaLabel
}) => {
  const config = statusConfig[status];

  return (
    <span
      role="status"
      aria-label={ariaLabel ?? config.label}
      className={`inline-flex items-center gap-1.5 rounded-md px-2 py-0.5 text-[10px] font-bold tracking-wide ${config.pillClass} ${className}`}
    >
      {config.icon}
      <span>{config.label}</span>
    </span>
  );
};

