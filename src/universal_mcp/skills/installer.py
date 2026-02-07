"""Skill installation from various sources.

Handles copying local skill directories and cloning/downloading skills
from GitHub repositories. All operations are synchronous since this is
CLI-facing code.
"""

import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

import httpx
from loguru import logger


def validate_skill_dir(path: Path) -> dict:
    """Validate that a directory is a valid skill (has SKILL.md with valid frontmatter).

    Args:
        path: Path to the directory to validate.

    Returns:
        Parsed YAML frontmatter as a dict with at least 'name' and 'description'.

    Raises:
        FileNotFoundError: If SKILL.md does not exist in the directory.
        ValueError: If the frontmatter is missing, malformed, or lacks required fields.
    """
    skill_md = path / "SKILL.md"
    if not skill_md.exists():
        raise FileNotFoundError(f"No SKILL.md found in {path}")

    frontmatter = _parse_skill_md_frontmatter(skill_md)
    if not frontmatter:
        raise ValueError(f"SKILL.md in {path} has no YAML frontmatter (expected --- delimited block at top)")

    if "name" not in frontmatter:
        raise ValueError(f"SKILL.md frontmatter in {path} is missing required 'name' field")
    if "description" not in frontmatter:
        raise ValueError(f"SKILL.md frontmatter in {path} is missing required 'description' field")

    return frontmatter


def install_from_local(source_path: Path, target_dir: Path) -> Path:
    """Copy a local skill directory to the target skills directory.

    Args:
        source_path: Path to the source skill directory.
        target_dir: Parent directory where the skill should be installed
                    (e.g., ~/.claude/skills/).

    Returns:
        Path to the installed skill directory.

    Raises:
        FileNotFoundError: If source_path does not exist.
        ValueError: If source_path is not a valid skill directory.
    """
    source_path = source_path.resolve()
    if not source_path.exists():
        raise FileNotFoundError(f"Source path does not exist: {source_path}")
    if not source_path.is_dir():
        raise ValueError(f"Source path is not a directory: {source_path}")

    # Validate the skill directory before copying
    frontmatter = validate_skill_dir(source_path)
    skill_name = frontmatter["name"]

    target_dir.mkdir(parents=True, exist_ok=True)
    dest = target_dir / skill_name

    if dest.exists():
        logger.info(f"Removing existing skill at {dest}")
        shutil.rmtree(dest)

    shutil.copytree(source_path, dest)
    logger.info(f"Installed skill '{skill_name}' from local path {source_path} to {dest}")
    return dest


def install_from_github(url: str, target_dir: Path) -> Path:
    """Clone or download a skill from a GitHub repository.

    Supports two URL formats:
    - Full repo: https://github.com/owner/repo
    - Subpath:   https://github.com/owner/repo/tree/branch/path/to/skill

    Uses git clone if git is available, otherwise falls back to downloading
    the repository zip via the GitHub API.

    Args:
        url: GitHub URL pointing to a repo or a specific directory within a repo.
        target_dir: Parent directory where the skill should be installed.

    Returns:
        Path to the installed skill directory.

    Raises:
        ValueError: If the URL is not a valid GitHub URL or the skill is invalid.
    """
    parsed = _parse_github_url(url)
    if parsed is None:
        raise ValueError(f"Could not parse GitHub URL: {url}")

    owner, repo, branch, subpath = parsed

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        if _git_available():
            _clone_repo(owner, repo, branch, tmp_path / repo)
            source = tmp_path / repo
        else:
            _download_repo_zip(owner, repo, branch, tmp_path)
            # GitHub zips extract to owner-repo-branch/ or similar
            extracted_dirs = [d for d in tmp_path.iterdir() if d.is_dir()]
            if not extracted_dirs:
                raise ValueError(f"Failed to extract GitHub repository from {url}")
            source = extracted_dirs[0]

        # If a subpath was specified, navigate into it
        if subpath:
            source = source / subpath
            if not source.exists():
                raise ValueError(f"Subpath '{subpath}' not found in repository {owner}/{repo}")

        # Validate and install
        frontmatter = validate_skill_dir(source)
        skill_name = frontmatter["name"]

        target_dir.mkdir(parents=True, exist_ok=True)
        dest = target_dir / skill_name

        if dest.exists():
            logger.info(f"Removing existing skill at {dest}")
            shutil.rmtree(dest)

        shutil.copytree(source, dest)
        logger.info(f"Installed skill '{skill_name}' from GitHub {owner}/{repo} to {dest}")
        return dest


def _parse_github_url(url: str) -> tuple[str, str, str | None, str | None] | None:
    """Parse a GitHub URL into (owner, repo, branch, subpath).

    Supported formats:
    - https://github.com/owner/repo
    - https://github.com/owner/repo.git
    - https://github.com/owner/repo/tree/branch
    - https://github.com/owner/repo/tree/branch/path/to/skill

    Returns:
        Tuple of (owner, repo, branch_or_none, subpath_or_none), or None if parsing fails.
    """
    # Normalize
    url = url.rstrip("/")

    # Match: https://github.com/owner/repo(/tree/branch(/subpath)?)?
    pattern = r"^https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?(?:/tree/([^/]+)(?:/(.+))?)?$"
    match = re.match(pattern, url)
    if not match:
        return None

    owner = match.group(1)
    repo = match.group(2)
    branch = match.group(3)  # may be None
    subpath = match.group(4)  # may be None

    return owner, repo, branch, subpath


def _git_available() -> bool:
    """Check if git is available on the system."""
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def _clone_repo(owner: str, repo: str, branch: str | None, dest: Path) -> None:
    """Clone a GitHub repository using git.

    Args:
        owner: Repository owner.
        repo: Repository name.
        branch: Branch to clone (None for default branch).
        dest: Destination directory.
    """
    clone_url = f"https://github.com/{owner}/{repo}.git"
    cmd = ["git", "clone", "--depth", "1"]
    if branch:
        cmd.extend(["--branch", branch])
    cmd.extend([clone_url, str(dest)])

    logger.info(f"Cloning {clone_url} (branch={branch or 'default'}) to {dest}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise ValueError(f"git clone failed: {result.stderr.strip()}")


def _download_repo_zip(owner: str, repo: str, branch: str | None, dest: Path) -> None:
    """Download and extract a GitHub repository zip archive.

    Args:
        owner: Repository owner.
        repo: Repository name.
        branch: Branch to download (None defaults to 'main').
        dest: Directory to extract into.
    """
    branch = branch or "main"
    zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"

    logger.info(f"Downloading {zip_url}")
    response = httpx.get(zip_url, follow_redirects=True, timeout=60.0)
    if response.status_code != 200:
        raise ValueError(f"Failed to download repository zip from {zip_url}: HTTP {response.status_code}")

    zip_path = dest / f"{repo}.zip"
    zip_path.write_bytes(response.content)

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(dest)

    zip_path.unlink()
    logger.info(f"Extracted repository to {dest}")


def _parse_skill_md_frontmatter(skill_md: Path) -> dict | None:
    """Parse YAML frontmatter from a SKILL.md file.

    Frontmatter is expected between --- markers at the top of the file:

        ---
        name: my-skill
        description: Does something useful
        version: 1.0.0
        ---

    Args:
        skill_md: Path to the SKILL.md file.

    Returns:
        Parsed YAML dict, or None if no frontmatter found.
    """
    import yaml

    content = skill_md.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return None

    # Find the closing ---
    end_idx = content.index("---", 3) if "---" in content[3:] else -1
    if end_idx == -1:
        return None

    # The frontmatter content is between the two --- markers
    # content[3:] skips the first ---, then we find the next ---
    remaining = content[3:]
    closing = remaining.find("---")
    if closing == -1:
        return None

    frontmatter_str = remaining[:closing].strip()
    if not frontmatter_str:
        return None

    try:
        return yaml.safe_load(frontmatter_str)
    except yaml.YAMLError as e:
        logger.warning(f"Failed to parse YAML frontmatter in {skill_md}: {e}")
        return None
