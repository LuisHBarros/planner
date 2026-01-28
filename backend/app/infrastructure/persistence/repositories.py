"""SQLAlchemy repository implementations for domain repositories."""
from typing import List, Optional
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
from app.domain.models.enums import TaskStatus
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
)


class SqlAlchemyCompanyRepository(CompanyRepository):
    """SQLAlchemy implementation of CompanyRepository."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, company: Company) -> None:
        model = self.session.get(CompanyModel, company.id) or CompanyModel(id=company.id)
        model.name = company.name
        model.slug = company.slug
        model.plan = company.plan
        model.billing_email = company.billing_email
        model.ai_enabled = company.ai_enabled
        model.ai_provider = company.ai_provider
        model.ai_api_key = company.ai_api_key
        self.session.add(model)

    def find_by_id(self, company_id: UUID) -> Optional[Company]:
        model = self.session.get(CompanyModel, company_id)
        if not model:
            return None
        return Company(
            id=model.id,
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
            id=model.id,
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
                id=m.id,
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
        model = self.session.get(TeamModel, team.id) or TeamModel(id=team.id)
        model.company_id = team.company_id
        model.name = team.name
        model.description = team.description
        model.default_language = team.default_language
        self.session.add(model)

    def find_by_id(self, team_id: UUID) -> Optional[Team]:
        model = self.session.get(TeamModel, team_id)
        if not model:
            return None
        return Team(
            id=model.id,
            company_id=model.company_id,
            name=model.name,
            description=model.description,
            default_language=model.default_language,
            created_at=model.created_at,
        )

    def find_by_company_id(self, company_id: UUID) -> List[Team]:
        models = (
            self.session.query(TeamModel)
            .filter(TeamModel.company_id == company_id)
            .all()
        )
        return [
            Team(
                id=m.id,
                company_id=m.company_id,
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
                id=m.id,
                company_id=m.company_id,
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
            .filter(TeamModel.company_id == company_id, TeamModel.name == name)
            .one_or_none()
        )
        if not model:
            return None
        return Team(
            id=model.id,
            company_id=model.company_id,
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
        model = self.session.get(UserModel, user.id) or UserModel(id=user.id)
        model.email = user.email
        model.name = user.name
        model.preferred_language = user.preferred_language
        model.avatar_url = user.avatar_url
        self.session.add(model)

    def find_by_id(self, user_id: UUID) -> Optional[User]:
        model = self.session.get(UserModel, user_id)
        if not model:
            return None
        return User(
            id=model.id,
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
            id=model.id,
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
                id=m.id,
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
        model = self.session.get(TeamMemberModel, member.id) or TeamMemberModel(
            id=member.id
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
        model = self.session.get(RoleModel, role.id) or RoleModel(id=role.id)
        model.team_id = role.team_id
        model.name = role.name
        model.level = role.level
        model.base_capacity = role.base_capacity
        model.description = role.description
        self.session.add(model)

    def find_by_id(self, role_id: UUID) -> Optional[Role]:
        model = self.session.get(RoleModel, role_id)
        if not model:
            return None
        return Role(
            id=model.id,
            team_id=model.team_id,
            name=model.name,
            level=model.level,
            base_capacity=model.base_capacity,
            description=model.description,
            created_at=model.created_at,
        )

    def find_by_team_id(self, team_id: UUID) -> List[Role]:
        models = (
            self.session.query(RoleModel)
            .filter(RoleModel.team_id == team_id)
            .all()
        )
        return [
            Role(
                id=m.id,
                team_id=m.team_id,
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
                id=m.id,
                team_id=m.team_id,
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
            .filter(RoleModel.team_id == team_id, RoleModel.name == name)
            .one_or_none()
        )
        if not model:
            return None
        return Role(
            id=model.id,
            team_id=model.team_id,
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
        model = self.session.get(ProjectModel, project.id) or ProjectModel(id=project.id)
        model.team_id = project.team_id
        model.name = project.name
        model.description = project.description
        model.status = project.status
        self.session.add(model)

    def find_by_id(self, project_id: UUID) -> Optional[Project]:
        model = self.session.get(ProjectModel, project_id)
        if not model:
            return None
        return Project(
            id=model.id,
            team_id=model.team_id,
            name=model.name,
            description=model.description,
            status=model.status,
            created_at=model.created_at,
        )

    def find_by_team_id(self, team_id: UUID) -> List[Project]:
        models = (
            self.session.query(ProjectModel)
            .filter(ProjectModel.team_id == team_id)
            .all()
        )
        return [
            Project(
                id=m.id,
                team_id=m.team_id,
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
                id=m.id,
                team_id=m.team_id,
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
            .filter(ProjectModel.team_id == team_id, ProjectModel.name == name)
            .one_or_none()
        )
        if not model:
            return None
        return Project(
            id=model.id,
            team_id=model.team_id,
            name=model.name,
            description=model.description,
            status=model.status,
            created_at=model.created_at,
        )


class SqlAlchemyTaskRepository(TaskRepository):
    """SQLAlchemy implementation of TaskRepository."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def _to_domain(self, model: TaskModel) -> Task:
        return Task(
            id=model.id,
            project_id=model.project_id,
            title=model.title,
            description=model.description,
            role_responsible_id=model.role_responsible_id,
            status=model.status,
            priority=model.priority,
            rank_index=model.rank_index,
            user_responsible_id=model.user_responsible_id,
            completion_percentage=model.completion_percentage,
            completion_source=model.completion_source,
            due_date=model.due_date,
            expected_start_date=model.expected_start_date,
            expected_end_date=model.expected_end_date,
            actual_start_date=model.actual_start_date,
            actual_end_date=model.actual_end_date,
            is_delayed=model.is_delayed,
            blocked_reason=model.blocked_reason,
            created_at=model.created_at,
            updated_at=model.updated_at,
            completed_at=model.completed_at,
        )

    def save(self, task: Task) -> None:
        model = self.session.get(TaskModel, task.id) or TaskModel(id=task.id)
        model.project_id = task.project_id
        model.title = task.title
        model.description = task.description
        model.role_responsible_id = task.role_responsible_id
        model.status = task.status
        model.priority = task.priority
        model.rank_index = task.rank_index
        model.user_responsible_id = task.user_responsible_id
        model.completion_percentage = task.completion_percentage
        model.completion_source = task.completion_source
        model.due_date = task.due_date
        model.expected_start_date = task.expected_start_date
        model.expected_end_date = task.expected_end_date
        model.actual_start_date = task.actual_start_date
        model.actual_end_date = task.actual_end_date
        model.is_delayed = task.is_delayed
        model.blocked_reason = task.blocked_reason
        model.created_at = task.created_at
        model.updated_at = task.updated_at
        model.completed_at = task.completed_at
        self.session.add(model)

    def find_by_id(self, task_id: UUID) -> Optional[Task]:
        model = self.session.get(TaskModel, task_id)
        if not model:
            return None
        return self._to_domain(model)

    def find_by_project_id(self, project_id: UUID) -> List[Task]:
        models = (
            self.session.query(TaskModel)
            .filter(TaskModel.project_id == project_id)
            .order_by(TaskModel.rank_index)
            .all()
        )
        return [self._to_domain(m) for m in models]

    def find_by_role_id(
        self, role_id: UUID, status: Optional[TaskStatus] = None
    ) -> List[Task]:
        query = self.session.query(TaskModel).filter(
            TaskModel.role_responsible_id == role_id
        )
        if status is not None:
            query = query.filter(TaskModel.status == status)
        models = query.order_by(TaskModel.rank_index).all()
        return [self._to_domain(m) for m in models]

    def find_by_user_id(self, user_id: UUID) -> List[Task]:
        models = (
            self.session.query(TaskModel)
            .filter(TaskModel.user_responsible_id == user_id)
            .order_by(TaskModel.rank_index)
            .all()
        )
        return [self._to_domain(m) for m in models]

    def find_dependent_tasks(self, task_id: UUID) -> List[Task]:
        deps = (
            self.session.query(TaskDependencyModel)
            .filter(TaskDependencyModel.depends_on_task_id == task_id)
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
            self.session.get(TaskDependencyModel, dependency.id)
            or TaskDependencyModel(id=dependency.id)
        )
        model.task_id = dependency.task_id
        model.depends_on_task_id = dependency.depends_on_task_id
        model.dependency_type = dependency.dependency_type
        model.created_at = dependency.created_at
        self.session.add(model)

    def find_by_id(self, dependency_id: UUID) -> Optional[TaskDependency]:
        model = self.session.get(TaskDependencyModel, dependency_id)
        if not model:
            return None
        return TaskDependency(
            id=model.id,
            task_id=model.task_id,
            depends_on_task_id=model.depends_on_task_id,
            dependency_type=model.dependency_type,
            created_at=model.created_at,
        )

    def find_by_task_id(self, task_id: UUID) -> List[TaskDependency]:
        models = (
            self.session.query(TaskDependencyModel)
            .filter(TaskDependencyModel.task_id == task_id)
            .all()
        )
        return [
            TaskDependency(
                id=m.id,
                task_id=m.task_id,
                depends_on_task_id=m.depends_on_task_id,
                dependency_type=m.dependency_type,
                created_at=m.created_at,
            )
            for m in models
        ]

    def find_by_depends_on_task_id(self, depends_on_task_id: UUID) -> List[TaskDependency]:
        models = (
            self.session.query(TaskDependencyModel)
            .filter(TaskDependencyModel.depends_on_task_id == depends_on_task_id)
            .all()
        )
        return [
            TaskDependency(
                id=m.id,
                task_id=m.task_id,
                depends_on_task_id=m.depends_on_task_id,
                dependency_type=m.dependency_type,
                created_at=m.created_at,
            )
            for m in models
        ]

    def delete(self, dependency_id: UUID) -> None:
        model = self.session.get(TaskDependencyModel, dependency_id)
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
        model = self.session.get(TeamInviteModel, invite.id) or TeamInviteModel(
            id=invite.id
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
        model = self.session.get(NoteModel, note.id) or NoteModel(id=note.id)
        model.task_id = note.task_id
        model.content = note.content
        model.note_type = note.note_type
        model.author_id = note.author_id
        model.created_at = note.created_at
        model.updated_at = note.updated_at
        self.session.add(model)

    def find_by_id(self, note_id: UUID) -> Optional[Note]:
        model = self.session.get(NoteModel, note_id)
        if not model:
            return None
        return Note(
            id=model.id,
            task_id=model.task_id,
            content=model.content,
            note_type=model.note_type,
            author_id=model.author_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def find_by_task_id(self, task_id: UUID) -> List[Note]:
        models = (
            self.session.query(NoteModel)
            .filter(NoteModel.task_id == task_id)
            .order_by(NoteModel.created_at)
            .all()
        )
        return [
            Note(
                id=m.id,
                task_id=m.task_id,
                content=m.content,
                note_type=m.note_type,
                author_id=m.author_id,
                created_at=m.created_at,
                updated_at=m.updated_at,
            )
            for m in models
        ]


