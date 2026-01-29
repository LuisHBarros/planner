# Planner Multiplayer - Specification

**Version:** 2.1  
**Status:** REFINED  
**Last Updated:** 2026-01-29  
**Changes:** Schedule system clarifications, edge cases, and value object requirements

---

## 📋 Table of Contents

1. Vision & Core Concepts
2. Domain Model
3. Business Rules (REFINED)
4. Use Cases
5. Architecture Requirements (REFINED)
6. Implementation Notes

---

## 🎯 Vision & Core Concepts

### What Problem Does This Solve?

**The Coordination Problem:**

* "What should I work on next?"
* "Who is responsible for this?"
* "Why are we blocked?"
* "Why are we late?"
* **"Why were we late? What caused this delay?"** (NEW)

This system is **not a task list**. It is a **coordination and accountability system**.

### Core Pillars (Updated)

1. Role-First Ownership
2. Manager-Defined Execution Order
3. Intelligent Workload Monitoring
4. Dependency-Aware Task Management
5. Schedule-Aware Execution (REFINED)
6. Causal History & Traceability (EXTENDED)
7. AI-Powered Progress Tracking (Optional)

---

## 🧠 Conceptual Principles

### 1. Tasks Form a Directed Graph, Not a List

Tasks may depend on other tasks. The project is treated as a **Directed Acyclic Graph (DAG)**.
```
Task A ──▶ Task B ──▶ Task C
           ↑_________|
      (Multiple paths possible)
```

Rules:

* Dependencies are explicit (finish-to-start only in MVP)
* Cycles are forbidden (enforced by system)
* Dependencies affect **status** and **schedule** (BR-024)

### 2. Expected vs Actual Dates - Immutable Reality

Dates are **never overwritten silently**.

Each task tracks:

* **expected_start_date** / **expected_end_date** → Planning targets (MUTABLE)
* **actual_start_date** / **actual_end_date** → Reality records (IMMUTABLE)

This enables:

* Delay detection and propagation
* Historical analysis and auditability
* Root-cause tracking (UC-030)

### 3. Schedule Propagation is Cascading

When Task A delays, all transitively dependent tasks cascade delay (BR-024):
```
A (delays 3 days) ──▶ B ──▶ C ──▶ D
                       ↑       ↑
                       └───────┘
                    (Multiple paths)

Result: All receive 3+ days of delay (maximum of all paths)
```

---

## 📦 Domain Model

### Core Entities

#### Task (Extended)
```
Task {
  id: TaskId (VALUE OBJECT)
  project_id: ProjectId (VALUE OBJECT)
  title: String
  description: String
  
  # Scheduling (NEW PRECISION)
  expected_start_date: Optional[UtcDateTime]
  expected_end_date: Optional[UtcDateTime]
  actual_start_date: Optional[UtcDateTime]
  actual_end_date: Optional[UtcDateTime]
  is_delayed: Boolean
  
  # Status and Assignment
  status: TaskStatus (todo|doing|blocked|done)
  role_responsible_id: RoleId (VALUE OBJECT)
  user_responsible_id: Optional[UserId] (VALUE OBJECT)
  
  # Tracking
  rank_index: Float (BR-011: for ordering without renum)
  priority: TaskPriority (low|medium|high)
  completion_percentage: Optional[Int 0-100]
  completion_source: Optional[CompletionSource]
  
  # Metadata
  created_at: UtcDateTime
  updated_at: UtcDateTime
  completed_at: Optional[UtcDateTime]
}
```

**New Requirements:**

* `expected_start_date`, `expected_end_date` are MUTABLE (can be adjusted)
* `actual_start_date`, `actual_end_date` are IMMUTABLE once set (BR-022)
* All dates must be in UTC (UtcDateTime value object)

#### TaskDependency (Clarified)
```
TaskDependency {
  id: UUID
  task_id: TaskId (the dependent)
  depends_on_task_id: TaskId (the blocker)
  dependency_type: DependencyType (finish_to_start only)
  created_at: UtcDateTime
}
```

Only **Finish → Start** dependencies in MVP.

#### ScheduleHistory (Extended)
```
ScheduleHistory {
  id: UUID
  task_id: TaskId
  
  # Previous state
  old_expected_start: Optional[UtcDateTime]
  old_expected_end: Optional[UtcDateTime]
  
  # New state
  new_expected_start: Optional[UtcDateTime]
  new_expected_end: Optional[UtcDateTime]
  
  # Causality
  reason: ScheduleChangeReason enum:
    - DEPENDENCY_DELAY (propagated from blocker)
    - MANUAL_OVERRIDE (manager changed manually)
    - SCOPE_CHANGE (requirements changed)
    - ESTIMATION_ERROR (estimation was wrong)
  
  caused_by_task_id: Optional[TaskId] (if reason = DEPENDENCY_DELAY)
  changed_by_user_id: Optional[UserId] (if reason = MANUAL_OVERRIDE)
  
  # Audit
  created_at: UtcDateTime (immutable)
}
```

**Immutability Rule:** ScheduleHistory records NEVER change. New changes = new records (append-only log).

---

## 📏 Business Rules (REFINED)

### BR-022: Schedule Immutability

* Actual dates (actual_start_date, actual_end_date) are IMMUTABLE once set
* Expected dates can change only via:
  * System propagation (when dependency delays)
  * Manager manual override (UC-029)
* No direct editing of actual dates by users
* Actual dates represent objective reality

### BR-023: Delay Detection
```
if actual_end_date > expected_end_date:
    task.is_delayed = true
```

Automatically detected when task status → DONE (BR-027)

### BR-024: CASCADING DELAY PROPAGATION (REFINED)

#### Definition

Delay in Task A propagates TRANSITIVELY through all dependencies:
```
A (delays 3 days) → B → C → D
Result: B, C, D all delay 3 days
```

#### Algorithm (BFS with max delay selection)

**Input:** Root task that is delayed (just became DONE with actual_end > expected_end)

**Process:**

1. Calculate `delay_delta = actual_end_date - expected_end_date`

2. BFS traversal of dependency graph:
```
   queue = [root_task_id]
   visited = set()
   
   while queue:
       current_id = queue.pop(0)
       if current_id in visited: continue
       visited.add(current_id)
       
       dependents = find_tasks_depending_on(current_id)
       for dependent in dependents:
           queue.append(dependent.id)
           apply_propagation(dependent, delay_delta)
```

3. **Multiple Paths Handling (NEW):** If A → D and B → D:
   * A delays 2 days, B delays 4 days
   * D receives **max(2, 4) = 4 days** delay
   * Each path creates separate ScheduleHistory entry
   * Result: D is shifted by maximum accumulated delay

4. **Task Lifecycle Awareness (BR-026):**
```
   if dependent.status = DONE:
       # Don't shift (actual_end_date is immutable)
       continue
   
   if dependent.actual_start_date is not NULL:
       # Task already started (reality is set)
       dependent.expected_start_date = no_change
       dependent.expected_end_date += delay_delta
   else:
       # Task not started (future is flexible)
       dependent.expected_start_date += delay_delta
       dependent.expected_end_date += delay_delta
```

5. **Duration Preservation:**
```
   duration = expected_end_date - expected_start_date
   # After shift: duration remains the same
```

6. **Idempotency:** If propagate() called twice = no-op (visited set prevents)

**Postcondition:** All dependent tasks shifted by correct delay, history recorded, events emitted.

### BR-025: Historical Integrity & Auditability (EXTENDED)

* ScheduleHistory is APPEND-ONLY (no updates, no deletes)
* Every schedule change creates a new ScheduleHistory entry
* Causal chain is fully traceable (caused_by_task_id)
* Each entry is immutable once created (created_at is permanent)

**Reconstruction of Delay Cause Chain (UC-030):**

Query all ScheduleHistory for a task, ordered by created_at:
```
Task D is 4 days delayed
↳ 2026-12-20 12:00: Shifted by Task C (2 days)
   ↳ 2026-12-18 14:30: Shifted by Task B (2 days)
      ↳ 2026-12-18 09:15: Shifted by Task A (4 days)
         ↳ Reason: Task A completed with actual_end > expected_end
```

### BR-026: SCHEDULE RESPECTS TASK LIFECYCLE (NEW)

When Task B is in progress (actual_start_date is set) and propagation occurs:

* **actual_start_date:** NO CHANGE (immutable, already happened)
* **expected_start_date:** NO CHANGE (already started, can't reschedule start)
* **expected_end_date:** SHIFT by delay_delta (prediction of when will finish)

This prevents semantic confusion: task can't start before it actually started.

### BR-027: AUTOMATIC DELAY DETECTION TIMING (NEW)

Trigger: `TaskStatusChanged` event with new_status = DONE

**Automatic Flow:**

1. Task status changes to DONE
2. `actual_end_date` is set (if not already)
3. `ScheduleService.detect_delay(task)` is called automatically
4. If `actual_end_date > expected_end_date`:
   * Set `task.is_delayed = true`
   * Emit `TaskDelayed` event
   * Trigger propagation via `ScheduleService.propagate_delay()`
5. All dependent tasks are shifted automatically
6. `ScheduleHistory` entries created for audit trail

No manual intervention needed (fully automatic).

---

## 🎬 Use Cases (UPDATED)

### UC-027: Detect Task Delay (AUTOMATED)

**Actor:** System  
**Trigger:** Task status changes to DONE  
**Precondition:** Task has expected_end_date set

**Flow:**

1. User marks task as DONE (or system marks it)
2. `actual_end_date` is automatically set to current UTC time
3. System automatically compares dates
4. If `actual_end_date > expected_end_date`:
   * Mark task as delayed
   * Emit `TaskDelayed` event
   * Initiate propagation

**Postcondition:** Task marked as delayed, propagation queued

### UC-028: Propagate Schedule Changes

**Actor:** System (automatic, triggered by UC-027)

**Flow:**

1. Receive `TaskDelayed` event from UC-027
2. Get root task's `delay_delta = actual_end - expected_end`
3. BFS traverse all dependent tasks
4. For each dependent:
   * Apply BR-024 (cascading)
   * Apply BR-026 (respect lifecycle)
   * Create ScheduleHistory entry
   * Emit `ScheduleChanged` event
5. All propagations complete atomically

**Postcondition:** All dependent schedules updated, history recorded

### UC-029: Manual Schedule Override

**Actor:** Team Manager  
**Precondition:** Manager has permission on project's team

**Flow:**

1. Manager edits Task A's expected dates
2. Manager selects reason:
   * SCOPE_CHANGE (requirements changed)
   * ESTIMATION_ERROR (estimate was wrong)
   * (System auto-selects DEPENDENCY_DELAY or MANUAL_OVERRIDE based on context)
3. System validates new dates
4. Creates ScheduleHistory with changed_by_user_id
5. Triggers propagation (like UC-028)

**Postcondition:** Task reschedules, dependents adjusted, history recorded

### UC-030: VIEW DELAY CAUSE CHAIN (NEW)

**Actor:** Team Member or Manager  
**Precondition:** Task exists and is delayed

**Flow:**

1. User navigates to task details (task is marked as delayed)
2. System queries `SELECT * FROM schedule_history WHERE task_id = ?`
3. System reconstructs causal chain:
   * Walk backwards through caused_by_task_id
   * Build timeline of what caused what
4. Display to user:
```
   Task D is 4 days delayed
   
   Timeline of Changes:
   2026-12-20 12:00 UTC: Adjusted +2 days (caused by Task C)
   2026-12-18 14:30 UTC: Adjusted +2 days (caused by Task B)
   2026-12-18 09:15 UTC: Adjusted +4 days (caused by Task A)
   
   Root Cause:
   Task A was completed 4 days late (actual_end > expected_end)
```

**Postcondition:** User understands complete causal chain of delay

---

## 🏗️ Architecture Requirements (REFINED)

### A. Value Objects for Domain Safety

All identifiers must be VALUE OBJECTS (not raw UUIDs):
```python
class TaskId(ValueObject):
    """Task identifier - type-safe wrapper around UUID"""
    value: UUID

class ProjectId(ValueObject):
class UserId(ValueObject):
class TeamId(ValueObject):
class RoleId(ValueObject):

class UtcDateTime(ValueObject):
    """Always UTC, prevents timezone confusion"""
    value: datetime (with tz=UTC)
    
    @staticmethod
    def now() -> UtcDateTime
    def __add__(self, delta: timedelta) -> UtcDateTime
    def __sub__(self, other: UtcDateTime) -> timedelta
```

**Why:** 
* Type safety (can't pass ProjectId where TaskId expected)
* Semantic clarity (task.id is a TaskId, not ambiguous UUID)
* Prevents common bugs with raw UUIDs

### B. Domain Services vs. Application Services

**Domain Services** (pure business logic, no persistence):
* `ScheduleService`: Calculate delays, detect delays, propagate delays
* `RankingService`: Calculate rank indices
* `AuditService`: Create audit notes

**Application Services** (use cases, orchestration with persistence):
* `CreateTaskUseCase`: Orchestrate task creation
* `UpdateTaskStatusUseCase`: Orchestrate status changes + automatic propagation
* `GetTaskDelayChaincUseCase`: Orchestrate delay chain retrieval

**Why:**
* Single Responsibility (each class has one reason to change)
* Testability (domain services are pure, no mocks needed)
* Reusability (domain services can be used by multiple use cases)

### C. Single Responsibility Principle (SRP)

**CreateTaskUseCase** should ONLY:
* Validate inputs
* Call domain methods
* Emit events
* Orchestrate persistence

**NOT:**
* Calculate ranks (delegate to RankingService)
* Create audit notes (delegate to AuditService)
* Persist multiple entities (repository does that)

Similar for all other use cases.

### D. Event-Driven Architecture

Every significant change emits an event:
```
TaskCreated → Domain event
TaskStatusChanged → Domain event  
TaskDelayed → Domain event (automatic)
ScheduleChanged → Domain event (automatic)
TaskCompleted → Domain event
DependencyAdded → Domain event
```

**Benefits:**
* Automatic side effects (listeners react to events)
* Traceability (audit trail via events)
* Loose coupling (use cases don't call each other)

---

## 🧪 Testing Requirements

### Critical Tests for Schedule System
```python
# test_schedule_propagation_critical.py

test_multiple_paths_uses_max_delay():
    """A→D (2 days), B→D (4 days) ⟹ D delays 4 days"""
    
test_propagation_respects_task_started():
    """If B started, only expected_end shifts, not expected_start"""
    
test_completed_tasks_not_shifted():
    """If B is DONE, propagation doesn't shift it"""
    
test_duration_preserved():
    """duration = end - start always preserved after shift"""
    
test_multiple_paths_idempotent():
    """Propagating from A then B results in correct delay (max, not sum)"""
    
test_schedule_history_immutable():
    """ScheduleHistory can't be updated or deleted"""
    
test_delay_chain_reconstruction():
    """UC-030: Getting task D's chain shows A→B→C→D"""
    
test_automatic_propagation_on_completion():
    """Completing A automatically propagates to B, C, D"""
    
test_manager_override_updates_chain():
    """UC-029: Manual override creates new ScheduleHistory entry"""
```

---

## 📝 Implementation Checklist

### Phase 1: Value Objects & Domain Services

- [x] Create ValueObject base class (frozen dataclasses)
- [x] Implement TaskId, ProjectId, UserId, RoleId, TeamId
- [x] Implement UtcDateTime value object
- [ ] Update all domain models to use value objects (incremental adoption)
- [x] Create ScheduleService domain service (schedule_service_refined.py)
- [x] Create RankingService domain service (ranking.py)
- [ ] Create AuditService domain service

### Phase 2: Schedule Refinements

- [x] Implement BR-026 (task lifecycle awareness)
- [x] Implement BR-027 (automatic detection)
- [x] Refactor propagation algorithm (max delay, multiple paths)
- [x] Add ScheduleHistoryRepository
- [x] Implement UC-030 (delay chain)

### Phase 3: Use Case Refactoring

- [x] Refactor CreateTaskUseCase (SRP)
- [x] Refactor UpdateTaskStatusUseCase (automatic propagation)
- [x] Refactor OverrideTaskScheduleUseCase
- [x] Add critical tests (98 tests passing)

### Phase 4: API & Frontend

- [x] Add GET /api/tasks/{id}/delay-chain endpoint
- [ ] Add schedule visualization on task details (frontend)
- [ ] Implement delay cause chain UI (frontend)
