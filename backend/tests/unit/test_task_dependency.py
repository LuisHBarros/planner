"""Unit tests for TaskDependency."""
import pytest
from uuid import uuid4

from app.domain.exceptions import BusinessRuleViolation
from app.domain.models.task_dependency import TaskDependency
from app.domain.models.enums import DependencyType


class TestTaskDependency:
    """Test task dependency creation."""
    
    def test_create_dependency(self):
        """Test creating a valid dependency."""
        task_id = uuid4()
        depends_on_id = uuid4()
        
        dependency = TaskDependency.create(
            task_id=task_id,
            depends_on_task_id=depends_on_id,
        )
        
        assert dependency.task_id == task_id
        assert dependency.depends_on_task_id == depends_on_id
        assert dependency.dependency_type == DependencyType.BLOCKS
    
    def test_create_dependency_self_reference(self):
        """Test creating self-dependency (should fail)."""
        task_id = uuid4()
        
        with pytest.raises(BusinessRuleViolation) as exc:
            TaskDependency.create(
                task_id=task_id,
                depends_on_task_id=task_id,
            )
        
        assert exc.value.code == "self_dependency"
