"""Crontab Registry - manages cron job definitions and execution history.

Jobs are persisted to ~/.universal-mcp/crontabs.json.
Execution history is stored at ~/.universal-mcp/crontabs-history.json.
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from loguru import logger

from universal_mcp.crontabs.models import CrontabExecution, CrontabJob

CRONTABS_PATH = Path.home() / ".universal-mcp" / "crontabs.json"
HISTORY_PATH = Path.home() / ".universal-mcp" / "crontabs-history.json"
MAX_HISTORY_PER_JOB = 50


class CrontabRegistry:
    """Manages cron job definitions and execution history.

    Jobs are persisted to disk as JSON. The registry provides CRUD
    operations for jobs and tracks execution history.
    """

    def __init__(
        self,
        crontabs_path: Path | None = None,
        history_path: Path | None = None,
    ) -> None:
        self._crontabs_path = crontabs_path or CRONTABS_PATH
        self._history_path = history_path or HISTORY_PATH
        self._jobs: dict[str, CrontabJob] = {}
        self._history: dict[str, list[dict]] = {}
        self._load()

    # -- Job CRUD ----------------------------------------------------------

    def add_job(self, job: CrontabJob) -> CrontabJob:
        """Add or update a cron job.

        Args:
            job: CrontabJob instance to add.

        Returns:
            The added job.

        Raises:
            ValueError: If a job with the same name already exists (use update_job to modify).
        """
        if job.name in self._jobs:
            raise ValueError(
                f"Job '{job.name}' already exists. Use update_job() to modify it."
            )
        self._jobs[job.name] = job
        self._save()
        logger.info(f"Added cron job '{job.name}': {job.schedule}")
        return job

    def update_job(self, name: str, **kwargs) -> CrontabJob:
        """Update an existing job's fields.

        Args:
            name: Job name to update.
            **kwargs: Fields to update (schedule, prompt, enabled, etc.).

        Returns:
            The updated job.

        Raises:
            KeyError: If the job is not found.
        """
        job = self._jobs.get(name)
        if not job:
            raise KeyError(f"Job '{name}' not found.")

        data = job.model_dump()
        data.update(kwargs)
        data["updated_at"] = datetime.now(UTC).isoformat()
        updated = CrontabJob.model_validate(data)
        self._jobs[name] = updated
        self._save()
        logger.info(f"Updated cron job '{name}'")
        return updated

    def remove_job(self, name: str) -> bool:
        """Remove a job by name.

        Args:
            name: Job name to remove.

        Returns:
            True if removed, False if not found.
        """
        if name not in self._jobs:
            return False
        del self._jobs[name]
        self._save()
        logger.info(f"Removed cron job '{name}'")
        return True

    def get_job(self, name: str) -> CrontabJob | None:
        """Get a job by name."""
        return self._jobs.get(name)

    def list_jobs(self, enabled_only: bool = False) -> list[CrontabJob]:
        """List all jobs, optionally filtered by enabled status.

        Args:
            enabled_only: If True, only return enabled jobs.

        Returns:
            List of CrontabJob instances.
        """
        jobs = list(self._jobs.values())
        if enabled_only:
            jobs = [j for j in jobs if j.enabled]
        return sorted(jobs, key=lambda j: j.name)

    def enable_job(self, name: str) -> CrontabJob:
        """Enable a job."""
        return self.update_job(name, enabled=True)

    def disable_job(self, name: str) -> CrontabJob:
        """Disable a job."""
        return self.update_job(name, enabled=False)

    # -- Execution History -------------------------------------------------

    def record_execution(self, execution: CrontabExecution) -> None:
        """Record a job execution in history.

        Args:
            execution: CrontabExecution record to store.
        """
        history = self._history.setdefault(execution.job_name, [])
        history.append(execution.model_dump())

        # Trim to max history
        if len(history) > MAX_HISTORY_PER_JOB:
            self._history[execution.job_name] = history[-MAX_HISTORY_PER_JOB:]

        self._save_history()

    def get_history(
        self, job_name: str | None = None, limit: int = 10
    ) -> list[CrontabExecution]:
        """Get execution history, optionally filtered by job name.

        Args:
            job_name: Filter to a specific job. None returns all.
            limit: Maximum number of records to return.

        Returns:
            List of CrontabExecution records, newest first.
        """
        if job_name:
            entries = self._history.get(job_name, [])
        else:
            entries = []
            for records in self._history.values():
                entries.extend(records)

        # Sort by started_at descending
        entries.sort(key=lambda e: e.get("started_at", ""), reverse=True)

        return [
            CrontabExecution.model_validate(e) for e in entries[:limit]
        ]

    # -- Persistence -------------------------------------------------------

    def _save(self) -> None:
        """Persist jobs to disk."""
        self._crontabs_path.parent.mkdir(parents=True, exist_ok=True)
        data = {name: job.model_dump() for name, job in self._jobs.items()}
        try:
            self._crontabs_path.write_text(
                json.dumps(data, indent=2, default=str), encoding="utf-8"
            )
        except OSError as e:
            logger.error(f"Failed to save crontabs to {self._crontabs_path}: {e}")

    def _load(self) -> None:
        """Load jobs from disk."""
        self._jobs = {}
        if self._crontabs_path.exists():
            try:
                data = json.loads(self._crontabs_path.read_text(encoding="utf-8"))
                for name, entry in data.items():
                    try:
                        self._jobs[name] = CrontabJob.model_validate(entry)
                    except Exception as e:
                        logger.warning(f"Skipping invalid crontab entry '{name}': {e}")
            except (json.JSONDecodeError, OSError) as e:
                logger.error(f"Failed to load crontabs: {e}")

        self._history = {}
        if self._history_path.exists():
            try:
                self._history = json.loads(
                    self._history_path.read_text(encoding="utf-8")
                )
            except (json.JSONDecodeError, OSError) as e:
                logger.error(f"Failed to load crontab history: {e}")

    def _save_history(self) -> None:
        """Persist execution history to disk."""
        self._history_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self._history_path.write_text(
                json.dumps(self._history, indent=2, default=str), encoding="utf-8"
            )
        except OSError as e:
            logger.error(f"Failed to save crontab history: {e}")

    def __len__(self) -> int:
        return len(self._jobs)

    def __repr__(self) -> str:
        enabled = sum(1 for j in self._jobs.values() if j.enabled)
        return f"CrontabRegistry(jobs={len(self._jobs)}, enabled={enabled})"
