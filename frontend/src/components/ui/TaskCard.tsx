import React from "react";
import { CalendarDays, Clock, Users } from "lucide-react";
import { StatusBadge, TaskStatus } from "./StatusBadge";

export type TaskCardProps = {
  id?: string;
  title: string;
  role: string;
  assignee: string;
  estimatedHours: number;
  status: TaskStatus;
  expectedStart?: string | null;
  expectedEnd?: string | null;
  dependenciesCount?: number;
  isDragging?: boolean;
  onClick?: () => void;
};

export const TaskCard: React.FC<TaskCardProps> = ({
  id,
  title,
  role,
  assignee,
  estimatedHours,
  status,
  expectedStart,
  expectedEnd,
  dependenciesCount = 0,
  isDragging = false,
  onClick
}) => {
  return (
    <article
      id={id}
      tabIndex={0}
      aria-label={title}
      className={`group relative rounded-xl border bg-surface shadow-soft-elevated transition-all cursor-pointer focus-ring ${
        isDragging ? "cursor-grabbing scale-[1.02]" : "cursor-grab"
      }`}
      onClick={onClick}
    >
      {/* Header */}
      <header className="flex items-start justify-between gap-3 border-b border-border/60 bg-surface-muted px-3 py-2.5">
        <div className="min-w-0">
          <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
            {role}
          </p>
          <h3 className="mt-0.5 line-clamp-2 text-sm font-semibold text-foreground">
            {title}
          </h3>
        </div>
        <StatusBadge status={status} />
      </header>

      {/* Body */}
      <div className="space-y-2.5 px-3 py-3">
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span className="inline-flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-primary-soft text-[11px] font-semibold text-primary-foreground">
            {assignee
              .split(" ")
              .map((n) => n[0])
              .join("")
              .slice(0, 2)
              .toUpperCase()}
          </span>
          <div className="min-w-0">
            <p className="truncate text-xs font-medium text-foreground">
              {assignee}
            </p>
            <p className="truncate text-[11px] text-muted-foreground">
              {role}
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2 text-[11px]">
          <span className="inline-flex items-center gap-1 rounded-md bg-accent-green/10 px-1.5 py-0.5 text-[11px] font-medium text-accent-green">
            <Clock className="h-3 w-3" aria-hidden="true" />
            {estimatedHours}h
          </span>

          {typeof dependenciesCount === "number" && dependenciesCount > 0 && (
            <span className="inline-flex items-center gap-1 rounded-md bg-status-blocked-soft px-1.5 py-0.5 text-[11px] font-semibold text-status-blocked">
              <Users className="h-3 w-3" aria-hidden="true" />
              {dependenciesCount} blocker
              {dependenciesCount > 1 ? "s" : ""}
            </span>
          )}
        </div>

        {(expectedStart || expectedEnd) && (
          <dl className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-muted-foreground">
            <div className="inline-flex items-center gap-1.5">
              <CalendarDays className="h-3 w-3" aria-hidden="true" />
              <dt className="sr-only">Expected</dt>
              <dd className="flex items-center gap-1">
                {expectedStart && <span>{expectedStart}</span>}
                {expectedEnd && expectedEnd !== expectedStart && (
                  <>
                    <span aria-hidden="true">→</span>
                    <span>{expectedEnd}</span>
                  </>
                )}
              </dd>
            </div>
          </dl>
        )}
      </div>
    </article>
  );
};

export const TaskCardSkeleton: React.FC = () => {
  return (
    <article
      aria-busy="true"
      aria-label="Loading task"
      className="rounded-xl border border-border bg-surface-muted/60 p-3 shadow-soft-elevated animate-pulse"
    >
      <div className="mb-3 flex items-start justify-between gap-3">
        <div className="space-y-1.5">
          <div className="h-2 w-16 rounded-full bg-muted/40" />
          <div className="h-3 w-40 rounded-full bg-muted/40" />
        </div>
        <div className="h-5 w-20 rounded-full bg-muted/40" />
      </div>

      <div className="mb-3 flex items-center gap-2">
        <div className="h-7 w-7 rounded-full bg-muted/40" />
        <div className="space-y-1">
          <div className="h-2.5 w-28 rounded-full bg-muted/40" />
          <div className="h-2 w-16 rounded-full bg-muted/40" />
        </div>
      </div>

      <div className="flex gap-2">
        <div className="h-4 w-16 rounded-full bg-muted/40" />
        <div className="h-4 w-20 rounded-full bg-muted/30" />
      </div>
    </article>
  );
};

