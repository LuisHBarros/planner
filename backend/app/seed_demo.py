"""
Seed script for Planner Multiplayer demo data.

Creates:
- One company
- One team
- A few roles
- A couple of users
- One demo project
- Several tasks with dependencies

Run locally (from the backend directory) with:

    uvicorn app.main:app --reload  # in one terminal

Then in another terminal:

    python -m app.seed_demo
"""

from __future__ import annotations

from uuid import uuid4

from sqlalchemy.orm import Session

from app.infrastructure.database import SessionLocal, init_db
from app.infrastructure.persistence import repositories as repo
from app.domain.models import company as company_model
from app.domain.models import team as team_model
from app.domain.models import role as role_model
from app.domain.models import user as user_model
from app.domain.models import project as project_model
from app.domain.models import task as task_model
from app.domain.models import task_dependency as task_dependency_model
from app.domain.models import enums


def seed_demo() -> None:
  init_db()
  db: Session = SessionLocal()

  try:
    company_repo = repo.SqlAlchemyCompanyRepository(db)
    team_repo = repo.SqlAlchemyTeamRepository(db)
    role_repo = repo.SqlAlchemyRoleRepository(db)
    user_repo = repo.SqlAlchemyUserRepository(db)
    project_repo = repo.SqlAlchemyProjectRepository(db)
    task_repo = repo.SqlAlchemyTaskRepository(db)

    # Idempotency by slug/name
    company = company_repo.find_by_slug("demo-company")
    if not company:
      company = company_model.Company(
        id=str(uuid4()),
        name="Demo Company",
        slug="demo-company",
        plan=enums.CompanyPlan.FREE,
        ai_enabled=False,
        billing_email="demo@example.com",
      )
      company_repo.add(company)

    team = team_repo.find_by_name_and_company("Core Product", company.id)
    if not team:
      team = team_model.Team(
        id=str(uuid4()),
        company_id=company.id,
        name="Core Product",
        description="Demo team for Planner Multiplayer",
        default_language="en",
      )
      team_repo.add(team)

    # Roles
    roles_by_name: dict[str, role_model.Role] = {}
    for name, level, capacity in [
      ("Backend Senior", enums.RoleLevel.SENIOR, 4),
      ("Frontend", enums.RoleLevel.MID, 4),
      ("Product Manager", enums.RoleLevel.SENIOR, 6),
    ]:
      existing = role_repo.find_by_name_and_team(name=name, team_id=team.id)
      if existing:
        roles_by_name[name] = existing
        continue
      role = role_model.Role(
        id=str(uuid4()),
        team_id=team.id,
        name=name,
        level=level,
        base_capacity=capacity,
        description=f"{name} demo role",
      )
      role_repo.add(role)
      roles_by_name[name] = role

    # Users
    def get_or_create_user(email: str, name: str) -> user_model.User:
      existing = user_repo.find_by_email(email)
      if existing:
        return existing
      user = user_model.User(
        id=str(uuid4()),
        email=email,
        name=name,
        preferred_language="en",
      )
      user_repo.add(user)
      return user

    backend_user = get_or_create_user("backend.senior@example.com", "Backend Senior Demo")
    frontend_user = get_or_create_user("frontend@example.com", "Frontend Demo")
    pm_user = get_or_create_user("pm@example.com", "Product Manager Demo")

    # Simple project
    project = project_repo.find_by_name_and_team("Payments Revamp", team.id)
    if not project:
      project = project_model.Project(
        id=str(uuid4()),
        team_id=team.id,
        name="Payments Revamp",
        description="Demo project used by the frontend workspace",
        status=enums.ProjectStatus.ACTIVE,
      )
      project_repo.add(project)

    # Tasks (simplified, rank_index just incremental)
    if not task_repo.find_by_project_id(project.id):
      tasks_data = [
        {
          "title": "Fix critical payment bug",
          "description": "Resolve bug causing failures in checkout flow.",
          "role": "Backend Senior",
          "user": backend_user,
          "priority": enums.TaskPriority.HIGH,
          "status": enums.TaskStatus.DOING,
        },
        {
          "title": "Implement OAuth2 provider",
          "description": "Add OAuth2 login for major providers.",
          "role": "Backend Senior",
          "user": backend_user,
          "priority": enums.TaskPriority.HIGH,
          "status": enums.TaskStatus.TODO,
        },
        {
          "title": "Dashboard layout for payments",
          "description": "Create dashboard layout to monitor payments.",
          "role": "Frontend",
          "user": frontend_user,
          "priority": enums.TaskPriority.HIGH,
          "status": enums.TaskStatus.BLOCKED,
        },
        {
          "title": "Define Q2 priorities",
          "description": "Align team around Q2 execution order.",
          "role": "Product Manager",
          "user": pm_user,
          "priority": enums.TaskPriority.MEDIUM,
          "status": enums.TaskStatus.DOING,
        },
      ]

      created_tasks: list[task_model.Task] = []
      for idx, item in enumerate(tasks_data):
        task = task_model.Task(
          id=str(uuid4()),
          project_id=project.id,
          title=item["title"],
          description=item["description"],
          status=item["status"],
          priority=item["priority"],
          rank_index=float(idx + 1),
          role_responsible_id=roles_by_name[item["role"]].id,
          user_responsible_id=item["user"].id,
        )
        created_tasks.append(task)
        task_repo.add(task)

      # Dependencies: dashboard blocked by payment bug
      dep_repo = repo.SqlAlchemyTaskDependencyRepository(db)
      if len(created_tasks) >= 3:
        from_task = created_tasks[0]
        blocked_task = created_tasks[2]
        dep_repo.add(
          task_dependency_model.TaskDependency(
            id=str(uuid4()),
            task_id=blocked_task.id,
            depends_on_task_id=from_task.id,
            dependency_type=enums.DependencyType.BLOCKS,
          )
        )

    db.commit()
    print("✅ Demo data seeded successfully.")
    print(f"Company ID: {company.id}")
    print(f"Team ID: {team.id}")
    print(f"Project ID: {project.id}")
    print(f"Backend Senior role ID: {roles_by_name['Backend Senior'].id}")

  finally:
    db.close()


if __name__ == "__main__":
  seed_demo()

