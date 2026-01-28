"""Unit tests for ranking service (BR-011)."""
from app.domain.services.ranking import (
    calculate_rank_index,
    rebalance_ranks,
    should_rebalance,
)
from app.domain.models.task import Task
from app.domain.models.enums import TaskStatus, TaskPriority


class TestCalculateRankIndex:
    """Test rank index calculation."""
    
    def test_empty_list(self):
        """Test calculating rank for empty list."""
        rank = calculate_rank_index(0, [])
        assert rank == 1.0
    
    def test_insert_at_beginning(self):
        """Test inserting at beginning."""
        tasks = [
            Task.create(
                project_id=None,
                title="Task 1",
                description="",
                role_responsible_id=None,
                rank_index=10.0,
            ),
            Task.create(
                project_id=None,
                title="Task 2",
                description="",
                role_responsible_id=None,
                rank_index=20.0,
            ),
        ]
        
        rank = calculate_rank_index(0, tasks)
        assert rank == 9.0
    
    def test_insert_at_end(self):
        """Test inserting at end."""
        tasks = [
            Task.create(
                project_id=None,
                title="Task 1",
                description="",
                role_responsible_id=None,
                rank_index=10.0,
            ),
            Task.create(
                project_id=None,
                title="Task 2",
                description="",
                role_responsible_id=None,
                rank_index=20.0,
            ),
        ]
        
        rank = calculate_rank_index(2, tasks)
        assert rank == 21.0
    
    def test_insert_between(self):
        """Test inserting between two tasks."""
        tasks = [
            Task.create(
                project_id=None,
                title="Task 1",
                description="",
                role_responsible_id=None,
                rank_index=10.0,
            ),
            Task.create(
                project_id=None,
                title="Task 2",
                description="",
                role_responsible_id=None,
                rank_index=20.0,
            ),
        ]
        
        rank = calculate_rank_index(1, tasks)
        assert rank == 15.0


class TestRebalanceRanks:
    """Test rank rebalancing."""
    
    def test_rebalance_ranks(self):
        """Test rebalancing ranks."""
        tasks = [
            Task.create(
                project_id=None,
                title="Task 1",
                description="",
                role_responsible_id=None,
                rank_index=1.0,
            ),
            Task.create(
                project_id=None,
                title="Task 2",
                description="",
                role_responsible_id=None,
                rank_index=1.0001,
            ),
            Task.create(
                project_id=None,
                title="Task 3",
                description="",
                role_responsible_id=None,
                rank_index=1.0002,
            ),
        ]
        
        rebalance_ranks(tasks)
        
        assert tasks[0].rank_index == 10.0
        assert tasks[1].rank_index == 20.0
        assert tasks[2].rank_index == 30.0


class TestShouldRebalance:
    """Test rebalance detection."""
    
    def test_should_rebalance_true(self):
        """Test detecting need for rebalancing."""
        tasks = [
            Task.create(
                project_id=None,
                title="Task 1",
                description="",
                role_responsible_id=None,
                rank_index=10.0,
            ),
            Task.create(
                project_id=None,
                title="Task 2",
                description="",
                role_responsible_id=None,
                rank_index=10.00005,  # Very close
            ),
        ]
        
        assert should_rebalance(tasks) is True
    
    def test_should_rebalance_false(self):
        """Test not needing rebalancing."""
        tasks = [
            Task.create(
                project_id=None,
                title="Task 1",
                description="",
                role_responsible_id=None,
                rank_index=10.0,
            ),
            Task.create(
                project_id=None,
                title="Task 2",
                description="",
                role_responsible_id=None,
                rank_index=20.0,
            ),
        ]
        
        assert should_rebalance(tasks) is False
