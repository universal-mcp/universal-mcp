"""Crontab Scheduler - executes cron jobs using APScheduler.

Uses APScheduler's AsyncIOScheduler with CronTrigger to schedule
jobs. Each job executes a Claude agent query with the configured prompt.
"""

import asyncio
from datetime import UTC, datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger

from universal_mcp.crontabs.models import CrontabExecution, CrontabJob
from universal_mcp.crontabs.registry import CrontabRegistry


class CrontabScheduler:
    """Executes cron jobs on schedule using APScheduler.

    The scheduler loads enabled jobs from the registry, creates
    APScheduler jobs for each, and runs them on schedule. Each
    execution invokes a Claude agent with the job's prompt.
    """

    def __init__(self, registry: CrontabRegistry | None = None) -> None:
        self._registry = registry if registry is not None else CrontabRegistry()
        self._scheduler = AsyncIOScheduler(timezone="UTC")
        self._running = False

    def load_jobs(self) -> int:
        """Load enabled jobs from the registry into the scheduler.

        Returns:
            Number of jobs loaded.
        """
        # Remove any existing jobs first
        self._scheduler.remove_all_jobs()

        jobs = self._registry.list_jobs(enabled_only=True)
        for job in jobs:
            self._add_job_to_scheduler(job)

        logger.info(f"Loaded {len(jobs)} cron jobs into scheduler")
        return len(jobs)

    def _add_job_to_scheduler(self, job: CrontabJob) -> None:
        """Add a single job to the APScheduler."""
        try:
            trigger = CronTrigger.from_crontab(job.schedule, timezone=job.timezone)
            self._scheduler.add_job(
                self._execute_job,
                trigger=trigger,
                id=job.name,
                name=job.name,
                args=[job],
                replace_existing=True,
                max_instances=job.max_instances,
            )
            logger.debug(f"Scheduled job '{job.name}': {job.schedule}")
        except Exception as e:
            logger.error(f"Failed to schedule job '{job.name}': {e}")

    async def _execute_job(self, job: CrontabJob) -> None:
        """Execute a single cron job by running the agent."""
        execution = CrontabExecution(
            job_name=job.name,
            started_at=datetime.now(UTC).isoformat(),
            status="running",
        )

        logger.info(f"Executing cron job '{job.name}': {job.prompt[:80]}...")

        try:
            from universal_mcp.agent import run_agent_query

            await run_agent_query(prompt=job.prompt, model=job.model)

            execution.status = "success"
            execution.finished_at = datetime.now(UTC).isoformat()
            logger.info(f"Cron job '{job.name}' completed successfully")

        except Exception as e:
            execution.status = "error"
            execution.error = str(e)
            execution.finished_at = datetime.now(UTC).isoformat()
            logger.error(f"Cron job '{job.name}' failed: {e}")

        self._registry.record_execution(execution)

    def start(self) -> None:
        """Start the scheduler (non-blocking)."""
        if self._running:
            logger.warning("Scheduler is already running")
            return

        self.load_jobs()
        self._scheduler.start()
        self._running = True
        logger.info("Crontab scheduler started")

    def stop(self) -> None:
        """Stop the scheduler."""
        if self._running:
            self._scheduler.shutdown(wait=False)
            self._running = False
            logger.info("Crontab scheduler stopped")

    async def run(self) -> None:
        """Start the scheduler and run forever.

        This is the main entry point for the `unsw cron run` command.
        Blocks until interrupted.
        """
        self.start()
        try:
            # Run forever until interrupted
            while True:
                await asyncio.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            logger.info("Scheduler interrupted, shutting down...")
        finally:
            self.stop()

    def reload(self) -> int:
        """Reload jobs from the registry.

        Useful after adding/removing/updating jobs while the scheduler
        is running.

        Returns:
            Number of jobs loaded.
        """
        return self.load_jobs()

    @property
    def is_running(self) -> bool:
        """Whether the scheduler is currently running."""
        return self._running

    def get_next_run_times(self) -> dict[str, str | None]:
        """Get the next scheduled run time for each job.

        Returns:
            Dict mapping job name to next run time (ISO format) or None.
        """
        result = {}
        for scheduled_job in self._scheduler.get_jobs():
            next_run = scheduled_job.next_run_time
            result[scheduled_job.id] = next_run.isoformat() if next_run else None
        return result

    def __repr__(self) -> str:
        jobs = len(self._scheduler.get_jobs()) if self._running else 0
        return f"CrontabScheduler(running={self._running}, jobs={jobs})"
