# Planner Multiplayer - Specification

**Version:** 2.0  
**Focus:** Use Cases, Architecture & Business Logic  
**Last Updated:** January 28, 2026

---

## 📋 Table of Contents

1. [Vision & Core Concepts](#vision--core-concepts)
2. [Domain Model](#domain-model)
3. [Use Cases](#use-cases)
4. [Business Rules](#business-rules)
5. [Architecture](#architecture)
6. [Internationalization (i18n)](#internationalization-i18n)
7. [Events & Integration](#events--integration)

---

## 🎯 Vision & Core Concepts

### What Problem Does This Solve?

**The Coordination Problem:**
- "What should I work on next?"
- "Who is responsible for this?"
- "Why are we blocked?"
- "Where is the project knowledge?"

### The Solution: Four Pillars

#### 1. Role-First Ownership
Tasks belong to **roles**, not individuals.

**Why?**
- Roles persist when people change
- Clear responsibility boundaries
- Enables self-organization
- Reduces single points of failure

**Example:**
```
Task: "Implement payment gateway"
Role: Backend Senior
User: (none initially - anyone with this role can claim it)
```

#### 2. Manager-Defined Execution Order
Ranking defines **what to work on next**, not just importance.

**Why?**
- Eliminates "what's next?" ambiguity
- Aligns team on priorities
- Reduces coordination overhead
- Creates predictable flow

**Example:**
```
Ranked Task List (Backend Senior):
1. Fix critical payment bug [HIGH]
2. Implement OAuth2 [HIGH]  ← Work on this next
3. Add logging to API [MEDIUM]
4. Database optimization [LOW]
```

#### 3. Intelligent Workload Monitoring
Adaptive capacity tracking based on **team's reality**, not fixed numbers.

**Why?**
- Prevents burnout
- Enables data-driven hiring decisions
- Identifies bottlenecks early
- Adapts to team dynamics

**Example:**
```
Backend Senior: 🔴 Impossível (5.5 tasks/person)
└─ Historical baseline: 4.0 tasks/person
└─ Alert: Consider redistribution or hiring
```

#### 4. Dependency-Aware Task Management
Tasks automatically block/unblock based on relationships.

**Why?**
- No wasted effort on blocked work
- Clear dependency visualization
- Automatic workflow management
- Reduces "waiting on X" questions

**Example:**
```
API Design (done) ──blocks──> API Implementation (todo) ──blocks──> Frontend Integration (blocked)
```

#### 5. AI-Powered Progress Tracking (Optional)
Automatic estimation of task completion based on activity.

**Why?**
- Eliminates manual progress updates
- Data-driven project visibility
- Early detection of stalled tasks
- Reduces status meeting overhead

**How it works:**
- **With AI:** System analyzes task notes and estimates progress percentage automatically
- **Without AI:** Users manually update progress as they work
- **Hybrid:** AI estimates can always be overridden manually

**Example:**
```
Task: "Implement OAuth2 Login" [75% complete - AI estimated]

Notes analyzed:
- "Started implementation using authlib"
- "Google provider working, testing GitHub now"
- "Need to add token refresh logic"

AI reasoning: "Implementation is mostly done, testing in progress, 
one feature remaining = ~75% complete"
```

---

## 📦 Domain Model

### Core Entities & Relationships

```
                          ┌─────────────┐
                          │   COMPANY   │
                          │  • Billing  │
                          │  • AI Config│
                          └─────────────┘
                                 │
                                 │ owns
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                            TEAM                                 │
│  • Collaborative unit                                           │
│  • Owns projects, roles, users                                  │
└─────────────────────────────────────────────────────────────────┘
           │
           ├──────────────┬──────────────┬──────────────┐
           ▼              ▼              ▼              ▼
     ┌─────────┐    ┌──────────┐   ┌─────────┐   ┌──────────┐
     │  USER   │    │   ROLE   │   │ PROJECT │   │ SETTINGS │
     └─────────┘    └──────────┘   └─────────┘   └──────────┘
           │              │              │
           │              │              ▼
           │              │         ┌─────────┐
           │              └────────>│  TASK   │<───┐
           │                        └─────────┘    │
           │                             │         │
           └────────────────────────┬────┴─────┬───┘
                                    ▼          ▼
                              ┌──────────┐ ┌────────────┐
                              │   NOTE   │ │ DEPENDENCY │
                              └──────────┘ └────────────┘
```

### Entity Definitions

#### Company
```
Properties:
- id: UUID
- name: string
- slug: string (unique, URL-friendly)
- plan: enum (free, pro, enterprise)
- ai_enabled: boolean (has LLM integration)
- ai_provider: enum (none, anthropic, openai) (optional)
- ai_api_key: string (encrypted, optional)
- billing_email: string
- created_at: timestamp
- updated_at: timestamp

Relationships:
- teams: Team[] (one-to-many)

Business Context:
- Companies are the top-level billing entity
- AI features (like automatic progress tracking) are enabled per company
- Multiple teams can belong to same company (shared billing)
- AI provider can be configured at company level
```

#### Team
```
Properties:
- id: UUID
- company_id: UUID (foreign key)
- name: string
- description: text (optional)
- default_language: string (en, pt-BR, es, etc.)
- created_at: timestamp

Relationships:
- company: Company (belongs to)
- members: User[] (many-to-many)
- roles: Role[] (one-to-many)
- projects: Project[] (one-to-many)
```

#### User
```
Properties:
- id: UUID
- email: string (unique)
- name: string
- preferred_language: string (overrides team default)
- avatar_url: string (optional)
- created_at: timestamp

Relationships:
- teams: Team[] (many-to-many)
- roles: Role[] (many-to-many, per team)
- assigned_tasks: Task[] (optional assignment)
- authored_notes: Note[]
- email_preferences: EmailPreferences
```

#### Role
```
Properties:
- id: UUID
- team_id: UUID
- name: string (e.g., "Backend Developer")
- level: enum (junior, mid, senior, lead, specialist)
- base_capacity: integer (default tasks per person)
- description: text (optional)
- created_at: timestamp

Relationships:
- team: Team
- members: User[] (many-to-many)
- responsible_tasks: Task[] (tasks assigned to this role)

Examples:
- Backend Junior
- Backend Senior
- Frontend Mid
- QA Lead
- DevOps Specialist
```

#### Project
```
Properties:
- id: UUID
- team_id: UUID
- name: string
- description: text (optional)
- status: enum (active, archived)
- created_at: timestamp

Relationships:
- team: Team
- tasks: Task[] (one-to-many)
```

#### Task
```
Properties:
- id: UUID
- project_id: UUID
- title: string
- description: text
- status: enum (todo, doing, blocked, done)
- priority: enum (low, medium, high)
- rank_index: float (for ordering)
- completion_percentage: integer (0-100, optional)
- completion_source: enum (manual, ai, null)
- due_date: timestamp (optional)
- role_responsible_id: UUID (required)
- user_responsible_id: UUID (optional)
- blocked_reason: text (when status = blocked)
- created_at: timestamp
- updated_at: timestamp
- completed_at: timestamp (when status = done)

Relationships:
- project: Project
- role_responsible: Role (required)
- user_responsible: User (optional)
- notes: Note[] (timeline)
- dependencies: TaskDependency[] (what this task depends on)
- dependents: TaskDependency[] (what depends on this task)

Invariants:
- role_responsible is always required
- user_responsible must have the role_responsible role
- rank_index must be unique within project
- completed_at is set only when status changes to done
- completion_percentage must be between 0 and 100 (if not null)
- completion_source tracks how percentage was set (manual vs AI)
```

#### TaskDependency
```
Properties:
- id: UUID
- task_id: UUID (the dependent task)
- depends_on_task_id: UUID (the blocking task)
- dependency_type: enum (blocks, relates_to)
- created_at: timestamp

Relationships:
- task: Task (the dependent)
- depends_on_task: Task (the blocker)

Constraints:
- task_id ≠ depends_on_task_id (no self-dependencies)
- No circular dependencies allowed
```

#### Note
```
Properties:
- id: UUID
- task_id: UUID
- author_id: UUID (null for system notes)
- content: text
- note_type: enum (comment, status_change, assignment, blocker, system)
- created_at: timestamp
- updated_at: timestamp

Relationships:
- task: Task
- author: User (optional)
```

#### EmailPreferences
```
Properties:
- id: UUID
- user_id: UUID
- task_created: boolean (default: true)
- task_assigned: boolean (default: true)
- due_date_reminder: boolean (default: true)
- task_completed: boolean (default: false)
- task_blocked: boolean (default: true)
- task_unblocked: boolean (default: true)
- digest_mode: enum (none, daily, weekly) (default: daily)
- created_at: timestamp
- updated_at: timestamp

Relationships:
- user: User
```

---

## 🎬 Use Cases

### UC-001: Create Team
**Actor:** User  
**Precondition:** User is authenticated  

**Flow:**
1. User provides team name, description (optional), default language
2. System creates team
3. System assigns user as team manager
4. System creates default roles (optional: Backend, Frontend, QA)
5. System returns team details

**Postcondition:** User is manager of new team

---

### UC-002: Invite User to Team
**Actor:** Team Manager  
**Precondition:** User is manager of team  

**Flow:**
1. Manager provides email address and roles to assign
2. System validates email and roles exist
3. System sends invitation email (in team's default language)
4. Invited user accepts invitation
5. System adds user to team with specified roles

**Postcondition:** User is member of team with assigned roles

**Alternative Flow:**
- If user doesn't exist, create account first
- If user already in team, update roles

---

### UC-003: Create Role
**Actor:** Team Manager  
**Precondition:** User is manager of team  

**Flow:**
1. Manager provides role name, level, base capacity
2. System validates uniqueness (name + level per team)
3. System creates role
4. System returns role details

**Examples:**
- Backend Senior (base_capacity: 5)
- Frontend Junior (base_capacity: 3)
- DevOps Specialist (base_capacity: 4)

---

### UC-004: Create Project
**Actor:** Team Manager  
**Precondition:** User is manager of team  

**Flow:**
1. Manager provides project name, description
2. System creates project for team
3. System initializes empty task list
4. System returns project details

---

### UC-005: Create Task
**Actor:** Team Manager or User with permission  
**Precondition:** User is member of team  

**Flow:**
1. User provides:
   - title (required)
   - description (optional)
   - role_responsible (required)
   - priority (default: medium)
   - due_date (optional)
2. System assigns next available rank_index
3. System creates task with status = todo
4. System emits TaskCreated event
5. System creates system note "Task created by {user}"
6. System returns task details

**Postcondition:** Task exists and is visible to team

**Business Rules Applied:**
- BR-001: Role must belong to project's team
- BR-005: New tasks start with status = todo

---

### UC-006: Claim Task
**Actor:** Team Member  
**Precondition:** 
- User has role matching task's role_responsible
- Task has no user_responsible assigned
- Task status is todo or blocked

**Flow:**
1. User selects task from their role's queue
2. System validates user has required role
3. System assigns user_responsible = user
4. System changes status from todo → doing
5. System emits TaskAssigned event
6. System creates note "Task claimed by {user}"
7. System returns updated task

**Postcondition:** User is working on task

**Business Rules Applied:**
- BR-002: User must have role to claim task
- BR-006: Claiming task changes status to doing

---

### UC-007: Update Task Status
**Actor:** Team Member (assigned to task)  
**Precondition:** User is assigned to task or is manager  

**Flow:**
1. User changes task status
2. System validates status transition (see BR-007)
3. System updates task status
4. System updates timestamps (completed_at if done)
5. System emits TaskStatusChanged event
6. System creates note "{user} changed status from {old} to {new}"
7. **If new status = done:**
   - Check dependent tasks (UC-015)
   - Trigger unblock logic
8. System returns updated task

**Postcondition:** Task has new status

**Valid Transitions (BR-007):**
```
todo → doing, blocked
doing → done, blocked
blocked → todo
done → (terminal, cannot change)
```

---

### UC-008: Add Task Note
**Actor:** Team Member  
**Precondition:** User is member of team  

**Flow:**
1. User provides note content
2. System creates note with:
   - task_id
   - author_id = user
   - note_type = comment
   - content = user input
3. System emits NoteAdded event (optional notification)
4. System returns note details

**Postcondition:** Note is visible in task timeline

---

### UC-009: Rank Tasks
**Actor:** Team Manager  
**Precondition:** User is manager, project has tasks  

**Flow:**
1. Manager reorders tasks (drag-and-drop or API)
2. System calculates new rank_index values
3. System updates affected tasks
4. System emits TasksReranked event
5. System returns updated task list

**Postcondition:** Tasks are in new order

**Business Rules Applied:**
- BR-003: Ranking defines execution order
- BR-011: rank_index calculation algorithm

**Implementation Notes:**
- Use float-based ranking (see BR-011)
- Trigger rebalancing if ranks get too close (<0.001)

---

### UC-010: Add Task Dependency
**Actor:** Team Manager or Task Owner  
**Precondition:** Both tasks exist in same team  

**Flow:**
1. User specifies task A depends on task B
2. System validates no circular dependency (BR-008)
3. System creates TaskDependency record
4. **If task B is not done:**
   - System changes task A status to blocked
   - System sets blocked_reason = "Waiting on Task #B"
   - System emits TaskBlocked event
5. System creates note "Dependency added: Task #{B}"
6. System returns dependency details

**Postcondition:** Task A cannot be worked until Task B is done

**Business Rules Applied:**
- BR-008: No circular dependencies
- BR-009: Blocking dependencies auto-block tasks

---

### UC-011: Calculate Workload Health
**Actor:** System (scheduler) or Manager (on-demand)  
**Precondition:** Team has tasks and role assignments  

**Flow:**
1. System counts active tasks for role (status = todo, doing, blocked)
2. System counts users assigned to role
3. System calculates tasks_per_person = active_tasks / users
4. System retrieves historical baseline for role (BR-010)
5. System determines health status:
   ```
   tasks_per_person ≤ baseline * 0.8  → tranquilo (green)
   tasks_per_person ≤ baseline        → saudável (yellow)
   tasks_per_person ≤ baseline * 1.3  → apertado (orange)
   tasks_per_person > baseline * 1.3  → impossível (red)
   ```
6. **If status = impossível:**
   - System emits WorkloadAlert event
   - System notifies managers
7. System returns workload health data

**Postcondition:** Workload status is calculated and visible

**Business Rules Applied:**
- BR-010: Adaptive workload calculation

---

### UC-012: Send Email Notification
**Actor:** System (event handler)  
**Trigger:** Domain event (TaskCreated, TaskAssigned, etc.)  

**Flow:**
1. Event is emitted (e.g., TaskAssigned)
2. Email handler receives event
3. System checks user's email preferences
4. **If preference enabled and not in digest mode:**
   - System loads email template
   - System translates template to user's language (UC-017)
   - System populates template with event data
   - System sends email via provider
5. **If digest mode:**
   - System queues event for digest
6. System logs email sent/queued

**Postcondition:** User receives notification (immediate or digest)

---

### UC-013: Generate Daily Digest
**Actor:** System (scheduler)  
**Schedule:** Daily at 9 AM (user's timezone)  

**Flow:**
1. Scheduler triggers digest generation
2. System queries users with digest_mode = daily
3. **For each user:**
   - System collects events from last 24 hours
   - System groups events by type
   - System loads digest template
   - System translates to user's language (UC-017)
   - System populates template with aggregated data
   - System sends digest email
4. System clears processed events from queue

**Postcondition:** Users receive summary of yesterday's activity

---

### UC-014: Check Due Dates
**Actor:** System (scheduler)  
**Schedule:** Every hour  

**Flow:**
1. Scheduler triggers due date check
2. System queries tasks where:
   - due_date is within next 48 hours
   - status ≠ done
   - not already notified today
3. **For each task:**
   - System emits DueDateApproaching event
   - System creates reminder note (optional)
   - System sends notification (via UC-012)
4. System marks tasks as notified

**Postcondition:** Users are reminded of upcoming deadlines

---

### UC-015: Unblock Dependent Tasks
**Actor:** System (automatic trigger)  
**Trigger:** Task status changes to done  

**Flow:**
1. Task #{X} status changes to done
2. System queries all tasks that depend on #{X}
3. **For each dependent task:**
   - System checks if ALL dependencies are done
   - **If all dependencies done:**
     - System changes status from blocked → todo
     - System clears blocked_reason
     - System emits TaskUnblocked event
     - System creates note "Task unblocked - dependency #{X} completed"
     - System notifies assigned user (if exists)
4. System returns list of unblocked tasks

**Postcondition:** Previously blocked tasks are now ready to work

**Business Rules Applied:**
- BR-009: Auto-unblock when dependencies resolve

---

### UC-016: Request AI Ranking Suggestion (Optional)
**Actor:** Team Manager  
**Precondition:** AI integration enabled, project has unranked tasks  

**Flow:**
1. Manager clicks "Suggest Ranking" button
2. System collects context:
   - All tasks in project (status = todo or blocked)
   - Task dependencies
   - Current workload per role
   - Due dates
3. System sends prompt to LLM:
   ```
   "Given these tasks and constraints, suggest optimal execution order 
   considering: dependencies, due dates, workload balance, risk mitigation"
   ```
4. LLM returns suggested task order (array of task IDs)
5. System displays suggestion side-by-side with current ranking
6. Manager reviews and can:
   - Accept suggestion (apply ranking)
   - Manually adjust
   - Dismiss
7. **If accepted:** System applies ranking (UC-009)

**Postcondition:** Manager has AI-suggested ranking to consider

**Note:** This is an optional feature and should not block MVP

---

### UC-017: Translate System Text
**Actor:** System (on every UI render or email generation)  
**Precondition:** User has preferred_language or team has default_language  

**Flow:**
1. System needs to display/send text (e.g., email, UI label)
2. System determines target language:
   - Use user.preferred_language if set
   - Else use team.default_language
   - Else fallback to 'en'
3. System loads translation dictionary for language
4. System looks up translation key
5. **If translation exists:** Return translated text
6. **If translation missing:** Return English fallback + log warning
7. System returns localized text

**Postcondition:** User sees interface in their language

**Examples:**
```
Key: "task.status.todo"
en: "To Do"
pt-BR: "A Fazer"
es: "Por Hacer"

Key: "email.task_assigned.subject"
en: "Task assigned to you: {title}"
pt-BR: "Tarefa atribuída a você: {title}"
es: "Tarea asignada a ti: {title}"
```

---

### UC-018: View Manager Dashboard
**Actor:** Team Manager  
**Precondition:** User is manager of team  

**Flow:**
1. Manager navigates to dashboard
2. System calculates metrics:
   - **Team Health:** tasks created/completed (last 7 days)
   - **Workload:** health status per role (UC-011)
   - **Activity Feed:** recent task changes (last 20 events)
   - **Risk Indicators:** 
     - Tasks without assignee approaching due date
     - Overloaded roles (impossível status)
     - Long-blocked tasks (>3 days)
3. System translates all labels to manager's language (UC-017)
4. System renders dashboard with data
5. System enables real-time updates (polling every 5s when active)

**Postcondition:** Manager has overview of team status

---

### UC-019: View My Tasks
**Actor:** Team Member  
**Precondition:** User is member of at least one team  

**Flow:**
1. User navigates to "My Tasks" view
2. System queries tasks where:
   - user_responsible = user (assigned tasks)
   - OR role_responsible in user.roles AND user_responsible is null (available)
3. System groups tasks:
   - **Urgent:** status ≠ done, due_date within 2 days
   - **In Progress:** status = doing, assigned to user
   - **Available:** status = todo, role match, not assigned
   - **Blocked:** status = blocked, assigned to user
4. System orders by rank_index within each group
5. System translates UI (UC-017)
6. System renders task list

**Postcondition:** User sees their work queue

---

### UC-020: Calculate Historical Baseline
**Actor:** System (scheduler)  
**Schedule:** Daily at midnight  

**Flow:**
1. Scheduler triggers baseline calculation
2. System queries all teams and roles
3. **For each team + role combination:**
   - Query tasks completed in last 30 days
   - Count total completed tasks
   - Calculate average users in role during period
   - Calculate: avg_tasks_per_person = completed / (users * 30)
   - **If sufficient data (>10 tasks):**
     - Save WorkloadBaseline record
   - **Else:** Use role.base_capacity as baseline
4. System logs baseline calculations

**Postcondition:** Workload health uses updated baselines

**Business Rules Applied:**
- BR-010: Baselines adapt to team reality

---

### UC-021: Create Company
**Actor:** Admin User  
**Precondition:** User has admin privileges  

**Flow:**
1. User provides company name, plan, billing email
2. System creates unique slug from name
3. System creates company with:
   - ai_enabled = false (default)
   - ai_provider = none
   - plan as specified
4. System returns company details

**Postcondition:** Company exists and can own teams

---

### UC-022: Enable AI for Company
**Actor:** Company Admin  
**Precondition:** User is admin of company, company has pro/enterprise plan  

**Flow:**
1. Admin selects AI provider (anthropic, openai)
2. Admin provides API key
3. System validates API key by test call
4. **If valid:**
   - System encrypts and stores API key
   - System sets ai_enabled = true
   - System sets ai_provider
5. **If invalid:**
   - System returns error message
6. System returns updated company settings

**Postcondition:** Company can use AI features

**Business Rules Applied:**
- BR-017: AI features require valid API key

---

### UC-023: Update Task Progress (Manual)
**Actor:** Team Member (assigned to task)  
**Precondition:** User is assigned to task  

**Flow:**
1. User provides completion_percentage (0-100)
2. System validates:
   - Value is between 0-100
   - Task is not in done status
3. System updates task:
   - completion_percentage = user input
   - completion_source = 'manual'
   - updated_at = now()
4. System emits TaskProgressUpdated event
5. System creates note "{user} updated progress to {percentage}%"
6. System returns updated task

**Postcondition:** Task shows manual progress percentage

**Business Rules Applied:**
- BR-018: Manual progress tracking

---

### UC-024: Analyze Task Progress with AI
**Actor:** System (scheduled or on-demand)  
**Trigger:** Task notes added OR periodic check (daily)  
**Precondition:** Company has ai_enabled = true  

**Flow:**
1. System identifies task to analyze:
   - Task status = 'doing'
   - Has notes/updates since last analysis
   - Company has AI enabled
2. System collects context:
   - Task title and description
   - All task notes (chronologically)
   - Current completion_percentage (if set)
3. System sends prompt to LLM:
   ```
   "Analyze this task's progress based on the notes and updates.
   
   Task: {title}
   Description: {description}
   Current progress: {current_percentage}%
   
   Notes timeline:
   {notes_chronologically}
   
   Based on the work described, estimate completion percentage (0-100).
   Consider: implementation status, testing, blockers mentioned, 
   remaining work described.
   
   Return only a JSON: {\"percentage\": <0-100>, \"reasoning\": \"brief explanation\"}"
   ```
4. LLM returns estimated percentage and reasoning
5. **If estimate differs from current by >10%:**
   - System updates task:
     - completion_percentage = AI estimate
     - completion_source = 'ai'
     - updated_at = now()
   - System emits TaskProgressUpdated event
   - System creates note "AI estimated progress at {percentage}% - {reasoning}"
6. **Else:** No update needed
7. System returns analysis result

**Postcondition:** Task has AI-estimated progress percentage

**Business Rules Applied:**
- BR-019: AI progress estimation

**Alternative Flow:**
- If AI unavailable or errors, log and skip update
- User can always override AI estimate with manual update

---

### UC-025: View Task Progress History
**Actor:** Team Member  
**Precondition:** User is member of team  

**Flow:**
1. User opens task detail view
2. System retrieves task with:
   - Current completion_percentage and source
   - Progress updates from notes (filtered by type)
3. System displays:
   - Current progress indicator (0-100%)
   - Source badge (Manual/AI)
   - Timeline of progress updates
4. **If AI-estimated:**
   - Show "Estimated by AI" badge
   - Option to manually override
5. System renders progress chart (optional)

**Postcondition:** User sees progress tracking information

---

## 📏 Business Rules

### BR-001: Role Assignment Constraints
- A task's `role_responsible` must belong to the same team as the task's project
- A task's `user_responsible` must have the `role_responsible` role
- A user can have multiple roles in the same team
- A role belongs to exactly one team

### BR-002: Task Claiming
- Users can only claim tasks where:
  - Task's `role_responsible` is in user's roles
  - Task's `user_responsible` is null (not yet claimed)
  - Task's status is `todo` or `blocked`
- Claiming a task automatically assigns the user and changes status to `doing`

### BR-003: Task Ranking
- Ranking defines **execution order**, not importance
- Within a project, tasks should be consumed top-down by role
- Multiple tasks can have the same priority but different ranks
- Ranking is visible to all team members

### BR-004: Task Status Lifecycle
```
[todo] ──> [doing] ──> [done]
   │          │
   └──> [blocked] ──┘

Initial state: todo
Terminal state: done (cannot transition out)
```

### BR-005: Task Creation Defaults
- New tasks start with status = `todo`
- If no rank_index provided, assign to end of list
- Priority defaults to `medium` if not specified
- Tasks must have `role_responsible` (required)
- Tasks can have `user_responsible` = null (unclaimed)

### BR-006: Task Status Transitions
```
Valid transitions:
- todo → doing (user claims or manually starts)
- todo → blocked (dependency or manual block)
- doing → done (task completed)
- doing → blocked (encountered blocker)
- blocked → todo (blocker resolved)

Invalid transitions (throw error):
- done → * (done is terminal)
- Any state → Any invalid state
```

### BR-007: Task Completion
- When task status changes to `done`:
  - Set `completed_at` = current timestamp
  - Calculate lead time (completed_at - created_at)
  - Check dependent tasks (may trigger unblocking)
  - Emit `TaskCompleted` event
- Once done, task cannot change status

### BR-008: Dependency Constraints
- A task cannot depend on itself
- Circular dependencies are not allowed
  - Example: Task A depends on B, B depends on C, C depends on A ❌
- Dependencies must be within the same team (can be across projects)
- Dependency type `blocks` means dependent task cannot start until blocker is done

### BR-009: Automatic Blocking
- When a blocking dependency is added:
  - **If** blocker status ≠ done
  - **Then** dependent task status → blocked
  - Set `blocked_reason` = "Waiting on Task #{blocker_id}"
- When a blocker task completes (status → done):
  - Check all dependent tasks
  - **If** all dependencies for a task are done
  - **Then** task status → todo (unblocked)
  - Clear `blocked_reason`

### BR-010: Workload Health Calculation
```python
# Pseudocode
tasks_per_person = active_tasks_for_role / users_in_role
baseline = historical_baseline(role, last_30_days)

if tasks_per_person <= baseline * 0.8:
    health = "tranquilo" (green)
elif tasks_per_person <= baseline:
    health = "saudável" (yellow)
elif tasks_per_person <= baseline * 1.3:
    health = "apertado" (orange)
else:
    health = "impossível" (red)
```

**Baseline Calculation:**
- Use last 30 days of completed tasks
- Calculate average tasks per person per week
- Update daily via scheduler
- If insufficient data (<10 tasks), use role.base_capacity

### BR-011: Rank Index Algorithm
```python
# Float-based ranking allows insertion without renumbering

def calculate_rank_index(position: int, existing_tasks: List[Task]) -> float:
    if not existing_tasks:
        return 1.0
    
    if position == 0:
        # Insert at beginning
        return existing_tasks[0].rank_index - 1.0
    
    if position >= len(existing_tasks):
        # Insert at end
        return existing_tasks[-1].rank_index + 1.0
    
    # Insert between two tasks
    prev_rank = existing_tasks[position - 1].rank_index
    next_rank = existing_tasks[position].rank_index
    return (prev_rank + next_rank) / 2.0

# Rebalancing (when ranks get too close)
def rebalance_ranks(project_id: UUID):
    """Call when adjacent ranks differ by <0.001"""
    tasks = get_tasks_ordered_by_rank(project_id)
    for idx, task in enumerate(tasks):
        task.rank_index = (idx + 1) * 10.0  # 10, 20, 30, ...
```

### BR-012: Email Notification Rules
- Emails are sent based on user's `EmailPreferences`
- **Immediate mode:** Send email when event occurs (if preference enabled)
- **Digest mode:** Queue events and send summary at scheduled time
- All emails are translated to user's `preferred_language`
- System respects user opt-outs (preference = false)

### BR-013: Email Digest Aggregation
- **Daily digest:** Sent at 9 AM in user's timezone
- **Weekly digest:** Sent Monday 9 AM in user's timezone
- Digest groups events by type:
  - Tasks assigned to you (count)
  - Tasks completed (count)
  - Upcoming due dates (list)
  - Tasks blocked (count)
- After sending, clear queued events for user

### BR-014: Language Fallback
```
Determine user's language:
1. user.preferred_language (highest priority)
2. team.default_language (if user's team)
3. 'en' (system fallback)

If translation key not found:
1. Try English ('en') as fallback
2. Log missing translation warning
3. Return key itself as last resort
```

### BR-015: Task Notes
- System notes (`author_id = null`) are created automatically for:
  - Status changes
  - Assignments
  - Dependency changes
  - Blocking/unblocking
- User notes (`author_id = user`) are manual comments
- Notes are immutable (can be deleted but not edited)
- Notes are ordered by `created_at` (timeline)

### BR-016: Manager Permissions
- Managers can:
  - Create/edit/delete projects
  - Create/edit/delete roles
  - Assign tasks to any user
  - Rank tasks
  - View team dashboard
  - Invite users to team
- Team members can:
  - Claim tasks from their roles
  - Update tasks they're assigned to
  - Add notes to tasks
  - View team projects and tasks

### BR-017: AI Features Access Control
- AI features (progress estimation, ranking suggestions) require:
  - Company has `ai_enabled = true`
  - Company has valid `ai_api_key` for selected provider
  - Company plan is pro or enterprise
- Free plan companies cannot enable AI features
- Invalid/expired API keys automatically disable AI features

### BR-018: Manual Progress Tracking
- Users can manually set `completion_percentage` (0-100) for tasks they're assigned to
- Manual updates set `completion_source = 'manual'`
- Manual updates always take precedence over AI estimates
- Progress percentage cannot be set for tasks with status = 'done' (always 100%)
- Progress percentage cannot be set for tasks with status = 'todo' (unless claimed)

### BR-019: AI Progress Estimation
- AI can estimate task progress based on:
  - Task notes and updates
  - Description and current status
  - Time elapsed vs estimated time
- AI estimates set `completion_source = 'ai'`
- AI only updates if estimate differs from current by >10%
- Users can always override AI estimates with manual input
- AI estimation respects rate limits and handles API failures gracefully
- AI creates a system note explaining its reasoning

**AI Prompt Strategy:**
```
Context: Task with title, description, notes timeline
Goal: Estimate completion percentage (0-100)
Considerations:
- Implementation milestones mentioned
- Testing/review status
- Blockers or issues raised
- Remaining work described
- Time-based progress if applicable

Output: JSON with percentage and brief reasoning
```

### BR-020: Progress Percentage Display
- Progress is displayed as:
  - Visual bar (0-100%)
  - Numeric percentage
  - Source badge (Manual/AI/None)
- When completion_source = 'ai', show estimated indicator
- When completion_source = 'manual', show user-set indicator
- When completion_percentage is null, show "Not tracked"
- Progress percentage automatically becomes 100% when status changes to 'done'

### BR-021: Company-Team Relationship
- Every team must belong to exactly one company
- Teams inherit AI capabilities from their company
- Company admins can manage all teams within company
- Billing is handled at company level
- AI usage quota is tracked per company, not per team

---

## 🏗️ Architecture

### Architectural Style: Layered + Event-Driven

```
┌─────────────────────────────────────────────────────────────┐
│                      Presentation Layer                     │
│  • REST API (JSON)                                          │
│  • Request validation                                       │
│  • Response formatting                                      │
│  • Authentication & Authorization                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Application Layer                      │
│  • Use Case Handlers (one per use case)                    │
│  • Orchestration logic                                      │
│  • Transaction management                                   │
│  • Event emission                                           │
└─────────────────────────────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
┌─────────────────────────┐   ┌──────────────────────────┐
│     Domain Layer        │   │     Event Bus            │
│  • Business Rules       │   │  • Event dispatching     │
│  • Domain Models        │   │  • Handler registration  │
│  • Calculations         │   └──────────────────────────┘
└─────────────────────────┘              │
                │                        ▼
                ▼              ┌──────────────────────────┐
┌─────────────────────────┐   │   Event Handlers         │
│  Infrastructure Layer   │   │  • Email notifications   │
│  • Repositories         │   │  • Audit logging         │
│  • Database access      │   │  • Webhooks (future)     │
│  • Email service        │   └──────────────────────────┘
│  • Translation service  │
└─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│                         Database                            │
│  • PostgreSQL (persistent storage)                          │
│  • Redis (cache, job queue)                                 │
└─────────────────────────────────────────────────────────────┘
```

---

### Layer Responsibilities

#### 1. Presentation Layer
**Responsibility:** Handle HTTP requests/responses

**Components:**
- Controllers/Routers
- Request DTOs (Data Transfer Objects)
- Response DTOs
- Middleware (auth, logging, error handling)

**Example:**
```python
# Pseudocode
class TaskController:
    def create_task(request):
        # 1. Validate request
        dto = CreateTaskDTO.from_request(request)
        
        # 2. Call use case
        task = create_task_use_case.execute(dto, current_user)
        
        # 3. Return response
        return TaskResponse.from_domain(task), 201
```

---

#### 2. Application Layer
**Responsibility:** Orchestrate use cases

**Components:**
- Use Case Handlers (one class per use case)
- Application Services (coordinate multiple use cases)
- Transaction boundaries
- Event emission

**Example:**
```python
# Pseudocode
class CreateTaskUseCase:
    def __init__(self, task_repo, event_bus, translator):
        self.task_repo = task_repo
        self.event_bus = event_bus
        self.translator = translator
    
    def execute(self, dto: CreateTaskDTO, user: User) -> Task:
        # 1. Load dependencies
        project = self.task_repo.get_project(dto.project_id)
        role = self.task_repo.get_role(dto.role_id)
        
        # 2. Validate business rules
        if role.team_id != project.team_id:
            raise ValidationError("Role must belong to project's team")
        
        # 3. Calculate rank
        existing_tasks = self.task_repo.get_tasks_by_project(project.id)
        rank_index = calculate_rank_index(len(existing_tasks), existing_tasks)
        
        # 4. Create domain object
        task = Task(
            project_id=project.id,
            role_responsible_id=role.id,
            title=dto.title,
            description=dto.description,
            priority=dto.priority or Priority.MEDIUM,
            rank_index=rank_index,
            status=TaskStatus.TODO
        )
        
        # 5. Persist
        self.task_repo.save(task)
        
        # 6. Emit event
        self.event_bus.emit(TaskCreated(
            task_id=task.id,
            project_id=project.id,
            role_id=role.id,
            title=task.title,
            created_by=user.id
        ))
        
        # 7. Return
        return task
```

---

#### 3. Domain Layer
**Responsibility:** Encode business rules

**Components:**
- Domain Models (entities)
- Value Objects
- Domain Services (complex calculations)
- Business Rule validators

**Key Domain Models:**

```python
# Pseudocode
class Task:
    """Domain model for Task"""
    
    def claim(self, user: User):
        """Business logic for claiming a task (BR-002)"""
        if self.role_responsible not in user.roles:
            raise BusinessRuleViolation("User doesn't have required role")
        
        if self.user_responsible is not None:
            raise BusinessRuleViolation("Task already claimed")
        
        if self.status not in [TaskStatus.TODO, TaskStatus.BLOCKED]:
            raise BusinessRuleViolation("Task not in claimable state")
        
        self.user_responsible = user
        self.status = TaskStatus.DOING
        self.updated_at = now()
    
    def complete(self):
        """Business logic for completing a task (BR-007)"""
        if self.status != TaskStatus.DOING:
            raise BusinessRuleViolation("Can only complete tasks in DOING state")
        
        self.status = TaskStatus.DONE
        self.completed_at = now()
        self.updated_at = now()
    
    def block(self, reason: str):
        """Business logic for blocking a task (BR-006)"""
        if self.status not in [TaskStatus.TODO, TaskStatus.DOING]:
            raise BusinessRuleViolation("Cannot block task in current state")
        
        self.status = TaskStatus.BLOCKED
        self.blocked_reason = reason
        self.updated_at = now()

class WorkloadCalculator:
    """Domain service for workload calculations (BR-010)"""
    
    def calculate_health(
        self, 
        role: Role, 
        active_tasks: int, 
        users_count: int,
        baseline: float
    ) -> WorkloadHealth:
        
        if users_count == 0:
            return WorkloadHealth(status="no_users", tasks_per_person=0)
        
        tasks_per_person = active_tasks / users_count
        
        if tasks_per_person <= baseline * 0.8:
            status = "tranquilo"
        elif tasks_per_person <= baseline:
            status = "saudável"
        elif tasks_per_person <= baseline * 1.3:
            status = "apertado"
        else:
            status = "impossível"
        
        return WorkloadHealth(
            status=status,
            tasks_per_person=tasks_per_person,
            baseline=baseline
        )

class AIProgressAnalyzer:
    """Domain service for AI-based progress estimation (BR-019)"""
    
    def analyze_task_progress(
        self,
        task: Task,
        notes: List[Note],
        llm_client: LLMClient
    ) -> Optional[ProgressEstimate]:
        """
        Analyze task progress using AI based on notes and context.
        Returns None if AI is unavailable or analysis fails.
        """
        # Build context
        context = {
            "title": task.title,
            "description": task.description,
            "current_progress": task.completion_percentage or 0,
            "status": task.status,
            "notes": [
                {
                    "timestamp": note.created_at,
                    "author": note.author.name if note.author else "System",
                    "content": note.content
                }
                for note in notes
            ]
        }
        
        # Build prompt
        prompt = f"""
        Analyze this task's progress based on the notes and updates.
        
        Task: {context['title']}
        Description: {context['description']}
        Current progress: {context['current_progress']}%
        Status: {context['status']}
        
        Notes timeline (chronological):
        {self._format_notes(context['notes'])}
        
        Based on the work described, estimate completion percentage (0-100).
        Consider:
        - Implementation status and milestones reached
        - Testing and review mentions
        - Blockers or issues mentioned
        - Remaining work described
        
        Return only valid JSON: {{"percentage": <0-100>, "reasoning": "brief explanation"}}
        """
        
        try:
            # Call LLM
            response = llm_client.complete(prompt)
            result = json.loads(response)
            
            # Validate response
            percentage = int(result['percentage'])
            reasoning = result['reasoning']
            
            if not (0 <= percentage <= 100):
                raise ValueError("Percentage out of range")
            
            return ProgressEstimate(
                percentage=percentage,
                reasoning=reasoning,
                confidence="high" if abs(percentage - context['current_progress']) <= 20 else "low"
            )
            
        except Exception as e:
            logger.error(f"AI progress analysis failed: {e}")
            return None
    
    def should_update_progress(
        self,
        current: Optional[int],
        estimated: int,
        threshold: int = 10
    ) -> bool:
        """
        Determine if progress should be updated based on estimate.
        BR-019: Only update if difference > threshold (default 10%)
        """
        if current is None:
            return True
        
        return abs(estimated - current) > threshold
    
    def _format_notes(self, notes: List[dict]) -> str:
        """Format notes for LLM context"""
        formatted = []
        for note in notes:
            formatted.append(
                f"[{note['timestamp']}] {note['author']}: {note['content']}"
            )
        return "\n".join(formatted)
```

---

#### 4. Infrastructure Layer
**Responsibility:** Technical implementation details

**Components:**
- Repositories (database access)
- Email Service (SMTP/API provider)
- Translation Service (i18n)
- Cache Service
- Job Queue

---

### Event-Driven Architecture

#### Domain Events

```python
# Pseudocode
@dataclass
class DomainEvent:
    timestamp: datetime
    user_id: Optional[UUID]

@dataclass
class TaskCreated(DomainEvent):
    task_id: UUID
    project_id: UUID
    role_id: UUID
    title: str

@dataclass
class TaskAssigned(DomainEvent):
    task_id: UUID
    user_id: UUID

@dataclass
class TaskStatusChanged(DomainEvent):
    task_id: UUID
    old_status: TaskStatus
    new_status: TaskStatus

@dataclass
class TaskCompleted(DomainEvent):
    task_id: UUID
    completed_by: UUID
    lead_time_days: float

@dataclass
class TaskBlocked(DomainEvent):
    task_id: UUID
    reason: str

@dataclass
class TaskUnblocked(DomainEvent):
    task_id: UUID

@dataclass
class DueDateApproaching(DomainEvent):
    task_id: UUID
    days_until_due: int

@dataclass
class WorkloadAlert(DomainEvent):
    team_id: UUID
    role_id: UUID
    health_status: str

@dataclass
class TaskProgressUpdated(DomainEvent):
    task_id: UUID
    completion_percentage: int
    source: str  # 'manual' or 'ai'
    reasoning: Optional[str]  # AI reasoning if source='ai'
```

#### Event Bus (In-Memory for MVP)

```python
# Pseudocode
class EventBus:
    def __init__(self):
        self._handlers = defaultdict(list)
    
    def subscribe(self, event_type: Type, handler: Callable):
        self._handlers[event_type].append(handler)
    
    def emit(self, event: DomainEvent):
        event_type = type(event)
        for handler in self._handlers[event_type]:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error handling {event_type}: {e}")
```

#### Event Handlers

```python
# Pseudocode
class EmailNotificationHandler:
    def handle_task_assigned(self, event: TaskAssigned):
        user = self.user_repo.get_by_id(event.user_id)
        prefs = user.email_preferences
        
        if not prefs.task_assigned:
            return  # User opted out
        
        if prefs.digest_mode != DigestMode.NONE:
            self.queue_for_digest(user, event)
            return
        
        task = self.task_repo.get_by_id(event.task_id)
        self.email_service.send_task_assigned_email(task, user)

class DependencyHandler:
    def handle_task_completed(self, event: TaskCompleted):
        """Implements UC-015: Unblock dependent tasks"""
        dependents = self.task_repo.get_dependent_tasks(event.task_id)
        
        for dependent in dependents:
            all_deps = self.task_repo.get_dependencies(dependent.id)
            all_done = all(dep.depends_on_task.status == TaskStatus.DONE 
                          for dep in all_deps)
            
            if all_done and dependent.status == TaskStatus.BLOCKED:
                dependent.unblock()
                self.task_repo.save(dependent)
                self.event_bus.emit(TaskUnblocked(task_id=dependent.id))

class AIProgressHandler:
    """Handles AI progress estimation triggers"""
    
    def handle_note_added(self, event: NoteAdded):
        """
        When a note is added to a task, trigger AI progress analysis
        if the task is active and company has AI enabled
        """
        task = self.task_repo.get_by_id(event.task_id)
        
        # Only analyze active tasks
        if task.status != TaskStatus.DOING:
            return
        
        # Check if company has AI enabled
        company = self.company_repo.get_by_team(task.project.team_id)
        if not company.ai_enabled:
            return
        
        # Trigger analysis (async job)
        self.job_queue.enqueue(
            'analyze_task_progress',
            task_id=task.id
        )
```

---

### Scheduler Jobs

```python
# Pseudocode
class SchedulerJobs:
    """Background jobs for automation"""
    
    def check_due_dates_job(self):
        """Runs every hour - UC-014"""
        tasks = self.task_repo.get_tasks_due_soon(hours=48)
        
        for task in tasks:
            if self.already_notified_today(task):
                continue
            
            self.event_bus.emit(DueDateApproaching(
                task_id=task.id,
                days_until_due=calculate_days_until(task.due_date),
                timestamp=now(),
                user_id=None
            ))
            
            self.mark_notified(task)
    
    def send_daily_digests_job(self):
        """Runs daily at 9 AM - UC-013"""
        users = self.user_repo.get_users_with_digest(DigestMode.DAILY)
        
        for user in users:
            events = self.get_queued_events(user.id, hours=24)
            
            if not events:
                continue
            
            grouped = self.group_events(events)
            self.email_service.send_daily_digest(user, grouped)
            self.clear_queued_events(user.id)
    
    def calculate_baselines_job(self):
        """Runs daily at midnight - UC-020"""
        teams = self.team_repo.get_all()
        
        for team in teams:
            roles = self.role_repo.get_by_team(team.id)
            
            for role in roles:
                baseline = self.calculate_baseline(team, role, days=30)
                
                self.baseline_repo.save(WorkloadBaseline(
                    team_id=team.id,
                    role_id=role.id,
                    avg_tasks_per_person=baseline,
                    period_start=now() - timedelta(days=30),
                    period_end=now()
                ))
    
    def analyze_task_progress_job(self):
        """
        Runs daily - UC-024
        Analyzes progress of active tasks using AI for companies with AI enabled
        """
        # Get all companies with AI enabled
        companies = self.company_repo.get_with_ai_enabled()
        
        for company in companies:
            # Get all active tasks for this company's teams
            tasks = self.task_repo.get_active_tasks_by_company(
                company.id,
                status=TaskStatus.DOING
            )
            
            for task in tasks:
                # Skip if task was already analyzed today
                if self.was_analyzed_today(task.id):
                    continue
                
                # Get task notes
                notes = self.note_repo.get_by_task(task.id)
                
                # Skip if no new notes since last analysis
                if not self.has_new_notes(task.id, notes):
                    continue
                
                # Get LLM client for company's provider
                llm_client = self.llm_factory.get_client(
                    company.ai_provider,
                    company.ai_api_key
                )
                
                # Analyze progress
                analyzer = AIProgressAnalyzer()
                estimate = analyzer.analyze_task_progress(task, notes, llm_client)
                
                if estimate is None:
                    continue  # Analysis failed
                
                # Check if update is needed (BR-019: >10% difference)
                if analyzer.should_update_progress(
                    task.completion_percentage,
                    estimate.percentage
                ):
                    # Update task
                    task.completion_percentage = estimate.percentage
                    task.completion_source = CompletionSource.AI
                    self.task_repo.save(task)
                    
                    # Create system note
                    self.note_repo.create(Note(
                        task_id=task.id,
                        author_id=None,  # System
                        content=f"AI estimated progress at {estimate.percentage}% - {estimate.reasoning}",
                        note_type=NoteType.SYSTEM
                    ))
                    
                    # Emit event
                    self.event_bus.emit(TaskProgressUpdated(
                        task_id=task.id,
                        completion_percentage=estimate.percentage,
                        source='ai',
                        reasoning=estimate.reasoning,
                        timestamp=now(),
                        user_id=None
                    ))
                
                # Mark as analyzed
                self.mark_analyzed_today(task.id)
```

---

## 🌍 Internationalization (i18n)

### Translation Dictionary Structure

```
translations/
├── en.json          # English (fallback)
├── pt-BR.json       # Portuguese (Brazil)
├── es.json          # Spanish
└── fr.json          # French (future)
```

### Translation Keys (Comprehensive Examples)

```json
{
  "task.status.todo": {"en": "To Do", "pt-BR": "A Fazer", "es": "Por Hacer"},
  "task.status.doing": {"en": "Doing", "pt-BR": "Fazendo", "es": "Haciendo"},
  "task.status.blocked": {"en": "Blocked", "pt-BR": "Bloqueado", "es": "Bloqueado"},
  "task.status.done": {"en": "Done", "pt-BR": "Concluído", "es": "Hecho"},
  
  "task.priority.low": {"en": "Low", "pt-BR": "Baixa", "es": "Baja"},
  "task.priority.medium": {"en": "Medium", "pt-BR": "Média", "es": "Media"},
  "task.priority.high": {"en": "High", "pt-BR": "Alta", "es": "Alta"},
  
  "task.progress.manual": {"en": "Manual", "pt-BR": "Manual", "es": "Manual"},
  "task.progress.ai": {"en": "AI Estimated", "pt-BR": "Estimado por IA", "es": "Estimado por IA"},
  "task.progress.not_tracked": {"en": "Not tracked", "pt-BR": "Não rastreado", "es": "No rastreado"},
  "task.progress.update": {"en": "Update progress", "pt-BR": "Atualizar progresso", "es": "Actualizar progreso"},
  
  "workload.health.tranquilo": {"en": "Relaxed", "pt-BR": "Tranquilo", "es": "Tranquilo"},
  "workload.health.saudavel": {"en": "Healthy", "pt-BR": "Saudável", "es": "Saludable"},
  "workload.health.apertado": {"en": "Tight", "pt-BR": "Apertado", "es": "Ajustado"},
  "workload.health.impossivel": {"en": "Impossible", "pt-BR": "Impossível", "es": "Imposible"},
  
  "email.task_assigned.subject": {
    "en": "Task assigned to you: {title}",
    "pt-BR": "Tarefa atribuída a você: {title}",
    "es": "Tarea asignada a ti: {title}"
  },
  
  "note.task_created": {
    "en": "Task created by {user}",
    "pt-BR": "Tarefa criada por {user}",
    "es": "Tarea creada por {user}"
  },
  
  "note.status_changed": {
    "en": "{user} changed status from {old_status} to {new_status}",
    "pt-BR": "{user} alterou status de {old_status} para {new_status}",
    "es": "{user} cambió estado de {old_status} a {new_status}"
  },
  
  "note.progress_updated_manual": {
    "en": "{user} updated progress to {percentage}%",
    "pt-BR": "{user} atualizou progresso para {percentage}%",
    "es": "{user} actualizó progreso a {percentage}%"
  },
  
  "note.progress_updated_ai": {
    "en": "AI estimated progress at {percentage}% - {reasoning}",
    "pt-BR": "IA estimou progresso em {percentage}% - {reasoning}",
    "es": "IA estimó progreso en {percentage}% - {reasoning}"
  },
  
  "error.task.role_not_in_team": {
    "en": "Role must belong to project's team",
    "pt-BR": "Role deve pertencer ao time do projeto",
    "es": "El rol debe pertenecer al equipo del proyecto"
  },
  
  "error.company.ai_not_enabled": {
    "en": "AI features are not enabled for this company",
    "pt-BR": "Recursos de IA não estão habilitados para esta empresa",
    "es": "Las funciones de IA no están habilitadas para esta empresa"
  },
  
  "error.progress.invalid_percentage": {
    "en": "Progress percentage must be between 0 and 100",
    "pt-BR": "Porcentagem de progresso deve estar entre 0 e 100",
    "es": "El porcentaje de progreso debe estar entre 0 y 100"
  }
}
```

### Translation Service Implementation

```python
# Pseudocode
class TranslationService:
    def __init__(self, translations_dir: str):
        self.translations = self._load_translations(translations_dir)
    
    def translate(self, key: str, language: str, **params) -> str:
        """
        Implements BR-014: Language fallback
        
        Priority:
        1. Requested language
        2. English fallback
        3. Return key itself
        """
        # Try requested language
        if language in self.translations:
            if key in self.translations[language]:
                return self.translations[language][key].format(**params)
        
        # Fallback to English
        if key in self.translations['en']:
            return self.translations['en'][key].format(**params)
        
        # Last resort
        logger.warning(f"Missing translation: {key} for {language}")
        return key
```

### Usage Examples

```python
# In use case - creating system note
note_content = translator.translate(
    "note.task_created",
    user.preferred_language,
    user=user.name
)

# In email service
subject = translator.translate(
    "email.task_assigned.subject",
    language,
    title=task.title
)

# In API response
status_label = translator.translate(
    f"task.status.{task.status}",
    user.preferred_language
)
```

---

## 🔗 Events & Integration

### Event Flow Examples

#### Task Completion with Dependency Unblocking
```
User completes Task A
    ↓
UpdateTaskStatusUseCase
    ↓
Task A.complete()
    ↓
EventBus.emit(TaskCompleted)
    ↓
┌─────────────┬──────────────────┐
│             │                  │
EmailHandler  DependencyHandler  AuditLogger
│             │                  │
Notify user   Find Task B       Log event
              depends on A
              │
              All deps done?
              │
              Task B.unblock()
              │
              EventBus.emit(TaskUnblocked)
              │
              EmailHandler
              │
              Notify Task B assignee
```

### Integration Points (Future)

- **Webhooks:** HTTP callbacks for events
- **Slack/Discord:** Real-time team notifications
- **GitHub/GitLab:** Link commits to tasks
- **Calendar:** Sync due dates with Google Calendar

---

## 🎯 Implementation Priority

### Phase 1: Core (MVP)
- ✅ Company & Team models
- ✅ Domain models (User, Role, Project, Task, Note)
- ✅ Use Cases 1-10 (core task management)
- ✅ Business Rules 1-9
- ✅ Basic i18n (en, pt-BR)
- ✅ In-memory event bus
- ✅ Manual progress tracking (UC-023)

### Phase 2: Intelligence
- ✅ Use Cases 11, 18-20 (workload, dashboard, baselines)
- ✅ Business Rules 10-11 (workload, ranking)
- ✅ Event handlers (email)
- ✅ Scheduler jobs
- ✅ Progress tracking UI

### Phase 3: AI Integration (Optional but Recommended)
- ✅ Use Cases 21-22 (Company management, AI enablement)
- ✅ Use Case 24-25 (AI progress analysis)
- ✅ Business Rules 17-21 (AI features, progress tracking)
- ✅ LLM integration (Anthropic/OpenAI)
- ✅ AI progress analyzer service
- ✅ AI scheduler job

### Phase 4: Communication
- ✅ Use Cases 12-14 (notifications, digests, reminders)
- ✅ Business Rules 12-13 (email rules)
- ✅ Email templates (all languages)

### Phase 5: Polish
- ✅ Use Case 16 (AI ranking suggestion)
- ✅ Complete i18n coverage
- ✅ Webhooks
- ✅ Integrations (Slack, GitHub)

---

## 📝 Next Steps

1. **Create TECH_STACK.md** - Specify technologies (FastAPI, React, PostgreSQL, etc.)
2. **Define API Contract** - OpenAPI/Swagger specification
3. **Database Schema** - DDL scripts for PostgreSQL
4. **Set Up Project Structure** - Directory layout and dependencies
5. **Implement Phase 1** - Core domain and use cases

**This specification is ready for implementation with any modern web stack.**
