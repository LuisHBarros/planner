"""SQLAlchemy repository implementations for domain repositories."""
from typing import List, Optional, Union
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.models.company import Company
from app.domain.models.team import Team
from app.domain.models.user import User
from app.domain.models.role import Role
from app.domain.models.project import Project
from app.domain.models.task import Task
from app.domain.models.task_dependency import TaskDependency
from app.domain.models.note import Note
from app.domain.models.team_member import TeamMember
from app.domain.models.team_invite import TeamInvite
from app.domain.models.schedule_history import ScheduleHistory
from app.domain.models.project_member import ProjectMember
from app.domain.models.task_assignment_history import TaskAssignmentHistory
from app.domain.models.task_abandonment import TaskAbandonment
from app.domain.models.enums import TaskStatus
from app.domain.models.value_objects import TaskId, ProjectId, RoleId, UserId


def _extract_uuid(value: Union[TaskId, ProjectId, RoleId, UserId, UUID, None]) -> Optional[UUID]:
    """Extract raw UUID from a value object or return as-is if already UUID."""
    if value is None:
        return None
    if hasattr(value, 'value'):
        return value.value
    return value
from app.application.ports.company_repository import CompanyRepository
from app.application.ports.team_repository import TeamRepository
from app.application.ports.user_repository import UserRepository
from app.application.ports.role_repository import RoleRepository
from app.application.ports.project_repository import ProjectRepository
from app.application.ports.task_repository import TaskRepository
from app.application.ports.task_dependency_repository import TaskDependencyRepository
from app.application.ports.note_repository import NoteRepository
from app.application.ports.team_member_repository import TeamMemberRepository
from app.application.ports.team_invite_repository import TeamInviteRepository
from app.application.ports.schedule_history_repository import ScheduleHistoryRepository
from app.application.ports.project_member_repository import ProjectMemberRepository
from app.application.ports.task_assignment_history_repository import TaskAssignmentHistoryRepository
from app.application.ports.task_abandonment_repository import TaskAbandonmentRepository
from app.infrastructure.persistence.models import (
    CompanyModel,
    TeamModel,
    UserModel,
    RoleModel,
    ProjectModel,
    TaskModel,
    TaskDependencyModel,
    NoteModel,
    TeamMemberModel,
    TeamInviteModel,
    ScheduleHistoryModel,
    ProjectMemberModel,
    TaskAssignmentHistoryModel,
    TaskAbandonmentModel,
)


class SqlAlchemyCompanyRepository(CompanyRepository):
    """SQLAlchemy implementation of CompanyRepository."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, company: Company) -> None:
        model = self.session.get(CompanyModel, str(company.id)) or CompanyModel(id=str(company.id))
        model.name = company.name
        model.slug = company.slug
        model.plan = company.plan
        model.billing_email = company.billing_email
        model.ai_enabled = company.ai_enabled
        model.ai_provider = company.ai_provider
        model.ai_api_key = company.ai_api_key
        self.session.add(model)

    def find_by_id(self, company_id: UUID) -> Optional[Company]:
        model = self.session.get(CompanyModel, str(company_id))
        if not model:
            return None
        return Company(
            id=UUID(model.id) if isinstance(model.id, str) else model.id,
            name=model.name,
            slug=model.slug,
            plan=model.plan,
            billing_email=model.billing_email,
            ai_enabled=model.ai_enabled,
            ai_provider=model.ai_provider,
            ai_api_key=model.ai_api_key,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def find_by_slug(self, slug: str) -> Optional[Company]:
        model = (
            self.session.query(CompanyModel)
            .filter(CompanyModel.slug == slug)
            .one_or_none()
        )
        if not model:
            return None
        return Company(
            id=UUID(model.id) if isinstance(model.id, str) else model.id,
            name=model.name,
            slug=model.slug,
            plan=model.plan,
            billing_email=model.billing_email,
            ai_enabled=model.ai_enabled,
            ai_provider=model.ai_provider,
            ai_api_key=model.ai_api_key,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def find_all(self) -> List[Company]:
        """Find all companies (for MVP, no pagination)."""
        models = self.session.query(CompanyModel).all()
        return [
            Company(
                id=UUID(m.id) if isinstance(m.id, str) else m.id,
                name=m.name,
                slug=m.slug,
                plan=m.plan,
                billing_email=m.billing_email,
                ai_enabled=m.ai_enabled,
                ai_provider=m.ai_provider,
                ai_api_key=m.ai_api_key,
                created_at=m.created_at,
                updated_at=m.updated_at,
            )
            for m in models
        ]

    # Convenience alias used by seed scripts
    def add(self, company: Company) -> None:
        """Add a new company (alias for save)."""
        self.save(company)


class SqlAlchemyTeamRepository(TeamRepository):
    """SQLAlchemy implementation of TeamRepository."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, team: Team) -> None:
        model = self.session.get(TeamModel, str(team.id)) or TeamModel(id=str(team.id))
        model.company_id = str(team.company_id)
        model.name = team.name
        model.description = team.description
        model.default_language = team.default_language
        self.session.add(model)

    def find_by_id(self, team_id: UUID) -> Optional[Team]:
        model = self.session.get(TeamModel, str(team_id))
        if not model:
            return None
        return Team(
            id=UUID(model.id) if isinstance(model.id, str) else model.id,
            company_id=UUID(model.company_id) if isinstance(model.company_id, str) else model.company_id,
            name=model.name,
            description=model.description,
            default_language=model.default_language,
            created_at=model.created_at,
        )

    def find_by_company_id(self, company_id: UUID) -> List[Team]:
        models = (
            self.session.query(TeamModel)
            .filter(TeamModel.company_id == str(company_id))
            .all()
        )
        return [
            Team(
                id=UUID(m.id) if isinstance(m.id, str) else m.id,
                company_id=UUID(m.company_id) if isinstance(m.company_id, str) else m.company_id,
                name=m.name,
                description=m.description,
                default_language=m.default_language,
                created_at=m.created_at,
            )
            for m in models
        ]

    def find_all(self) -> List[Team]:
        """Find all teams (for MVP, no pagination)."""
        models = self.session.query(TeamModel).all()
        return [
            Team(
                id=UUID(m.id) if isinstance(m.id, str) else m.id,
                company_id=UUID(m.company_id) if isinstance(m.company_id, str) else m.company_id,
                name=m.name,
                description=m.description,
                default_language=m.default_language,
                created_at=m.created_at,
            )
            for m in models
        ]

    # Convenience helpers for seed scripts
    def add(self, team: Team) -> None:
        """Add a new team (alias for save)."""
        self.save(team)

    def find_by_name_and_company(self, name: str, company_id: UUID) -> Optional[Team]:
        model = (
            self.session.query(TeamModel)
            .filter(TeamModel.company_id == str(company_id), TeamModel.name == name)
            .one_or_none()
        )
        if not model:
            return None
        return Team(
            id=UUID(model.id) if isinstance(model.id, str) else model.id,
            company_id=UUID(model.company_id) if isinstance(model.company_id, str) else model.company_id,
            name=model.name,
            description=model.description,
            default_language=model.default_language,
            created_at=model.created_at,
        )


class SqlAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, user: User) -> None:
        model = self.session.get(UserModel, str(user.id)) or UserModel(id=str(user.id))
        model.email = user.email
        model.name = user.name
        model.preferred_language = user.preferred_language
        model.avatar_url = user.avatar_url
        self.session.add(model)

    def find_by_id(self, user_id: UUID) -> Optional[User]:
        model = self.session.get(UserModel, str(user_id))
        if not model:
            return None
        return User(
            id=UUID(model.id) if isinstance(model.id, str) else model.id,
            email=model.email,
            name=model.name,
            preferred_language=model.preferred_language,
            avatar_url=model.avatar_url,
            created_at=model.created_at,
        )

    def find_by_email(self, email: str) -> Optional[User]:
        model = (
            self.session.query(UserModel)
            .filter(UserModel.email == email)
            .one_or_none()
        )
        if not model:
            return None
        return User(
            id=UUID(model.id) if isinstance(model.id, str) else model.id,
            email=model.email,
            name=model.name,
            preferred_language=model.preferred_language,
            avatar_url=model.avatar_url,
            created_at=model.created_at,
        )

    def find_by_team_id(self, team_id: UUID) -> List[User]:
        # For MVP and seeding, just return all users (no membership table yet)
        models = self.session.query(UserModel).all()
        return [
            User(
                id=UUID(m.id) if isinstance(m.id, str) else m.id,
                email=m.email,
                name=m.name,
                preferred_language=m.preferred_language,
                avatar_url=m.avatar_url,
                created_at=m.created_at,
            )
            for m in models
        ]

    # Convenience alias used by seed scripts
    def add(self, user: User) -> None:
        """Add a new user (alias for save)."""
        self.save(user)


class SqlAlchemyTeamMemberRepository(TeamMemberRepository):
    """SQLAlchemy implementation of TeamMemberRepository."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, member: TeamMember) -> None:
        model = self.session.get(TeamMemberModel, str(member.id)) or TeamMemberModel(
            id=str(member.id)
        )
        model.user_id = str(member.user_id)
        model.team_id = str(member.team_id)
        model.role = member.role
        model.joined_at = member.joined_at
        self.session.add(model)

    def find_by_user_id(self, user_id: UUID) -> List[TeamMember]:
        models = (
            self.session.query(TeamMemberModel)
            .filter(TeamMemberModel.user_id == str(user_id))
            .all()
        )
        return [
            TeamMember(
                id=m.id,
                user_id=UUID(m.user_id),
                team_id=UUID(m.team_id),
                role=m.role,
                joined_at=m.joined_at,
            )
            for m in models
        ]

    def find_by_team_id(self, team_id: UUID) -> List[TeamMember]:
        models = (
            self.session.query(TeamMemberModel)
            .filter(TeamMemberModel.team_id == str(team_id))
            .all()
        )
        return [
            TeamMember(
                id=m.id,
                user_id=UUID(m.user_id),
                team_id=UUID(m.team_id),
                role=m.role,
                joined_at=m.joined_at,
            )
            for m in models
        ]


class SqlAlchemyRoleRepository(RoleRepository):
    """SQLAlchemy implementation of RoleRepository."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, role: Role) -> None:
        model = self.session.get(RoleModel, str(role.id)) or RoleModel(id=str(role.id))
        model.team_id = str(role.team_id)
        model.name = role.name
        model.level = role.level
        model.base_capacity = role.base_capacity
        model.description = role.description
        self.session.add(model)

    def find_by_id(self, role_id: UUID) -> Optional[Role]:
        model = self.session.get(RoleModel, str(role_id))
        if not model:
            return None
        return Role(
            id=UUID(model.id) if isinstance(model.id, str) else model.id,
            team_id=UUID(model.team_id) if isinstance(model.team_id, str) else model.team_id,
            name=model.name,
            level=model.level,
            base_capacity=model.base_capacity,
            description=model.description,
            created_at=model.created_at,
        )

    def find_by_team_id(self, team_id: UUID) -> List[Role]:
        models = (
            self.session.query(RoleModel)
            .filter(RoleModel.team_id == str(team_id))
            .all()
        )
        return [
            Role(
                id=UUID(m.id) if isinstance(m.id, str) else m.id,
                team_id=UUID(m.team_id) if isinstance(m.team_id, str) else m.team_id,
                name=m.name,
                level=m.level,
                base_capacity=m.base_capacity,
                description=m.description,
                created_at=m.created_at,
            )
            for m in models
        ]

    def find_by_user_and_team(self, user_id: UUID, team_id: UUID) -> List[Role]:
        # MVP: we don't model assignments, so return all roles for team.
        return self.find_by_team_id(team_id)

    def find_all(self) -> List[Role]:
        """Find all roles (for MVP, no pagination)."""
        models = self.session.query(RoleModel).all()
        return [
            Role(
                id=UUID(m.id) if isinstance(m.id, str) else m.id,
                team_id=UUID(m.team_id) if isinstance(m.team_id, str) else m.team_id,
                name=m.name,
                level=m.level,
                base_capacity=m.base_capacity,
                description=m.description,
                created_at=m.created_at,
            )
            for m in models
        ]

    # Convenience helpers for seed scripts
    def add(self, role: Role) -> None:
        """Add a new role (alias for save)."""
        self.save(role)

    def find_by_name_and_team(self, name: str, team_id: UUID) -> Optional[Role]:
        model = (
            self.session.query(RoleModel)
            .filter(RoleModel.team_id == str(team_id), RoleModel.name == name)
            .one_or_none()
        )
        if not model:
            return None
        return Role(
            id=UUID(model.id) if isinstance(model.id, str) else model.id,
            team_id=UUID(model.team_id) if isinstance(model.team_id, str) else model.team_id,
            name=model.name,
            level=model.level,
            base_capacity=model.base_capacity,
            description=model.description,
            created_at=model.created_at,
        )


class SqlAlchemyProjectRepository(ProjectRepository):
    """SQLAlchemy implementation of ProjectRepository."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, project: Project) -> None:
        model = self.session.get(ProjectModel, str(project.id)) or ProjectModel(id=str(project.id))
        model.team_id = str(project.team_id)
        model.name = project.name
        model.description = project.description
        model.status = project.status
        self.session.add(model)

    def find_by_id(self, project_id: UUID) -> Optional[Project]:
        model = self.session.get(ProjectModel, str(project_id))
        if not model:
            return None
        return Project(
            id=UUID(model.id) if isinstance(model.id, str) else model.id,
            team_id=UUID(model.team_id) if isinstance(model.team_id, str) else model.team_id,
            name=model.name,
            description=model.description,
            status=model.status,
            created_at=model.created_at,
        )

    def find_by_team_id(self, team_id: UUID) -> List[Project]:
        models = (
            self.session.query(ProjectModel)
            .filter(ProjectModel.team_id == str(team_id))
            .all()
        )
        return [
            Project(
                id=UUID(m.id) if isinstance(m.id, str) else m.id,
                team_id=UUID(m.team_id) if isinstance(m.team_id, str) else m.team_id,
                name=m.name,
                description=m.description,
                status=m.status,
                created_at=m.created_at,
            )
            for m in models
        ]

    def find_all(self) -> List[Project]:
        """Find all projects (for MVP, no pagination)."""
        models = self.session.query(ProjectModel).all()
        return [
            Project(
                id=UUID(m.id) if isinstance(m.id, str) else m.id,
                team_id=UUID(m.team_id) if isinstance(m.team_id, str) else m.team_id,
                name=m.name,
                description=m.description,
                status=m.status,
                created_at=m.created_at,
            )
            for m in models
        ]

    # Convenience helpers for seed scripts
    def add(self, project: Project) -> None:
        """Add a new project (alias for save)."""
        self.save(project)

    def find_by_name_and_team(self, name: str, team_id: UUID) -> Optional[Project]:
        model = (
            self.session.query(ProjectModel)
            .filter(ProjectModel.team_id == str(team_id), ProjectModel.name == name)
            .one_or_none()
        )
        if not model:
            return None
        return Project(
            id=UUID(model.id) if isinstance(model.id, str) else model.id,
            team_id=UUID(model.team_id) if isinstance(model.team_id, str) else model.team_id,
            name=model.name,
            description=model.description,
            status=model.status,
            created_at=model.created_at,
        )


class SqlAlchemyTaskRepository(TaskRepository):
    """SQLAlchemy implementation of TaskRepository.

    Handles value objects by extracting raw UUIDs for database operations.
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def _to_domain(self, model: TaskModel) -> Task:
        return Task(
            id=UUID(model.id) if isinstance(model.id, str) else model.id,
            project_id=UUID(model.project_id) if isinstance(model.project_id, str) else model.project_id,
            title=model.title,
            description=model.description,
            role_responsible_id=UUID(model.role_responsible_id) if isinstance(model.role_responsible_id, str) else model.role_responsible_id,
            status=model.status,
            priority=model.priority,
            rank_index=model.rank_index,
            user_responsible_id=UUID(model.user_responsible_id) if model.user_responsible_id and isinstance(model.user_responsible_id, str) else model.user_responsible_id,
            difficulty=model.difficulty,
            completion_percentage=model.completion_percentage,
            completion_source=model.completion_source,
            due_date=model.due_date,
            expected_start_date=model.expected_start_date,
            expected_end_date=model.expected_end_date,
            actual_start_date=model.actual_start_date,
            actual_end_date=model.actual_end_date,
            is_delayed=model.is_delayed,
            blocked_reason=model.blocked_reason,
            cancellation_reason=model.cancellation_reason,
            created_at=model.created_at,
            updated_at=model.updated_at,
            completed_at=model.completed_at,
            cancelled_at=model.cancelled_at,
        )

    def save(self, task: Task) -> None:
        # Extract raw UUIDs from value objects for database storage
        task_id = _extract_uuid(task.id)
        model = self.session.get(TaskModel, str(task_id)) or TaskModel(id=str(task_id))
        model.project_id = str(_extract_uuid(task.project_id))
        model.title = task.title
        model.description = task.description
        model.role_responsible_id = str(_extract_uuid(task.role_responsible_id))
        model.status = task.status
        model.priority = task.priority
        model.rank_index = task.rank_index
        user_id = _extract_uuid(task.user_responsible_id)
        model.user_responsible_id = str(user_id) if user_id else None
        model.difficulty = task.difficulty
        model.completion_percentage = task.completion_percentage
        model.completion_source = task.completion_source
        model.due_date = task.due_date
        model.expected_start_date = task.expected_start_date
        model.expected_end_date = task.expected_end_date
        model.actual_start_date = task.actual_start_date
        model.actual_end_date = task.actual_end_date
        model.is_delayed = task.is_delayed
        model.blocked_reason = task.blocked_reason
        model.cancellation_reason = task.cancellation_reason
        model.created_at = task.created_at
        model.updated_at = task.updated_at
        model.completed_at = task.completed_at
        model.cancelled_at = task.cancelled_at
        self.session.add(model)

    def find_by_id(self, task_id: Union[TaskId, UUID]) -> Optional[Task]:
        raw_id = _extract_uuid(task_id)
        model = self.session.get(TaskModel, str(raw_id))
        if not model:
            return None
        return self._to_domain(model)

    def find_by_project_id(self, project_id: Union[ProjectId, UUID]) -> List[Task]:
        raw_id = str(_extract_uuid(project_id))
        models = (
            self.session.query(TaskModel)
            .filter(TaskModel.project_id == raw_id)
            .order_by(TaskModel.rank_index)
            .all()
        )
        return [self._to_domain(m) for m in models]

    def find_by_role_id(
        self, role_id: Union[RoleId, UUID], status: Optional[TaskStatus] = None
    ) -> List[Task]:
        raw_id = str(_extract_uuid(role_id))
        query = self.session.query(TaskModel).filter(
            TaskModel.role_responsible_id == raw_id
        )
        if status is not None:
            query = query.filter(TaskModel.status == status)
        models = query.order_by(TaskModel.rank_index).all()
        return [self._to_domain(m) for m in models]

    def find_by_user_id(self, user_id: Union[UserId, UUID]) -> List[Task]:
        raw_id = str(_extract_uuid(user_id))
        models = (
            self.session.query(TaskModel)
            .filter(TaskModel.user_responsible_id == raw_id)
            .order_by(TaskModel.rank_index)
            .all()
        )
        return [self._to_domain(m) for m in models]

    def find_dependent_tasks(self, task_id: Union[TaskId, UUID]) -> List[Task]:
        raw_id = str(_extract_uuid(task_id))
        deps = (
            self.session.query(TaskDependencyModel)
            .filter(TaskDependencyModel.depends_on_task_id == raw_id)
            .all()
        )
        task_ids = [d.task_id for d in deps]
        if not task_ids:
            return []
        models = self.session.query(TaskModel).filter(TaskModel.id.in_(task_ids)).all()
        return [self._to_domain(m) for m in models]

    # Convenience alias used by seed scripts
    def add(self, task: Task) -> None:
        """Add a new task (alias for save)."""
        self.save(task)


class SqlAlchemyTaskDependencyRepository(TaskDependencyRepository):
    """SQLAlchemy implementation of TaskDependencyRepository."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, dependency: TaskDependency) -> None:
        model = (
            self.session.get(TaskDependencyModel, str(dependency.id))
            or TaskDependencyModel(id=str(dependency.id))
        )
        model.task_id = str(dependency.task_id)
        model.depends_on_task_id = str(dependency.depends_on_task_id)
        model.dependency_type = dependency.dependency_type
        model.created_at = dependency.created_at
        self.session.add(model)

    def find_by_id(self, dependency_id: UUID) -> Optional[TaskDependency]:
        model = self.session.get(TaskDependencyModel, str(dependency_id))
        if not model:
            return None
        return TaskDependency(
            id=UUID(model.id) if isinstance(model.id, str) else model.id,
            task_id=UUID(model.task_id) if isinstance(model.task_id, str) else model.task_id,
            depends_on_task_id=UUID(model.depends_on_task_id) if isinstance(model.depends_on_task_id, str) else model.depends_on_task_id,
            dependency_type=model.dependency_type,
            created_at=model.created_at,
        )

    def find_by_task_id(self, task_id: UUID) -> List[TaskDependency]:
        models = (
            self.session.query(TaskDependencyModel)
            .filter(TaskDependencyModel.task_id == str(task_id))
            .all()
        )
        return [
            TaskDependency(
                id=UUID(m.id) if isinstance(m.id, str) else m.id,
                task_id=UUID(m.task_id) if isinstance(m.task_id, str) else m.task_id,
                depends_on_task_id=UUID(m.depends_on_task_id) if isinstance(m.depends_on_task_id, str) else m.depends_on_task_id,
                dependency_type=m.dependency_type,
                created_at=m.created_at,
            )
            for m in models
        ]

    def find_by_depends_on_task_id(self, depends_on_task_id: UUID) -> List[TaskDependency]:
        models = (
            self.session.query(TaskDependencyModel)
            .filter(TaskDependencyModel.depends_on_task_id == str(depends_on_task_id))
            .all()
        )
        return [
            TaskDependency(
                id=UUID(m.id) if isinstance(m.id, str) else m.id,
                task_id=UUID(m.task_id) if isinstance(m.task_id, str) else m.task_id,
                depends_on_task_id=UUID(m.depends_on_task_id) if isinstance(m.depends_on_task_id, str) else m.depends_on_task_id,
                dependency_type=m.dependency_type,
                created_at=m.created_at,
            )
            for m in models
        ]

    def delete(self, dependency_id: UUID) -> None:
        model = self.session.get(TaskDependencyModel, str(dependency_id))
        if model:
            self.session.delete(model)

    # Convenience alias used by seed scripts
    def add(self, dependency: TaskDependency) -> None:
        """Add a new task dependency (alias for save)."""
        self.save(dependency)


class SqlAlchemyTeamInviteRepository(TeamInviteRepository):
    """SQLAlchemy implementation of TeamInviteRepository."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, invite: TeamInvite) -> None:
        model = self.session.get(TeamInviteModel, str(invite.id)) or TeamInviteModel(
            id=str(invite.id)
        )
        model.team_id = str(invite.team_id)
        model.role = invite.role
        model.token = invite.token
        model.expires_at = invite.expires_at
        model.created_by = str(invite.created_by)
        model.created_at = invite.created_at
        model.used_at = invite.used_at
        self.session.add(model)

    def find_by_token(self, token: str) -> Optional[TeamInvite]:
        model = (
            self.session.query(TeamInviteModel)
            .filter(TeamInviteModel.token == token)
            .one_or_none()
        )
        if not model:
            return None
        return TeamInvite(
            id=model.id,
            team_id=UUID(model.team_id),
            role=model.role,
            token=model.token,
            expires_at=model.expires_at,
            created_by=UUID(model.created_by),
            created_at=model.created_at,
            used_at=model.used_at,
        )


class SqlAlchemyNoteRepository(NoteRepository):
    """SQLAlchemy implementation of NoteRepository."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, note: Note) -> None:
        model = self.session.get(NoteModel, str(note.id)) or NoteModel(id=str(note.id))
        model.task_id = str(note.task_id)
        model.content = note.content
        model.note_type = note.note_type
        model.author_id = str(note.author_id) if note.author_id else None
        model.created_at = note.created_at
        model.updated_at = note.updated_at
        self.session.add(model)

    def find_by_id(self, note_id: UUID) -> Optional[Note]:
        model = self.session.get(NoteModel, str(note_id))
        if not model:
            return None
        return Note(
            id=UUID(model.id) if isinstance(model.id, str) else model.id,
            task_id=UUID(model.task_id) if isinstance(model.task_id, str) else model.task_id,
            content=model.content,
            note_type=model.note_type,
            author_id=UUID(model.author_id) if model.author_id and isinstance(model.author_id, str) else model.author_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def find_by_task_id(self, task_id: UUID) -> List[Note]:
        models = (
            self.session.query(NoteModel)
            .filter(NoteModel.task_id == str(task_id))
            .order_by(NoteModel.created_at)
            .all()
        )
        return [
            Note(
                id=UUID(m.id) if isinstance(m.id, str) else m.id,
                task_id=UUID(m.task_id) if isinstance(m.task_id, str) else m.task_id,
                content=m.content,
                note_type=m.note_type,
                author_id=UUID(m.author_id) if m.author_id and isinstance(m.author_id, str) else m.author_id,
                created_at=m.created_at,
                updated_at=m.updated_at,
            )
            for m in models
        ]


class SqlAlchemyScheduleHistoryRepository(ScheduleHistoryRepository):
    """SQLAlchemy implementation of ScheduleHistoryRepository.

    This repository is append-only (immutable records per BR-025).
    ScheduleHistory records NEVER change - new changes create new records.
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, history: ScheduleHistory) -> None:
        """Persist a schedule history record (immutable append-only)."""
        model = ScheduleHistoryModel(
            id=str(history.id),
            task_id=str(history.task_id),
            old_expected_start=history.old_expected_start,
            old_expected_end=history.old_expected_end,
            new_expected_start=history.new_expected_start,
            new_expected_end=history.new_expected_end,
            reason=history.reason,
            caused_by_task_id=str(history.caused_by_task_id) if history.caused_by_task_id else None,
            changed_by_user_id=str(history.changed_by_user_id) if history.changed_by_user_id else None,
        )
        self.session.add(model)

    def find_by_task_id(self, task_id: UUID) -> List[ScheduleHistory]:
        """Return all schedule history records for a task, ordered by created_at."""
        models = (
            self.session.query(ScheduleHistoryModel)
            .filter(ScheduleHistoryModel.task_id == str(task_id))
            .order_by(ScheduleHistoryModel.created_at)
            .all()
        )
        return [self._model_to_domain(m) for m in models]

    def find_by_caused_by_task_id(self, caused_by_task_id: UUID) -> List[ScheduleHistory]:
        """Return all schedule history records caused by a specific task."""
        models = (
            self.session.query(ScheduleHistoryModel)
            .filter(ScheduleHistoryModel.caused_by_task_id == str(caused_by_task_id))
            .order_by(ScheduleHistoryModel.created_at)
            .all()
        )
        return [self._model_to_domain(m) for m in models]

    def _model_to_domain(self, model: ScheduleHistoryModel) -> ScheduleHistory:
        """Convert SQLAlchemy model to domain object."""
        return ScheduleHistory(
            id=UUID(model.id) if isinstance(model.id, str) else model.id,
            task_id=UUID(model.task_id) if isinstance(model.task_id, str) else model.task_id,
            old_expected_start=model.old_expected_start,
            old_expected_end=model.old_expected_end,
            new_expected_start=model.new_expected_start,
            new_expected_end=model.new_expected_end,
            reason=model.reason,
            caused_by_task_id=UUID(model.caused_by_task_id) if model.caused_by_task_id else None,
            changed_by_user_id=UUID(model.changed_by_user_id) if model.changed_by_user_id else None,
            created_at=model.created_at,
        )


class SqlAlchemyProjectMemberRepository(ProjectMemberRepository):
    """SQLAlchemy implementation of ProjectMemberRepository (v3.0)."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, project_member: ProjectMember) -> None:
        model = self.session.get(ProjectMemberModel, str(project_member.id)) or ProjectMemberModel(
            id=str(project_member.id)
        )
        model.project_id = str(project_member.project_id)
        model.user_id = str(project_member.user_id)
        model.role = project_member.role
        model.level = project_member.level
        model.is_active = project_member.is_active
        model.joined_at = project_member.joined_at
        model.left_at = project_member.left_at
        self.session.add(model)

    def find_by_id(self, project_member_id: UUID) -> Optional[ProjectMember]:
        model = self.session.get(ProjectMemberModel, str(project_member_id))
        if not model:
            return None
        return self._model_to_domain(model)

    def find_by_project_id(self, project_id: UUID) -> List[ProjectMember]:
        models = (
            self.session.query(ProjectMemberModel)
            .filter(ProjectMemberModel.project_id == str(project_id))
            .all()
        )
        return [self._model_to_domain(m) for m in models]

    def find_by_user_id(self, user_id: UUID) -> List[ProjectMember]:
        models = (
            self.session.query(ProjectMemberModel)
            .filter(ProjectMemberModel.user_id == str(user_id))
            .all()
        )
        return [self._model_to_domain(m) for m in models]

    def find_by_project_and_user(
        self, project_id: UUID, user_id: UUID
    ) -> Optional[ProjectMember]:
        model = (
            self.session.query(ProjectMemberModel)
            .filter(
                ProjectMemberModel.project_id == str(project_id),
                ProjectMemberModel.user_id == str(user_id),
            )
            .one_or_none()
        )
        if not model:
            return None
        return self._model_to_domain(model)

    def find_active_by_project_id(self, project_id: UUID) -> List[ProjectMember]:
        models = (
            self.session.query(ProjectMemberModel)
            .filter(
                ProjectMemberModel.project_id == str(project_id),
                ProjectMemberModel.is_active == True,
            )
            .all()
        )
        return [self._model_to_domain(m) for m in models]

    def delete(self, project_member_id: UUID) -> None:
        model = self.session.get(ProjectMemberModel, str(project_member_id))
        if model:
            self.session.delete(model)

    def _model_to_domain(self, model: ProjectMemberModel) -> ProjectMember:
        return ProjectMember(
            id=UUID(model.id) if isinstance(model.id, str) else model.id,
            project_id=UUID(model.project_id) if isinstance(model.project_id, str) else model.project_id,
            user_id=UUID(model.user_id) if isinstance(model.user_id, str) else model.user_id,
            role=model.role,
            level=model.level,
            is_active=model.is_active,
            joined_at=model.joined_at,
            left_at=model.left_at,
        )


class SqlAlchemyTaskAssignmentHistoryRepository(TaskAssignmentHistoryRepository):
    """SQLAlchemy implementation of TaskAssignmentHistoryRepository (v3.0)."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, history: TaskAssignmentHistory) -> None:
        """Persist an assignment history record (append-only)."""
        model = TaskAssignmentHistoryModel(
            id=str(history.id),
            task_id=str(history.task_id),
            user_id=str(history.user_id),
            action=history.action,
            abandonment_type=history.abandonment_type,
            created_at=history.created_at,
        )
        self.session.add(model)

    def find_by_id(self, history_id: UUID) -> Optional[TaskAssignmentHistory]:
        model = self.session.get(TaskAssignmentHistoryModel, str(history_id))
        if not model:
            return None
        return self._model_to_domain(model)

    def find_by_task_id(self, task_id: UUID) -> List[TaskAssignmentHistory]:
        models = (
            self.session.query(TaskAssignmentHistoryModel)
            .filter(TaskAssignmentHistoryModel.task_id == str(task_id))
            .order_by(TaskAssignmentHistoryModel.created_at)
            .all()
        )
        return [self._model_to_domain(m) for m in models]

    def find_by_user_id(self, user_id: UUID) -> List[TaskAssignmentHistory]:
        models = (
            self.session.query(TaskAssignmentHistoryModel)
            .filter(TaskAssignmentHistoryModel.user_id == str(user_id))
            .order_by(TaskAssignmentHistoryModel.created_at)
            .all()
        )
        return [self._model_to_domain(m) for m in models]

    def find_by_task_and_user(
        self, task_id: UUID, user_id: UUID
    ) -> List[TaskAssignmentHistory]:
        models = (
            self.session.query(TaskAssignmentHistoryModel)
            .filter(
                TaskAssignmentHistoryModel.task_id == str(task_id),
                TaskAssignmentHistoryModel.user_id == str(user_id),
            )
            .order_by(TaskAssignmentHistoryModel.created_at)
            .all()
        )
        return [self._model_to_domain(m) for m in models]

    def _model_to_domain(self, model: TaskAssignmentHistoryModel) -> TaskAssignmentHistory:
        return TaskAssignmentHistory(
            id=UUID(model.id) if isinstance(model.id, str) else model.id,
            task_id=UUID(model.task_id) if isinstance(model.task_id, str) else model.task_id,
            user_id=UUID(model.user_id) if isinstance(model.user_id, str) else model.user_id,
            action=model.action,
            abandonment_type=model.abandonment_type,
            created_at=model.created_at,
        )


class SqlAlchemyTaskAbandonmentRepository(TaskAbandonmentRepository):
    """SQLAlchemy implementation of TaskAbandonmentRepository (v3.0)."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, abandonment: TaskAbandonment) -> None:
        model = TaskAbandonmentModel(
            id=str(abandonment.id),
            task_id=str(abandonment.task_id),
            user_id=str(abandonment.user_id),
            abandonment_type=abandonment.abandonment_type,
            reason=abandonment.reason,
            initiated_by_user_id=str(abandonment.initiated_by_user_id),
            created_at=abandonment.created_at,
        )
        self.session.add(model)

    def find_by_id(self, abandonment_id: UUID) -> Optional[TaskAbandonment]:
        model = self.session.get(TaskAbandonmentModel, str(abandonment_id))
        if not model:
            return None
        return self._model_to_domain(model)

    def find_by_task_id(self, task_id: UUID) -> List[TaskAbandonment]:
        models = (
            self.session.query(TaskAbandonmentModel)
            .filter(TaskAbandonmentModel.task_id == str(task_id))
            .order_by(TaskAbandonmentModel.created_at)
            .all()
        )
        return [self._model_to_domain(m) for m in models]

    def find_by_user_id(self, user_id: UUID) -> List[TaskAbandonment]:
        models = (
            self.session.query(TaskAbandonmentModel)
            .filter(TaskAbandonmentModel.user_id == str(user_id))
            .order_by(TaskAbandonmentModel.created_at)
            .all()
        )
        return [self._model_to_domain(m) for m in models]

    def find_by_initiated_by_user_id(
        self, initiated_by_user_id: UUID
    ) -> List[TaskAbandonment]:
        models = (
            self.session.query(TaskAbandonmentModel)
            .filter(TaskAbandonmentModel.initiated_by_user_id == str(initiated_by_user_id))
            .order_by(TaskAbandonmentModel.created_at)
            .all()
        )
        return [self._model_to_domain(m) for m in models]

    def _model_to_domain(self, model: TaskAbandonmentModel) -> TaskAbandonment:
        return TaskAbandonment(
            id=UUID(model.id) if isinstance(model.id, str) else model.id,
            task_id=UUID(model.task_id) if isinstance(model.task_id, str) else model.task_id,
            user_id=UUID(model.user_id) if isinstance(model.user_id, str) else model.user_id,
            abandonment_type=model.abandonment_type,
            reason=model.reason,
            initiated_by_user_id=UUID(model.initiated_by_user_id) if isinstance(model.initiated_by_user_id, str) else model.initiated_by_user_id,
            created_at=model.created_at,
        )

