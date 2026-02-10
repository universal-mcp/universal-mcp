"""Crontab models - Pydantic models for scheduled AI tasks."""

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class CrontabJob(BaseModel):
    """A scheduled AI task that runs on a cron schedule.

    Each job defines a prompt to execute via the Claude agent on a
    recurring schedule defined by a cron expression.
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Unique name for this cron job.",
    )
    schedule: str = Field(
        ...,
        description="Cron expression (5 fields: minute hour day month weekday). Example: '*/5 * * * *' for every 5 minutes.",
    )
    prompt: str = Field(
        ...,
        min_length=1,
        description="The prompt to execute via the Claude agent.",
    )
    model: str | None = Field(
        default=None,
        description="Optional model override (e.g., 'sonnet', 'opus'). Uses agent default if not set.",
    )
    enabled: bool = Field(
        default=True,
        description="Whether this job is active. Disabled jobs are not scheduled.",
    )
    description: str = Field(
        default="",
        description="Optional human-readable description of what this job does.",
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="ISO 8601 timestamp of when the job was created.",
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="ISO 8601 timestamp of last update.",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Optional tags for categorization.",
    )
    max_instances: int = Field(
        default=1,
        ge=1,
        le=5,
        description="Maximum concurrent instances of this job.",
    )
    timezone: str = Field(
        default="UTC",
        description="Timezone for the cron schedule.",
    )

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Normalize job name."""
        return v.strip()

    @field_validator("schedule", mode="before")
    @classmethod
    def validate_schedule(cls, v: str) -> str:
        """Validate cron expression using APScheduler's CronTrigger."""
        from apscheduler.triggers.cron import CronTrigger

        v = v.strip()
        try:
            CronTrigger.from_crontab(v)
        except (ValueError, KeyError) as e:
            raise ValueError(
                f"Invalid cron expression '{v}': {e}. "
                "Must have 5 fields: minute hour day month weekday. Example: '*/5 * * * *'"
            ) from e
        return v

    model_config = {"json_schema_extra": {"examples": [{"name": "daily-report", "schedule": "0 9 * * *", "prompt": "Generate a daily summary report of project status"}]}}


class CrontabExecution(BaseModel):
    """Record of a single job execution."""

    job_name: str = Field(
        ..., description="Name of the job that was executed."
    )
    started_at: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="ISO 8601 timestamp of execution start.",
    )
    finished_at: str | None = Field(
        default=None,
        description="ISO 8601 timestamp of execution end. None if still running.",
    )
    status: Literal["running", "success", "error"] = Field(
        default="running",
        description="Execution status.",
    )
    error: str | None = Field(
        default=None,
        description="Error message if execution failed.",
    )
    output: str | None = Field(
        default=None,
        description="Captured output from the execution.",
    )
