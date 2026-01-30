"""Unit tests for ProjectMember domain model (v3.0)."""
import pytest
from uuid import uuid4

from app.domain.models.project_member import ProjectMember, LEVEL_MULTIPLIERS
from app.domain.models.enums import ProjectMemberRole, RoleLevel


class TestProjectMemberCreation:
    """Test ProjectMember creation."""

    def test_create_project_member(self):
        """Test creating a project member."""
        project_id = uuid4()
        user_id = uuid4()

        member = ProjectMember.create(
            project_id=project_id,
            user_id=user_id,
            role=ProjectMemberRole.EMPLOYEE,
            level=RoleLevel.MID,
        )

        assert member.project_id == project_id
        assert member.user_id == user_id
        assert member.role == ProjectMemberRole.EMPLOYEE
        assert member.level == RoleLevel.MID
        assert member.is_active is True
        assert member.joined_at is not None
        assert member.left_at is None

    def test_create_manager(self):
        """Test creating a project manager."""
        project_id = uuid4()
        user_id = uuid4()

        member = ProjectMember.create_manager(
            project_id=project_id,
            user_id=user_id,
        )

        assert member.role == ProjectMemberRole.MANAGER
        assert member.level == RoleLevel.LEAD  # Default level for managers

    def test_create_employee(self):
        """Test creating a project employee."""
        project_id = uuid4()
        user_id = uuid4()

        member = ProjectMember.create_employee(
            project_id=project_id,
            user_id=user_id,
            level=RoleLevel.JUNIOR,
        )

        assert member.role == ProjectMemberRole.EMPLOYEE
        assert member.level == RoleLevel.JUNIOR


class TestProjectMemberRoleChecks:
    """Test role checking methods (BR-PROJ-002)."""

    def test_is_manager_true(self):
        """Test is_manager returns True for managers."""
        member = ProjectMember.create_manager(
            project_id=uuid4(),
            user_id=uuid4(),
        )
        assert member.is_manager() is True
        assert member.is_employee() is False

    def test_is_manager_false(self):
        """Test is_manager returns False for employees."""
        member = ProjectMember.create_employee(
            project_id=uuid4(),
            user_id=uuid4(),
            level=RoleLevel.MID,
        )
        assert member.is_manager() is False
        assert member.is_employee() is True


class TestLevelMultipliers:
    """Test level multiplier calculations (BR-WORK-001)."""

    def test_junior_multiplier(self):
        """Test JUNIOR level has 0.6 multiplier."""
        member = ProjectMember.create_employee(
            project_id=uuid4(),
            user_id=uuid4(),
            level=RoleLevel.JUNIOR,
        )
        assert member.get_level_multiplier() == 0.6

    def test_mid_multiplier(self):
        """Test MID level has 1.0 multiplier."""
        member = ProjectMember.create_employee(
            project_id=uuid4(),
            user_id=uuid4(),
            level=RoleLevel.MID,
        )
        assert member.get_level_multiplier() == 1.0

    def test_senior_multiplier(self):
        """Test SENIOR level has 1.3 multiplier."""
        member = ProjectMember.create_employee(
            project_id=uuid4(),
            user_id=uuid4(),
            level=RoleLevel.SENIOR,
        )
        assert member.get_level_multiplier() == 1.3

    def test_specialist_multiplier(self):
        """Test SPECIALIST level has 1.2 multiplier."""
        member = ProjectMember.create_employee(
            project_id=uuid4(),
            user_id=uuid4(),
            level=RoleLevel.SPECIALIST,
        )
        assert member.get_level_multiplier() == 1.2

    def test_lead_multiplier(self):
        """Test LEAD level has 1.1 multiplier."""
        member = ProjectMember.create_employee(
            project_id=uuid4(),
            user_id=uuid4(),
            level=RoleLevel.LEAD,
        )
        assert member.get_level_multiplier() == 1.1

    def test_all_levels_have_multipliers(self):
        """Verify all RoleLevels have defined multipliers."""
        for level in RoleLevel:
            assert level in LEVEL_MULTIPLIERS


class TestCapacityCalculation:
    """Test capacity calculation (BR-WORK-001)."""

    def test_junior_capacity(self):
        """Test capacity calculation for JUNIOR level."""
        member = ProjectMember.create_employee(
            project_id=uuid4(),
            user_id=uuid4(),
            level=RoleLevel.JUNIOR,
        )
        # base_capacity=10, multiplier=0.6 -> 6.0
        assert member.calculate_capacity(10) == 6.0

    def test_mid_capacity(self):
        """Test capacity calculation for MID level."""
        member = ProjectMember.create_employee(
            project_id=uuid4(),
            user_id=uuid4(),
            level=RoleLevel.MID,
        )
        # base_capacity=10, multiplier=1.0 -> 10.0
        assert member.calculate_capacity(10) == 10.0

    def test_senior_capacity(self):
        """Test capacity calculation for SENIOR level."""
        member = ProjectMember.create_employee(
            project_id=uuid4(),
            user_id=uuid4(),
            level=RoleLevel.SENIOR,
        )
        # base_capacity=10, multiplier=1.3 -> 13.0
        assert member.calculate_capacity(10) == 13.0


class TestProjectMemberLifecycle:
    """Test project member lifecycle methods."""

    def test_deactivate(self):
        """Test deactivating a project member."""
        member = ProjectMember.create_employee(
            project_id=uuid4(),
            user_id=uuid4(),
            level=RoleLevel.MID,
        )
        assert member.is_active is True

        member.deactivate()

        assert member.is_active is False
        assert member.left_at is not None

    def test_reactivate(self):
        """Test reactivating a project member."""
        member = ProjectMember.create_employee(
            project_id=uuid4(),
            user_id=uuid4(),
            level=RoleLevel.MID,
        )
        member.deactivate()
        assert member.is_active is False

        member.reactivate()

        assert member.is_active is True
        assert member.left_at is None
