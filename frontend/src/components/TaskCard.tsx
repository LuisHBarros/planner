import React from "react";
import type { TaskResponseDto, TaskStatus } from "../types/api";

type TaskCardProps = {
  task: TaskResponseDto;
  onChangeStatus?: (status: TaskStatus) => void;
  isUpdating?: boolean;
};

export const TaskCard: React.FC<TaskCardProps> = ({
  task,
  onChangeStatus,
  isUpdating
}) => {
  return (
    <div className="task-card p-3 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-2 mb-2">
        <h3 className="text-sm font-semibold text-text-primary line-clamp-2">
          {task.title}
        </h3>
        <span className="text-[10px] uppercase tracking-wide px-2 py-0.5 rounded-full bg-surface text-text-secondary">
          {task.priority}
        </span>
      </div>
      <p className="text-xs text-text-secondary line-clamp-3 mb-2">
        {task.description}
      </p>
      <div className="flex items-center justify-between text-[11px] text-text-secondary mb-2">
        <span>ID: {task.id.slice(0, 8)}</span>
        {task.due_date && (
          <span>Due {new Date(task.due_date).toLocaleDateString()}</span>
        )}
      </div>
      <div className="flex items-center justify-between gap-2">
        <div className="flex-1 h-1.5 rounded-full bg-surface overflow-hidden">
          <div
            className="h-full bg-brand"
            style={{ width: `${task.completion_percentage ?? 0}%` }}
          />
        </div>
        {onChangeStatus && (
          <button
            type="button"
            disabled={isUpdating}
            onClick={() =>
              onChangeStatus(
                task.status === "todo"
                  ? "doing"
                  : task.status === "doing"
                  ? "done"
                  : task.status
              )
            }
            className="text-[11px] px-2 py-1 rounded-md border border-brand/40 text-brand bg-background hover:bg-brand/5 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isUpdating ? "Updating..." : "Advance"}
          </button>
        )}
      </div>
    </div>
  );
};

