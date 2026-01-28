"use client";

import React, { useEffect } from "react";
import { useTasks } from "../../../lib/useTasks";
import { useToast } from "../../../components/ToastProvider";
import { TaskCard } from "../../../components/TaskCard";

const COLUMNS = [
  { id: "todo", title: "To do" },
  { id: "doing", title: "Doing" },
  { id: "blocked", title: "Blocked" },
  { id: "done", title: "Done" }
] as const;

export default function BoardPage() {
  const { tasks, isLoading, isError, error, updateStatus, isUpdatingStatus } =
    useTasks();
  const { showError } = useToast();

  useEffect(() => {
    if (isError && error instanceof Error) {
      showError(error.message);
    }
  }, [isError, error, showError]);

  return (
    <div className="max-w-[1600px] mx-auto px-8 py-8 space-y-6 text-text-primary">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-light text-text-primary">Task Board</h1>
          <p className="text-sm text-text-secondary">
            Connected to FastAPI tasks endpoint with React Query.
          </p>
        </div>
      </header>

      <section className="grid grid-cols-1 md:grid-cols-4 gap-4 items-start">
        {COLUMNS.map((column) => (
          <div key={column.id} className="space-y-3">
            <div className="flex items-center justify-between mb-1">
              <h2 className="text-sm font-semibold text-text-primary">
                {column.title}
              </h2>
              <span className="text-[11px] text-text-secondary">
                {
                  tasks.filter((t) => t.status === column.id).length
                }{" "}
                tasks
              </span>
            </div>

            <div className="board-column space-y-3 min-h-[160px]">
              {isLoading ? (
                <SkeletonColumn />
              ) : (
                tasks
                  .filter((task) => task.status === column.id)
                  .map((task) => (
                    <TaskCard
                      key={task.id}
                      task={task}
                      isUpdating={isUpdatingStatus}
                      onChangeStatus={(status) =>
                        updateStatus({ taskId: task.id, status })
                      }
                    />
                  ))
              )}

              {!isLoading &&
                tasks.filter((task) => task.status === column.id).length ===
                  0 && (
                  <p className="text-xs text-text-secondary text-center py-6">
                    No tasks in this column.
                  </p>
                )}
            </div>
          </div>
        ))}
      </section>
    </div>
  );
}

function SkeletonColumn() {
  return (
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <div
          key={i}
          className="animate-pulse rounded-lg border border-border-subtle bg-surface p-3 space-y-2"
        >
          <div className="h-3 w-3/4 bg-card rounded" />
          <div className="h-3 w-1/2 bg-card rounded" />
          <div className="h-2 w-full bg-card/70 rounded" />
        </div>
      ))}
    </div>
  );
}

