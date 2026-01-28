import { describe, expect, it } from "vitest";
import { taskListResponseSchema, taskStatusSchema } from "./api";

describe("API DTO schemas", () => {
  it("parses a valid task list response", () => {
    const payload = {
      tasks: [
        {
          id: "11111111-1111-1111-1111-111111111111",
          project_id: "22222222-2222-2222-2222-222222222222",
          title: "Test task",
          description: "Description",
          status: "todo",
          priority: "medium",
          rank_index: 1,
          role_responsible_id: "33333333-3333-3333-3333-333333333333",
          user_responsible_id: null,
          completion_percentage: null,
          completion_source: null,
          due_date: null,
          blocked_reason: null,
          created_at: "2024-01-01T00:00:00Z",
          updated_at: "2024-01-01T00:00:00Z",
          completed_at: null
        }
      ]
    };

    const parsed = taskListResponseSchema.parse(payload);
    expect(parsed.tasks).toHaveLength(1);
    expect(parsed.tasks[0].title).toBe("Test task");
  });

  it("rejects invalid task status", () => {
    expect(() =>
      taskStatusSchema.parse("invalid-status")
    ).toThrowError();
  });
});

