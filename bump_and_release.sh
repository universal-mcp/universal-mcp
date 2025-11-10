#!/bin/bash

set -e
set -x

# Ensure dependencies are installed
echo "Syncing dependencies..."
uv sync --frozen --all-extras --dev

# Run tests with pytest
echo "Running tests with pytest..."
uv run pytest

echo "Tests passed!"

# Get the current branch name
BRANCH=$(git branch --show-current)

# Read the current version from pyproject.toml
CURRENT_VERSION=$(grep -E '^version = "[0-9]+\.[0-9]+\.[0-9]+.*"' pyproject.toml | cut -d'"' -f2)

# Split version into major, minor, patch
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"

# Remove any rc suffix from PATCH if it exists
PATCH_NUM=$(echo $PATCH | sed 's/-rc[0-9]*//')

if [ "$BRANCH" = "master" ]; then
    # On main branch - bump patch version
    if [[ $PATCH == *"-rc"* ]]; then
        NEW_VERSION="$MAJOR.$MINOR.$PATCH_NUM"
    else
        # Increase patch number by 1
        PATCH_NUM=$((PATCH_NUM + 1))
        NEW_VERSION="$MAJOR.$MINOR.$PATCH_NUM"
    fi
else
    # On dev branch - bump rc version
    if [[ $PATCH == *"-rc"* ]]; then
        # If already has rc, increment rc number
        RC_NUM=$(echo $PATCH | grep -o 'rc[0-9]*' | sed 's/rc//')
        NEW_VERSION="$MAJOR.$MINOR.$PATCH_NUM-rc$((RC_NUM + 1))"
    else
        echo "No rc suffix found, adding rc1"
        # Increase patch number by 1
        PATCH_NUM=$((PATCH_NUM + 1))
        # Add rc1
        NEW_VERSION="$MAJOR.$MINOR.$PATCH_NUM-rc1"
    fi
fi

# Update version in pyproject.toml
sed -i '' "s/^version = ".*"/version = \"$NEW_VERSION\"/" pyproject.toml

echo "Version bumped from $CURRENT_VERSION to $NEW_VERSION"

# Stage the changed file
git add pyproject.toml uv.lock

# Commit the change
git commit -m "bump: version $CURRENT_VERSION → $NEW_VERSION"

# Create and push tag if on main
if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "develop" ] || [ "$BRANCH" = "master" ] || [ "$BRANCH" = "dev" ]; then
    git tag -a "v$NEW_VERSION" -m "Release version $NEW_VERSION"
    # Push both the branch and tag in one command
    git push origin $BRANCH "v$NEW_VERSION"
else
    # Push only the branch if not on main/develop
    git push origin $BRANCH
fi


# Either release is passed as arg or not
if [ "$1" = "release" ]; then
    # Execute release steps
    echo "Releasing version $NEW_VERSION..."
    rm -rf dist
    rm -rf build
    rm -rf *.egg-info
    rm -rf .pytest_cache
    rm -rf .ruff_cache
    rm -rf .mypy_cache
    rm -rf .venv
    rm -rf .cache
    rm -rf .DS_Store
    rm -rf .idea
    rm -rf .vscode

    uv sync && uv build && uv publish
    echo "Release complete!"
else
    echo "Skipping release steps"
fi
