"""Skills Registry - manages Claude Code skills installation and discovery.

A Claude Code skill is a directory containing a SKILL.md file with YAML
frontmatter. Skills can be installed globally (~/.claude/skills/) or
per-project (.claude/skills/).
"""

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from loguru import logger
from pydantic import BaseModel, Field, field_validator

from universal_mcp.skills.installer import install_from_github, install_from_local, validate_skill_dir

# Standard directories
GLOBAL_SKILLS_DIR = Path.home() / ".claude" / "skills"
PROJECT_SKILLS_DIR = Path(".claude") / "skills"
REGISTRY_INDEX_PATH = Path.home() / ".universal-mcp" / "skills-registry.json"

# Skill name validation: 1-64 chars, lowercase alphanumeric + hyphens
SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9\-]{0,63}$")


class SkillMetadata(BaseModel):
    """Metadata for an installed skill.

    Attributes:
        name: Skill name (1-64 chars, lowercase alphanumeric + hyphens).
        description: Human-readable description of what the skill does.
        source: Where the skill was installed from (GitHub URL, local path, etc.).
        version: Semantic version string.
        installed_at: ISO 8601 timestamp of when the skill was installed.
        scope: Whether the skill is installed globally or per-project.
        path: Full filesystem path to the skill directory.
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="Skill name: lowercase alphanumeric and hyphens only (1-64 chars).",
    )
    description: str = Field(
        ...,
        description="Human-readable description of what the skill does.",
    )
    source: str | None = Field(
        default=None,
        description="Where the skill was installed from (GitHub URL, local path, etc.).",
    )
    version: str = Field(
        default="0.1.0",
        description="Semantic version string.",
    )
    installed_at: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="ISO 8601 timestamp of installation.",
    )
    scope: Literal["global", "project"] = Field(
        default="global",
        description="Installation scope: 'global' (~/.claude/skills/) or 'project' (.claude/skills/).",
    )
    path: Path = Field(
        ...,
        description="Full filesystem path to the skill directory.",
    )

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate skill name matches the required pattern."""
        v = v.strip().lower()
        if not SKILL_NAME_PATTERN.match(v):
            raise ValueError(
                f"Invalid skill name '{v}'. Must be 1-64 chars, "
                "lowercase alphanumeric and hyphens only, starting with alphanumeric."
            )
        return v

    model_config = {"json_encoders": {Path: str}}


class SkillsRegistry:
    """Manages installation, discovery, and removal of Claude Code skills.

    Skills are stored in two locations:
    - Global: ~/.claude/skills/ (shared across all projects)
    - Project: .claude/skills/ (relative to current working directory)

    The registry index is persisted at ~/.universal-mcp/skills-registry.json
    to track installed skills and their metadata.
    """

    def __init__(self):
        """Initialize the registry and load the existing index from disk."""
        self._skills: dict[str, SkillMetadata] = {}
        self._registry_path = REGISTRY_INDEX_PATH
        self._load_registry()

    def list_skills(self, scope: str | None = None) -> list[SkillMetadata]:
        """List installed skills, optionally filtered by scope.

        Args:
            scope: Filter by 'global' or 'project'. None returns all.

        Returns:
            List of SkillMetadata for matching skills.
        """
        skills = list(self._skills.values())
        if scope:
            skills = [s for s in skills if s.scope == scope]
        return sorted(skills, key=lambda s: s.name)

    def search_skills(self, query: str) -> list[SkillMetadata]:
        """Search installed skills by name or description (case-insensitive substring).

        Args:
            query: Search string to match against skill name and description.

        Returns:
            List of matching SkillMetadata.
        """
        q = query.lower()
        results = []
        for skill in self._skills.values():
            if q in skill.name.lower() or q in skill.description.lower():
                results.append(skill)
        return sorted(results, key=lambda s: s.name)

    def get_skill(self, name: str) -> SkillMetadata | None:
        """Get metadata for a specific skill by name.

        Args:
            name: The skill name to look up.

        Returns:
            SkillMetadata if found, None otherwise.
        """
        return self._skills.get(name.lower())

    def install_skill(self, source: str, scope: Literal["global", "project"] = "global") -> SkillMetadata:
        """Install a skill from a local path or GitHub URL.

        Args:
            source: Either a local directory path or a GitHub URL.
                Local: /path/to/skill-dir (must contain SKILL.md)
                GitHub: https://github.com/owner/repo
                        https://github.com/owner/repo/tree/branch/path/to/skill
            scope: Installation scope - 'global' or 'project'.

        Returns:
            SkillMetadata for the installed skill.

        Raises:
            ValueError: If the source is invalid or the skill is malformed.
            FileNotFoundError: If a local source path does not exist.
        """
        target_dir = self._get_skills_dir(scope)

        # Determine source type and install
        source_path = Path(source).expanduser()
        if source_path.exists() and source_path.is_dir():
            installed_path = install_from_local(source_path, target_dir)
        elif source.startswith("https://github.com/") or source.startswith("http://github.com/"):
            installed_path = install_from_github(source, target_dir)
        else:
            # Try as a local path even if it doesn't exist yet (will raise a clear error)
            installed_path = install_from_local(source_path, target_dir)

        # Read the frontmatter from the installed skill
        frontmatter = validate_skill_dir(installed_path)

        metadata = SkillMetadata(
            name=frontmatter["name"],
            description=frontmatter.get("description", "No description provided."),
            source=source,
            version=frontmatter.get("version", "0.1.0"),
            scope=scope,
            path=installed_path,
        )

        self._skills[metadata.name] = metadata
        self._save_registry()

        logger.info(f"Skill '{metadata.name}' installed to {installed_path} (scope={scope})")
        return metadata

    def remove_skill(self, name: str) -> bool:
        """Remove a skill and delete its files from disk.

        Args:
            name: The name of the skill to remove.

        Returns:
            True if the skill was found and removed, False if not found.
        """
        name = name.lower()
        skill = self._skills.get(name)
        if not skill:
            logger.warning(f"Skill '{name}' not found in registry")
            return False

        # Remove files from disk
        import shutil

        skill_path = Path(skill.path)
        if skill_path.exists() and skill_path.is_dir():
            shutil.rmtree(skill_path)
            logger.info(f"Removed skill directory: {skill_path}")
        else:
            logger.warning(f"Skill directory not found on disk: {skill_path}")

        del self._skills[name]
        self._save_registry()

        logger.info(f"Skill '{name}' removed from registry")
        return True

    def scan_skills(self) -> None:
        """Scan global and project skill directories and update registry.

        Discovers skills that were manually added to the skill directories
        and adds them to the registry. Also removes registry entries for
        skills whose directories no longer exist.
        """
        discovered: dict[str, SkillMetadata] = {}

        # Scan global skills
        self._scan_directory(GLOBAL_SKILLS_DIR, "global", discovered)

        # Scan project skills (relative to cwd)
        project_dir = Path.cwd() / PROJECT_SKILLS_DIR
        self._scan_directory(project_dir, "project", discovered)

        # Merge: keep existing metadata for known skills, add new ones
        updated: dict[str, SkillMetadata] = {}
        for name, metadata in discovered.items():
            if name in self._skills:
                # Keep existing metadata but update path in case it moved
                existing = self._skills[name]
                existing.path = metadata.path
                existing.scope = metadata.scope
                updated[name] = existing
            else:
                updated[name] = metadata
                logger.info(f"Discovered new skill: '{name}' at {metadata.path}")

        # Log removed skills
        for name in self._skills:
            if name not in updated:
                logger.info(f"Skill '{name}' no longer found on disk, removing from registry")

        self._skills = updated
        self._save_registry()

    def _scan_directory(self, skills_dir: Path, scope: Literal["global", "project"], out: dict[str, SkillMetadata]) -> None:
        """Scan a single skills directory for valid skill subdirectories.

        Args:
            skills_dir: Directory to scan (e.g., ~/.claude/skills/).
            scope: The scope label ('global' or 'project').
            out: Dictionary to populate with discovered skills.
        """
        if not skills_dir.exists() or not skills_dir.is_dir():
            return

        for child in skills_dir.iterdir():
            if not child.is_dir():
                continue
            try:
                frontmatter = validate_skill_dir(child)
                name = frontmatter["name"].strip().lower()
                out[name] = SkillMetadata(
                    name=name,
                    description=frontmatter.get("description", "No description provided."),
                    source=None,
                    version=frontmatter.get("version", "0.1.0"),
                    scope=scope,
                    path=child.resolve(),
                )
            except (FileNotFoundError, ValueError) as e:
                logger.debug(f"Skipping {child}: {e}")

    def _get_skills_dir(self, scope: Literal["global", "project"]) -> Path:
        """Get the target directory for the given scope.

        Args:
            scope: 'global' or 'project'.

        Returns:
            The skills directory path.
        """
        if scope == "project":
            return Path.cwd() / PROJECT_SKILLS_DIR
        return GLOBAL_SKILLS_DIR

    def _save_registry(self) -> None:
        """Persist the registry index to disk as JSON."""
        self._registry_path.parent.mkdir(parents=True, exist_ok=True)

        data = {name: skill.model_dump(mode="json") for name, skill in self._skills.items()}
        # Convert Path objects to strings for JSON serialization
        for entry in data.values():
            if isinstance(entry.get("path"), Path):
                entry["path"] = str(entry["path"])

        try:
            self._registry_path.write_text(
                json.dumps(data, indent=2, default=str),
                encoding="utf-8",
            )
        except OSError as e:
            logger.error(f"Failed to save skills registry to {self._registry_path}: {e}")

    def _load_registry(self) -> None:
        """Load the registry index from disk."""
        if not self._registry_path.exists():
            self._skills = {}
            return

        try:
            content = self._registry_path.read_text(encoding="utf-8")
            data = json.loads(content)
            self._skills = {}
            for name, entry in data.items():
                try:
                    # Ensure path is a Path object
                    if isinstance(entry.get("path"), str):
                        entry["path"] = Path(entry["path"])
                    self._skills[name] = SkillMetadata.model_validate(entry)
                except Exception as e:
                    logger.warning(f"Skipping invalid registry entry '{name}': {e}")
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Failed to load skills registry from {self._registry_path}: {e}")
            self._skills = {}

    def _parse_skill_md(self, skill_dir: Path) -> dict:
        """Parse SKILL.md YAML frontmatter from a skill directory.

        This is a convenience wrapper around validate_skill_dir for
        external callers who need the raw frontmatter data.

        Args:
            skill_dir: Path to the skill directory.

        Returns:
            Parsed YAML frontmatter as a dict.
        """
        return validate_skill_dir(skill_dir)

    def __len__(self) -> int:
        return len(self._skills)

    def __repr__(self) -> str:
        return f"SkillsRegistry(skills={len(self._skills)})"
