"""Tests for the crontabs module - models, registry, and scheduler."""

import pytest
from pathlib import Path

from universal_mcp.crontabs.models import CrontabJob, CrontabExecution
from universal_mcp.crontabs.registry import CrontabRegistry
from universal_mcp.crontabs.scheduler import CrontabScheduler


# -- Model Tests -------------------------------------------------------


class TestCrontabJob:
    """Tests for CrontabJob model."""

    def test_valid_job(self):
        job = CrontabJob(
            name="test-job",
            schedule="*/5 * * * *",
            prompt="Run a test",
        )
        assert job.name == "test-job"
        assert job.schedule == "*/5 * * * *"
        assert job.prompt == "Run a test"
        assert job.enabled is True
        assert job.model is None
        assert job.timezone == "UTC"
        assert job.max_instances == 1

    def test_invalid_cron_expression(self):
        with pytest.raises(ValueError, match="Invalid cron expression"):
            CrontabJob(
                name="bad-cron",
                schedule="* * *",
                prompt="test",
            )

    def test_invalid_cron_too_many_fields(self):
        with pytest.raises(ValueError, match="Invalid cron expression"):
            CrontabJob(
                name="bad-cron",
                schedule="* * * * * *",
                prompt="test",
            )

    def test_empty_name_rejected(self):
        with pytest.raises(ValueError):
            CrontabJob(name="", schedule="* * * * *", prompt="test")

    def test_empty_prompt_rejected(self):
        with pytest.raises(ValueError):
            CrontabJob(name="test", schedule="* * * * *", prompt="")

    def test_name_stripped(self):
        job = CrontabJob(name="  my-job  ", schedule="* * * * *", prompt="test")
        assert job.name == "my-job"

    def test_schedule_stripped(self):
        job = CrontabJob(name="test", schedule="  */5 * * * *  ", prompt="test")
        assert job.schedule == "*/5 * * * *"

    def test_full_job_with_all_fields(self):
        job = CrontabJob(
            name="full-job",
            schedule="0 9 * * 1-5",
            prompt="Generate weekly report",
            model="sonnet",
            enabled=False,
            description="Weekly report generation",
            tags=["report", "weekly"],
            max_instances=3,
            timezone="America/New_York",
        )
        assert job.model == "sonnet"
        assert job.enabled is False
        assert job.description == "Weekly report generation"
        assert job.tags == ["report", "weekly"]
        assert job.max_instances == 3
        assert job.timezone == "America/New_York"

    def test_serialization_roundtrip(self):
        job = CrontabJob(
            name="roundtrip",
            schedule="0 * * * *",
            prompt="Test prompt",
        )
        data = job.model_dump()
        restored = CrontabJob.model_validate(data)
        assert restored.name == job.name
        assert restored.schedule == job.schedule
        assert restored.prompt == job.prompt


class TestCrontabExecution:
    """Tests for CrontabExecution model."""

    def test_default_execution(self):
        ex = CrontabExecution(job_name="test-job")
        assert ex.job_name == "test-job"
        assert ex.status == "running"
        assert ex.error is None
        assert ex.output is None
        assert ex.finished_at is None

    def test_success_execution(self):
        ex = CrontabExecution(
            job_name="test-job",
            status="success",
            finished_at="2025-01-01T00:00:00+00:00",
            output="Done!",
        )
        assert ex.status == "success"
        assert ex.output == "Done!"

    def test_error_execution(self):
        ex = CrontabExecution(
            job_name="test-job",
            status="error",
            error="Connection failed",
        )
        assert ex.status == "error"
        assert ex.error == "Connection failed"


# -- Registry Tests ----------------------------------------------------


class TestCrontabRegistry:
    """Tests for CrontabRegistry."""

    @pytest.fixture
    def registry(self, tmp_path):
        """Create a registry with temp storage."""
        return CrontabRegistry(
            crontabs_path=tmp_path / "crontabs.json",
            history_path=tmp_path / "history.json",
        )

    @pytest.fixture
    def sample_job(self):
        return CrontabJob(
            name="test-job",
            schedule="*/5 * * * *",
            prompt="Run a test task",
        )

    def test_empty_registry(self, registry):
        assert len(registry) == 0
        assert registry.list_jobs() == []

    def test_add_job(self, registry, sample_job):
        result = registry.add_job(sample_job)
        assert result.name == "test-job"
        assert len(registry) == 1

    def test_add_duplicate_raises(self, registry, sample_job):
        registry.add_job(sample_job)
        with pytest.raises(ValueError, match="already exists"):
            registry.add_job(sample_job)

    def test_get_job(self, registry, sample_job):
        registry.add_job(sample_job)
        job = registry.get_job("test-job")
        assert job is not None
        assert job.name == "test-job"

    def test_get_nonexistent_job(self, registry):
        assert registry.get_job("nope") is None

    def test_remove_job(self, registry, sample_job):
        registry.add_job(sample_job)
        assert registry.remove_job("test-job") is True
        assert len(registry) == 0

    def test_remove_nonexistent(self, registry):
        assert registry.remove_job("nope") is False

    def test_list_jobs(self, registry):
        registry.add_job(CrontabJob(name="b-job", schedule="* * * * *", prompt="B"))
        registry.add_job(CrontabJob(name="a-job", schedule="* * * * *", prompt="A"))
        jobs = registry.list_jobs()
        assert len(jobs) == 2
        assert jobs[0].name == "a-job"  # sorted by name

    def test_list_enabled_only(self, registry):
        registry.add_job(CrontabJob(name="enabled", schedule="* * * * *", prompt="E", enabled=True))
        registry.add_job(CrontabJob(name="disabled", schedule="* * * * *", prompt="D", enabled=False))
        enabled = registry.list_jobs(enabled_only=True)
        assert len(enabled) == 1
        assert enabled[0].name == "enabled"

    def test_enable_disable(self, registry, sample_job):
        registry.add_job(sample_job)
        registry.disable_job("test-job")
        assert registry.get_job("test-job").enabled is False
        registry.enable_job("test-job")
        assert registry.get_job("test-job").enabled is True

    def test_update_job(self, registry, sample_job):
        registry.add_job(sample_job)
        updated = registry.update_job("test-job", schedule="0 * * * *", description="Updated")
        assert updated.schedule == "0 * * * *"
        assert updated.description == "Updated"

    def test_update_nonexistent_raises(self, registry):
        with pytest.raises(KeyError, match="not found"):
            registry.update_job("nope", enabled=True)

    def test_persistence(self, tmp_path):
        """Jobs should survive registry restart."""
        path = tmp_path / "crontabs.json"
        history_path = tmp_path / "history.json"

        # Create and add
        r1 = CrontabRegistry(crontabs_path=path, history_path=history_path)
        r1.add_job(CrontabJob(name="persistent", schedule="* * * * *", prompt="test"))

        # Reload
        r2 = CrontabRegistry(crontabs_path=path, history_path=history_path)
        assert len(r2) == 1
        assert r2.get_job("persistent") is not None

    def test_execution_history(self, registry):
        execution = CrontabExecution(
            job_name="test-job",
            status="success",
        )
        registry.record_execution(execution)
        history = registry.get_history(job_name="test-job")
        assert len(history) == 1
        assert history[0].status == "success"

    def test_history_limit(self, registry):
        for i in range(15):
            registry.record_execution(
                CrontabExecution(job_name="test-job", status="success")
            )
        history = registry.get_history(job_name="test-job", limit=5)
        assert len(history) == 5

    def test_repr(self, registry, sample_job):
        registry.add_job(sample_job)
        assert "jobs=1" in repr(registry)
        assert "enabled=1" in repr(registry)


# -- Scheduler Tests ---------------------------------------------------


class TestCrontabScheduler:
    """Tests for CrontabScheduler."""

    @pytest.fixture
    def registry(self, tmp_path):
        return CrontabRegistry(
            crontabs_path=tmp_path / "crontabs.json",
            history_path=tmp_path / "history.json",
        )

    def test_init(self, registry):
        scheduler = CrontabScheduler(registry=registry)
        assert scheduler.is_running is False

    def test_load_jobs_empty(self, registry):
        scheduler = CrontabScheduler(registry=registry)
        count = scheduler.load_jobs()
        assert count == 0

    def test_load_jobs(self, registry):
        registry.add_job(CrontabJob(name="job1", schedule="*/5 * * * *", prompt="test"))
        registry.add_job(CrontabJob(name="job2", schedule="0 * * * *", prompt="test"))
        registry.add_job(CrontabJob(name="disabled", schedule="* * * * *", prompt="test", enabled=False))

        scheduler = CrontabScheduler(registry=registry)
        count = scheduler.load_jobs()
        assert count == 2  # Only enabled jobs

    @pytest.mark.asyncio
    async def test_start_stop(self, registry):
        registry.add_job(CrontabJob(name="job1", schedule="*/5 * * * *", prompt="test"))
        scheduler = CrontabScheduler(registry=registry)
        scheduler.start()
        assert scheduler.is_running is True
        scheduler.stop()
        assert scheduler.is_running is False

    @pytest.mark.asyncio
    async def test_reload(self, registry):
        scheduler = CrontabScheduler(registry=registry)
        scheduler.start()

        # Add a job after starting
        registry.add_job(CrontabJob(name="new-job", schedule="* * * * *", prompt="test"))
        count = scheduler.reload()
        assert count == 1

        scheduler.stop()

    @pytest.mark.asyncio
    async def test_get_next_run_times(self, registry):
        registry.add_job(CrontabJob(name="job1", schedule="*/5 * * * *", prompt="test"))
        scheduler = CrontabScheduler(registry=registry)
        scheduler.start()
        times = scheduler.get_next_run_times()
        assert "job1" in times
        assert times["job1"] is not None
        scheduler.stop()

    def test_repr(self, registry):
        scheduler = CrontabScheduler(registry=registry)
        assert "running=False" in repr(scheduler)
