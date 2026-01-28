"""Unit tests for WorkloadCalculator (BR-010)."""
from app.domain.services.workload_calculator import WorkloadCalculator
from app.domain.models.role import Role
from app.domain.models.enums import RoleLevel


class TestWorkloadCalculator:
    """Test workload health calculation."""
    
    def test_calculate_tranquilo(self):
        """Test calculating tranquilo status."""
        role = Role.create(
            team_id=None,
            name="Backend",
            level=RoleLevel.SENIOR,
            base_capacity=5,
        )
        
        # tasks_per_person = 3 / 2 = 1.5
        # baseline = 5
        # 1.5 <= 5 * 0.8 = 4.0 → tranquilo
        health = WorkloadCalculator.calculate_health(
            role=role,
            active_tasks=3,
            users_count=2,
            baseline=5.0,
        )
        
        assert health.status == "tranquilo"
        assert health.tasks_per_person == 1.5
    
    def test_calculate_saudavel(self):
        """Test calculating saudável status."""
        role = Role.create(
            team_id=None,
            name="Backend",
            level=RoleLevel.SENIOR,
            base_capacity=5,
        )
        
        # tasks_per_person = 4.5 / 1 = 4.5
        # baseline = 5
        # 4.5 <= 5 → saudável
        health = WorkloadCalculator.calculate_health(
            role=role,
            active_tasks=4,
            users_count=1,
            baseline=5.0,
        )
        
        assert health.status == "saudável"
    
    def test_calculate_apertado(self):
        """Test calculating apertado status."""
        role = Role.create(
            team_id=None,
            name="Backend",
            level=RoleLevel.SENIOR,
            base_capacity=5,
        )
        
        # tasks_per_person = 6 / 1 = 6.0
        # baseline = 5
        # 6.0 <= 5 * 1.3 = 6.5 → apertado
        health = WorkloadCalculator.calculate_health(
            role=role,
            active_tasks=6,
            users_count=1,
            baseline=5.0,
        )
        
        assert health.status == "apertado"
    
    def test_calculate_impossivel(self):
        """Test calculating impossível status."""
        role = Role.create(
            team_id=None,
            name="Backend",
            level=RoleLevel.SENIOR,
            base_capacity=5,
        )
        
        # tasks_per_person = 7 / 1 = 7.0
        # baseline = 5
        # 7.0 > 5 * 1.3 = 6.5 → impossível
        health = WorkloadCalculator.calculate_health(
            role=role,
            active_tasks=7,
            users_count=1,
            baseline=5.0,
        )
        
        assert health.status == "impossível"
    
    def test_calculate_no_users(self):
        """Test calculating with no users."""
        role = Role.create(
            team_id=None,
            name="Backend",
            level=RoleLevel.SENIOR,
            base_capacity=5,
        )
        
        health = WorkloadCalculator.calculate_health(
            role=role,
            active_tasks=10,
            users_count=0,
            baseline=5.0,
        )
        
        assert health.status == "no_users"
        assert health.tasks_per_person == 0.0
