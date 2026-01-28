# Planner Multiplayer - Specification

**Version:** 2.1
**Focus:** Use Cases, Architecture, Scheduling & Business Logic
**Last Updated:** January 28, 2026

---

## 📋 Table of Contents

1. Vision & Core Concepts
2. Domain Model
3. Use Cases
4. Business Rules
5. Architecture
6. Events & Integration
7. Scheduling, Dependencies & History

---

## 🎯 Vision & Core Concepts

### What Problem Does This Solve?

**The Coordination Problem:**

* "What should I work on next?"
* "Who is responsible for this?"
* "Why are we blocked?"
* "Why are we late?"
* "What caused this delay?"

This system is **not a task list**. It is a **coordination and accountability system**.

---

### Core Pillars (Updated)

1. Role-First Ownership
2. Manager-Defined Execution Order
3. Intelligent Workload Monitoring
4. Dependency-Aware Task Management
5. **Schedule-Aware Execution (NEW)**
6. **Causal History & Traceability (NEW)**
7. AI-Powered Progress Tracking (Optional)

---

## 🧠 New Conceptual Principles

### 1. Tasks Form a Directed Graph, Not a List

Tasks may depend on other tasks. The project is treated as a **Directed Acyclic Graph (DAG)**.

```
Task A ──▶ Task B ──▶ Task C
```

Rules:

* Dependencies are explicit
* Cycles are forbidden
* Dependencies affect **status** and **schedule**

---

### 2. Expected vs Actual Dates

Dates are **never overwritten silently**.

Each task tracks:

* Expected dates (planning)
* Actual dates (reality)

This enables:

* Delay propagation
* Historical analysis
* Root-cause tracking

---

## 📦 Domain Model (Additions)

### Task (Extended)

```
Task
- expected_start_date: timestamp (optional)
- expected_end_date: timestamp (optional)
- actual_start_date: timestamp (optional)
- actual_end_date: timestamp (optional)
```

Rules:

* expected_* dates are planning targets
* actual_* dates are immutable once set
* delays are detected by comparing expected_end vs actual_end

---

### TaskDependency (Clarified)

```
TaskDependency
- parent_task_id (blocker)
- child_task_id (dependent)
- dependency_type: enum (finish_to_start)
```

Only **Finish → Start** dependencies are supported in MVP.

---

### ScheduleHistory (NEW ENTITY)

```
ScheduleHistory
- id: UUID
- task_id: UUID
- old_expected_start
- old_expected_end
- new_expected_start
- new_expected_end
- reason: enum (
    dependency_delay,
    manual_override,
    scope_change,
    estimation_error
  )
- caused_by_task_id: UUID (optional)
- changed_by_user_id: UUID (null for system)
- created_at: timestamp
```

Purpose:

* Explain *why* dates changed
* Provide auditability
* Enable delay root-cause analysis

---

## 🎬 New & Updated Use Cases

### UC-026: Define Task Dependencies During Project Creation

**Actor:** Team Manager
**Precondition:** Project exists

**Flow:**

1. Manager creates tasks
2. Manager defines dependencies between tasks
3. System validates DAG (no cycles)
4. System stores TaskDependency records
5. **If parent task not done:**

   * Dependent task status → blocked
6. System creates system notes

**Postcondition:** Task execution order is structurally enforced

---

### UC-027: Detect Task Delay

**Actor:** System
**Trigger:** Task status changes to done

**Flow:**

1. System compares actual_end_date vs expected_end_date
2. **If actual > expected:**

   * Task marked as delayed
   * Emit `TaskDelayed` event
3. Trigger schedule recalculation for dependents

---

### UC-028: Propagate Schedule Changes

**Actor:** System (Schedule Service)

**Flow:**

1. Receive `TaskDelayed` event
2. Query all dependent tasks (graph traversal)
3. For each dependent task:

   * Shift expected_start_date
   * Shift expected_end_date
4. Persist changes
5. Create ScheduleHistory entry per task
6. Emit `ScheduleChanged` events

**Postcondition:** Project schedule remains consistent

---

### UC-029: Manual Schedule Override

**Actor:** Team Manager

**Flow:**

1. Manager edits expected dates of a task
2. Manager must provide reason
3. System updates task expected dates
4. System creates ScheduleHistory entry
5. System recalculates dependent tasks

---

### UC-030: View Delay Cause Chain

**Actor:** Team Member or Manager

**Flow:**

1. User opens delayed task
2. System retrieves ScheduleHistory entries
3. System reconstructs cause chain

**Example Output:**

```
Task C delayed
↳ caused by Task B
   ↳ caused by Task A (finished 3 days late)
```

---

## 📏 New Business Rules

### BR-022: Schedule Immutability

* Actual dates are immutable once set
* Expected dates can change only via:

  * system propagation
  * manager override

---

### BR-023: Delay Detection

```
if actual_end_date > expected_end_date:
    task.is_delayed = true
```

---

### BR-024: Delay Propagation

* Delays propagate only through **finish_to_start** dependencies
* Propagation is transitive
* Each propagation creates ScheduleHistory

---

### BR-025: Historical Integrity

* ScheduleHistory records are immutable
* History cannot be edited or deleted
* System-generated changes must reference cause

---

## 🏗️ Architecture (Extension)

### New Domain Service: ScheduleService

Responsibilities:

* Recalculate expected dates
* Traverse dependency graph
* Persist schedule changes
* Emit scheduling events

```
ScheduleService
- detect_delay(task)
- propagate_delay(task)
- recalculate_dependents(task)
```

---

### New Events

```
TaskDelayed
ScheduleChanged
ScheduleOverridden
```

These integrate naturally with:

* Email notifications
* Manager dashboard
* Risk indicators

---

## ✅ Design Outcome

With these additions, the system now:

* Explains *why* work is blocked
* Explains *why* projects are late
* Preserves planning vs reality
* Learns from historical execution

This elevates the product from **task management** to **execution intelligence**.
