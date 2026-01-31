"""Tests for TaskReport entity."""
from app.domain.models.task_report import TaskReport
from app.domain.models.enums import ProgressSource
from app.domain.models.value_objects import TaskId, UserId


def test_task_report_create():
    """TaskReport.create stores progress and source."""
    report = TaskReport.create(
        task_id=TaskId(),
        author_id=UserId(),
        progress=40,
        source=ProgressSource.MANUAL,
        note="Update",
    )
    assert report.progress == 40
    assert report.source == ProgressSource.MANUAL
    assert report.note == "Update"
