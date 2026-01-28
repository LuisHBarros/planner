import { z } from "zod";

export const taskStatusSchema = z.enum(["todo", "doing", "blocked", "done"]);
export type TaskStatus = z.infer<typeof taskStatusSchema>;

export const taskPrioritySchema = z.enum(["low", "medium", "high"]);
export type TaskPriority = z.infer<typeof taskPrioritySchema>;

export const completionSourceSchema = z.enum(["manual", "ai"]);
export type CompletionSource = z.infer<typeof completionSourceSchema>;

export const taskResponseSchema = z.object({
  id: z.string().uuid(),
  project_id: z.string().uuid(),
  title: z.string(),
  description: z.string(),
  status: taskStatusSchema,
  priority: taskPrioritySchema,
  rank_index: z.number(),
  role_responsible_id: z.string().uuid(),
  user_responsible_id: z.string().uuid().nullable().optional(),
  completion_percentage: z.number().int().min(0).max(100).nullable().optional(),
  completion_source: completionSourceSchema.nullable().optional(),
  due_date: z.string().datetime().nullable().optional(),
  blocked_reason: z.string().nullable().optional(),
  created_at: z.string(),
  updated_at: z.string(),
  completed_at: z.string().datetime().nullable().optional()
});

export type TaskResponseDto = z.infer<typeof taskResponseSchema>;

export const taskListResponseSchema = z.object({
  tasks: z.array(taskResponseSchema)
});

export type TaskListResponseDto = z.infer<typeof taskListResponseSchema>;

