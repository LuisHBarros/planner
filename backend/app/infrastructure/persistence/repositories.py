"""Repository implementations using SQLAlchemy."""
from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from app.domain.models.enums import (
    AbandonmentType,
    DependencyType,
    InviteStatus,
    MemberLevel,
    ProgressSource,
    ProjectStatus,
    ScheduleChangeReason,
    TaskStatus,
)
from app.domain.models.magic_link import MagicLink
from app.domain.models.notification_preference import NotificationPreference
from app.domain.models.project import Project
from app.domain.models.project_invite import ProjectInvite
from app.domain.models.project_member import ProjectMember
from app.domain.models.project_schedule_history import ProjectScheduleHistory
from app.domain.models.role import Role
from app.domain.models.task import Task
from app.domain.models.task_abandonment import TaskAbandonment
from app.domain.models.task_assignment_history import TaskAssignmentHistory
from app.domain.models.task_dependency import TaskDependency
from app.domain.models.task_report import TaskReport
from app.domain.models.task_schedule_history import TaskScheduleHistory
from app.domain.models.user import User
from app.domain.models.value_objects import (
    InviteToken,
    MagicLinkId,
    NotificationPreferenceId,
    ProjectId,
    ProjectInviteId,
    ProjectMemberId,
    ProjectScheduleHistoryId,
    RoleId,
    TaskAbandonmentId,
    TaskAssignmentHistoryId,
    TaskId,
    TaskReportId,
    TaskScheduleHistoryId,
    UserId,
    UtcDateTime,
)
from app.infrastructure.persistence.models import (
    MagicLinkModel,
    NotificationPreferenceModel,
    ProjectInviteModel,
    ProjectMemberModel,
    ProjectModel,
    ProjectScheduleHistoryModel,
    RoleModel,
    TaskAbandonmentModel,
    TaskAssignmentHistoryModel,
    TaskDependencyModel,
    TaskModel,
    TaskReportModel,
    TaskScheduleHistoryModel,
    UserModel,
)


def _uuid(value: str) -> UUID:
    return UUID(value)


class SqlAlchemyUserRepository:
    """User repository implementation."""

    def __init__(self, session: Session):
        self.session = session

    def save(self, user: User) -> None:
        self.session.merge(UserModel(
            id=str(user.id.value),
            email=user.email,
            name=user.name,
            created_at=user.created_at.value,
        ))

    def find_by_id(self, user_id: UserId) -> Optional[User]:
        model = self.session.get(UserModel, str(user_id.value))
        if model is None:
            return None
        return User(
            id=UserId(_uuid(model.id)),
            email=model.email,
            name=model.name,
            created_at=UtcDateTime(model.created_at),
        )

    def find_by_email(self, email: str) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.email == email)
        model = self.session.execute(stmt).scalars().first()
        if model is None:
            return None
        return User(
            id=UserId(_uuid(model.id)),
            email=model.email,
            name=model.name,
            created_at=UtcDateTime(model.created_at),
        )


class SqlAlchemyProjectRepository:
    """Project repository implementation."""

    def __init__(self, session: Session):
        self.session = session

    def save(self, project: Project) -> None:
        self.session.merge(ProjectModel(
            id=str(project.id.value),
            name=project.name,
            description=project.description,
            created_by=str(project.created_by.value),
            expected_end_date=project.expected_end_date.value if project.expected_end_date else None,
            status=project.status.value,
            llm_enabled=project.llm_enabled,
            llm_provider=project.llm_provider,
            llm_api_key_encrypted=project.llm_api_key_encrypted,
            created_at=project.created_at.value,
        ))

    def find_by_id(self, project_id: ProjectId) -> Optional[Project]:
        model = self.session.get(ProjectModel, str(project_id.value))
        if model is None:
            return None
        return Project(
            id=ProjectId(_uuid(model.id)),
            name=model.name,
            description=model.description,
            created_by=UserId(_uuid(model.created_by)),
            expected_end_date=UtcDateTime(model.expected_end_date) if model.expected_end_date else None,
            status=ProjectStatus(model.status),
            llm_enabled=model.llm_enabled,
            llm_provider=model.llm_provider,
            llm_api_key_encrypted=model.llm_api_key_encrypted,
            created_at=UtcDateTime(model.created_at),
        )

    def find_by_created_by(self, user_id: UserId) -> List[Project]:
        stmt = select(ProjectModel).where(ProjectModel.created_by == str(user_id.value))
        models = self.session.execute(stmt).scalars().all()
        return [self.find_by_id(ProjectId(_uuid(model.id))) for model in models]  # type: ignore[arg-type]

    def delete(self, project_id: ProjectId) -> None:
        self.session.execute(delete(ProjectModel).where(ProjectModel.id == str(project_id.value)))


class SqlAlchemyProjectMemberRepository:
    """Project member repository implementation."""

    def __init__(self, session: Session):
        self.session = session

    def save(self, member: ProjectMember) -> None:
        self.session.merge(ProjectMemberModel(
            id=str(member.id.value),
            project_id=str(member.project_id.value),
            user_id=str(member.user_id.value),
            role_id=str(member.role_id.value) if member.role_id else None,
            level=member.level.value,
            base_capacity=member.base_capacity,
            is_manager=member.is_manager,
            joined_at=member.joined_at.value,
        ))

    def find_by_id(self, member_id: ProjectMemberId) -> Optional[ProjectMember]:
        model = self.session.get(ProjectMemberModel, str(member_id.value))
        if model is None:
            return None
        return ProjectMember(
            id=ProjectMemberId(_uuid(model.id)),
            project_id=ProjectId(_uuid(model.project_id)),
            user_id=UserId(_uuid(model.user_id)),
            role_id=RoleId(_uuid(model.role_id)) if model.role_id else None,
            level=MemberLevel(model.level),
            base_capacity=model.base_capacity,
            is_manager=model.is_manager,
            joined_at=UtcDateTime(model.joined_at),
        )

    def list_by_project(self, project_id: ProjectId) -> List[ProjectMember]:
        stmt = select(ProjectMemberModel).where(ProjectMemberModel.project_id == str(project_id.value))
        models = self.session.execute(stmt).scalars().all()
        return [self.find_by_id(ProjectMemberId(_uuid(model.id))) for model in models]  # type: ignore[arg-type]

    def find_by_project_and_user(self, project_id: ProjectId, user_id: UserId) -> Optional[ProjectMember]:
        stmt = select(ProjectMemberModel).where(
            ProjectMemberModel.project_id == str(project_id.value),
            ProjectMemberModel.user_id == str(user_id.value),
        )
        model = self.session.execute(stmt).scalars().first()
        if model is None:
            return None
        return self.find_by_id(ProjectMemberId(_uuid(model.id)))


class SqlAlchemyRoleRepository:
    """Role repository implementation."""

    def __init__(self, session: Session):
        self.session = session

    def save(self, role: Role) -> None:
        self.session.merge(RoleModel(
            id=str(role.id.value),
            project_id=str(role.project_id.value),
            name=role.name,
            description=role.description,
            created_at=role.created_at.value,
        ))

    def find_by_id(self, role_id: RoleId) -> Optional[Role]:
        model = self.session.get(RoleModel, str(role_id.value))
        if model is None:
            return None
        return Role(
            id=RoleId(_uuid(model.id)),
            project_id=ProjectId(_uuid(model.project_id)),
            name=model.name,
            description=model.description,
            created_at=UtcDateTime(model.created_at),
        )

    def list_by_project(self, project_id: ProjectId) -> List[Role]:
        stmt = select(RoleModel).where(RoleModel.project_id == str(project_id.value))
        models = self.session.execute(stmt).scalars().all()
        return [self.find_by_id(RoleId(_uuid(model.id))) for model in models]  # type: ignore[arg-type]


class SqlAlchemyProjectInviteRepository:
    """Project invite repository implementation."""

    def __init__(self, session: Session):
        self.session = session

    def save(self, invite: ProjectInvite) -> None:
        self.session.merge(ProjectInviteModel(
            id=str(invite.id.value),
            project_id=str(invite.project_id.value),
            email=invite.email,
            token=str(invite.token),
            role_id=str(invite.role_id.value) if invite.role_id else None,
            status=invite.status.value,
            created_at=invite.created_at.value,
            expires_at=invite.expires_at.value if invite.expires_at else None,
        ))

    def find_by_id(self, invite_id: ProjectInviteId) -> Optional[ProjectInvite]:
        model = self.session.get(ProjectInviteModel, str(invite_id.value))
        if model is None:
            return None
        return ProjectInvite(
            id=ProjectInviteId(_uuid(model.id)),
            project_id=ProjectId(_uuid(model.project_id)),
            email=model.email,
            token=InviteToken(model.token),
            role_id=RoleId(_uuid(model.role_id)) if model.role_id else None,
            status=InviteStatus(model.status),
            created_at=UtcDateTime(model.created_at),
            expires_at=UtcDateTime(model.expires_at) if model.expires_at else None,
        )

    def find_by_token(self, token: InviteToken) -> Optional[ProjectInvite]:
        stmt = select(ProjectInviteModel).where(ProjectInviteModel.token == str(token))
        model = self.session.execute(stmt).scalars().first()
        if model is None:
            return None
        return self.find_by_id(ProjectInviteId(_uuid(model.id)))

    def list_by_project(self, project_id: ProjectId) -> List[ProjectInvite]:
        stmt = select(ProjectInviteModel).where(ProjectInviteModel.project_id == str(project_id.value))
        models = self.session.execute(stmt).scalars().all()
        return [self.find_by_id(ProjectInviteId(_uuid(model.id))) for model in models]  # type: ignore[arg-type]


class SqlAlchemyTaskRepository:
    """Task repository implementation."""

    def __init__(self, session: Session):
        self.session = session

    def save(self, task: Task) -> None:
        self.session.merge(TaskModel(
            id=str(task.id.value),
            project_id=str(task.project_id.value),
            title=task.title,
            description=task.description,
            status=task.status.value,
            difficulty=task.difficulty,
            role_id=str(task.role_id.value) if task.role_id else None,
            assigned_to=str(task.assigned_to.value) if task.assigned_to else None,
            expected_start_date=task.expected_start_date.value if task.expected_start_date else None,
            expected_end_date=task.expected_end_date.value if task.expected_end_date else None,
            actual_start_date=task.actual_start_date.value if task.actual_start_date else None,
            actual_end_date=task.actual_end_date.value if task.actual_end_date else None,
            created_at=task.created_at.value,
        ))

    def find_by_id(self, task_id: TaskId) -> Optional[Task]:
        model = self.session.get(TaskModel, str(task_id.value))
        if model is None:
            return None
        return Task(
            id=TaskId(_uuid(model.id)),
            project_id=ProjectId(_uuid(model.project_id)),
            title=model.title,
            description=model.description,
            status=TaskStatus(model.status),
            difficulty=model.difficulty,
            role_id=RoleId(_uuid(model.role_id)) if model.role_id else None,
            assigned_to=UserId(_uuid(model.assigned_to)) if model.assigned_to else None,
            expected_start_date=UtcDateTime(model.expected_start_date) if model.expected_start_date else None,
            expected_end_date=UtcDateTime(model.expected_end_date) if model.expected_end_date else None,
            actual_start_date=UtcDateTime(model.actual_start_date) if model.actual_start_date else None,
            actual_end_date=UtcDateTime(model.actual_end_date) if model.actual_end_date else None,
            created_at=UtcDateTime(model.created_at),
        )

    def list_by_project(self, project_id: ProjectId) -> List[Task]:
        stmt = select(TaskModel).where(TaskModel.project_id == str(project_id.value))
        models = self.session.execute(stmt).scalars().all()
        return [self.find_by_id(TaskId(_uuid(model.id))) for model in models]  # type: ignore[arg-type]


class SqlAlchemyTaskDependencyRepository:
    """Task dependency repository implementation."""

    def __init__(self, session: Session):
        self.session = session

    def save(self, dependency: TaskDependency) -> None:
        self.session.merge(TaskDependencyModel(
            task_id=str(dependency.task_id.value),
            depends_on_id=str(dependency.depends_on_id.value),
            dependency_type=dependency.dependency_type.value,
            created_at=dependency.created_at.value,
        ))

    def list_by_task(self, task_id: TaskId) -> List[TaskDependency]:
        stmt = select(TaskDependencyModel).where(TaskDependencyModel.task_id == str(task_id.value))
        models = self.session.execute(stmt).scalars().all()
        return [
            TaskDependency(
                task_id=TaskId(_uuid(model.task_id)),
                depends_on_id=TaskId(_uuid(model.depends_on_id)),
                dependency_type=DependencyType(model.dependency_type),
                created_at=UtcDateTime(model.created_at),
            )
            for model in models
        ]

    def delete(self, task_id: TaskId, depends_on_id: TaskId) -> None:
        self.session.execute(delete(TaskDependencyModel).where(
            TaskDependencyModel.task_id == str(task_id.value),
            TaskDependencyModel.depends_on_id == str(depends_on_id.value),
        ))


class SqlAlchemyTaskReportRepository:
    """Task report repository implementation."""

    def __init__(self, session: Session):
        self.session = session

    def save(self, report: TaskReport) -> None:
        self.session.merge(TaskReportModel(
            id=str(report.id.value),
            task_id=str(report.task_id.value),
            author_id=str(report.author_id.value),
            progress=report.progress,
            source=report.source.value,
            note=report.note,
            created_at=report.created_at.value,
        ))

    def list_by_task(self, task_id: TaskId) -> List[TaskReport]:
        stmt = select(TaskReportModel).where(TaskReportModel.task_id == str(task_id.value))
        models = self.session.execute(stmt).scalars().all()
        return [
            TaskReport(
                id=TaskReportId(_uuid(model.id)),
                task_id=TaskId(_uuid(model.task_id)),
                author_id=UserId(_uuid(model.author_id)),
                progress=model.progress,
                source=ProgressSource(model.source),
                note=model.note,
                created_at=UtcDateTime(model.created_at),
            )
            for model in models
        ]


class SqlAlchemyTaskAbandonmentRepository:
    """Task abandonment repository implementation."""

    def __init__(self, session: Session):
        self.session = session

    def save(self, abandonment: TaskAbandonment) -> None:
        self.session.merge(TaskAbandonmentModel(
            id=str(abandonment.id.value),
            task_id=str(abandonment.task_id.value),
            user_id=str(abandonment.user_id.value),
            abandonment_type=abandonment.abandonment_type.value,
            note=abandonment.note,
            created_at=abandonment.created_at.value,
        ))

    def list_by_task(self, task_id: TaskId) -> List[TaskAbandonment]:
        stmt = select(TaskAbandonmentModel).where(TaskAbandonmentModel.task_id == str(task_id.value))
        models = self.session.execute(stmt).scalars().all()
        return [
            TaskAbandonment(
                id=TaskAbandonmentId(_uuid(model.id)),
                task_id=TaskId(_uuid(model.task_id)),
                user_id=UserId(_uuid(model.user_id)),
                abandonment_type=AbandonmentType(model.abandonment_type),
                note=model.note,
                created_at=UtcDateTime(model.created_at),
            )
            for model in models
        ]


class SqlAlchemyTaskAssignmentHistoryRepository:
    """Task assignment history repository implementation."""

    def __init__(self, session: Session):
        self.session = session

    def save(self, history: TaskAssignmentHistory) -> None:
        self.session.merge(TaskAssignmentHistoryModel(
            id=str(history.id.value),
            task_id=str(history.task_id.value),
            user_id=str(history.user_id.value),
            assigned_at=history.assigned_at.value,
            unassigned_at=history.unassigned_at.value if history.unassigned_at else None,
            assignment_reason=history.assignment_reason,
        ))

    def list_by_task(self, task_id: TaskId) -> List[TaskAssignmentHistory]:
        stmt = select(TaskAssignmentHistoryModel).where(TaskAssignmentHistoryModel.task_id == str(task_id.value))
        models = self.session.execute(stmt).scalars().all()
        return [
            TaskAssignmentHistory(
                id=TaskAssignmentHistoryId(_uuid(model.id)),
                task_id=TaskId(_uuid(model.task_id)),
                user_id=UserId(_uuid(model.user_id)),
                assigned_at=UtcDateTime(model.assigned_at),
                unassigned_at=UtcDateTime(model.unassigned_at) if model.unassigned_at else None,
                assignment_reason=model.assignment_reason,
            )
            for model in models
        ]


class SqlAlchemyScheduleHistoryRepository:
    """Schedule history repository implementation."""

    def __init__(self, session: Session):
        self.session = session

    def save_task_history(self, history: TaskScheduleHistory) -> None:
        self.session.merge(TaskScheduleHistoryModel(
            id=str(history.id.value),
            task_id=str(history.task_id.value),
            previous_start=history.previous_start.value,
            previous_end=history.previous_end.value,
            new_start=history.new_start.value,
            new_end=history.new_end.value,
            reason=history.reason.value,
            created_at=history.created_at.value,
        ))

    def save_project_history(self, history: ProjectScheduleHistory) -> None:
        self.session.merge(ProjectScheduleHistoryModel(
            id=str(history.id.value),
            project_id=str(history.project_id.value),
            previous_end=history.previous_end.value,
            new_end=history.new_end.value,
            reason=history.reason.value,
            created_at=history.created_at.value,
        ))

    def list_task_history(self, task_id: TaskId) -> List[TaskScheduleHistory]:
        stmt = select(TaskScheduleHistoryModel).where(TaskScheduleHistoryModel.task_id == str(task_id.value))
        models = self.session.execute(stmt).scalars().all()
        return [
            TaskScheduleHistory(
                id=TaskScheduleHistoryId(_uuid(model.id)),
                task_id=TaskId(_uuid(model.task_id)),
                previous_start=UtcDateTime(model.previous_start),
                previous_end=UtcDateTime(model.previous_end),
                new_start=UtcDateTime(model.new_start),
                new_end=UtcDateTime(model.new_end),
                reason=ScheduleChangeReason(model.reason),
                created_at=UtcDateTime(model.created_at),
            )
            for model in models
        ]

    def list_project_history(self, project_id: ProjectId) -> List[ProjectScheduleHistory]:
        stmt = select(ProjectScheduleHistoryModel).where(
            ProjectScheduleHistoryModel.project_id == str(project_id.value)
        )
        models = self.session.execute(stmt).scalars().all()
        return [
            ProjectScheduleHistory(
                id=ProjectScheduleHistoryId(_uuid(model.id)),
                project_id=ProjectId(_uuid(model.project_id)),
                previous_end=UtcDateTime(model.previous_end),
                new_end=UtcDateTime(model.new_end),
                reason=ScheduleChangeReason(model.reason),
                created_at=UtcDateTime(model.created_at),
            )
            for model in models
        ]


class SqlAlchemyNotificationPreferenceRepository:
    """Notification preference repository implementation."""

    def __init__(self, session: Session):
        self.session = session

    def save(self, preference: NotificationPreference) -> None:
        self.session.merge(NotificationPreferenceModel(
            id=str(preference.id.value),
            project_id=str(preference.project_id.value),
            user_id=str(preference.user_id.value),
            email_enabled=preference.email_enabled,
            toast_enabled=preference.toast_enabled,
            created_at=preference.created_at.value,
        ))

    def find_by_user_and_project(
        self,
        user_id: UserId,
        project_id: ProjectId,
    ) -> Optional[NotificationPreference]:
        stmt = select(NotificationPreferenceModel).where(
            NotificationPreferenceModel.user_id == str(user_id.value),
            NotificationPreferenceModel.project_id == str(project_id.value),
        )
        model = self.session.execute(stmt).scalars().first()
        if model is None:
            return None
        return NotificationPreference(
            id=NotificationPreferenceId(_uuid(model.id)),
            project_id=ProjectId(_uuid(model.project_id)),
            user_id=UserId(_uuid(model.user_id)),
            email_enabled=model.email_enabled,
            toast_enabled=model.toast_enabled,
            created_at=UtcDateTime(model.created_at),
        )


class SqlAlchemyMagicLinkRepository:
    """Magic link repository implementation."""

    def __init__(self, session: Session):
        self.session = session

    def save(self, magic_link: MagicLink) -> None:
        self.session.merge(MagicLinkModel(
            id=str(magic_link.id.value),
            token=str(magic_link.token),
            user_id=str(magic_link.user_id.value),
            expires_at=magic_link.expires_at.value,
            consumed_at=magic_link.consumed_at.value if magic_link.consumed_at else None,
        ))

    def find_by_id(self, link_id: MagicLinkId) -> Optional[MagicLink]:
        model = self.session.get(MagicLinkModel, str(link_id.value))
        if model is None:
            return None
        return MagicLink(
            id=MagicLinkId(_uuid(model.id)),
            token=InviteToken(model.token),
            user_id=UserId(_uuid(model.user_id)),
            expires_at=UtcDateTime(model.expires_at),
            consumed_at=UtcDateTime(model.consumed_at) if model.consumed_at else None,
        )

    def find_by_token(self, token: InviteToken) -> Optional[MagicLink]:
        stmt = select(MagicLinkModel).where(MagicLinkModel.token == str(token))
        model = self.session.execute(stmt).scalars().first()
        if model is None:
            return None
        return self.find_by_id(MagicLinkId(_uuid(model.id)))
