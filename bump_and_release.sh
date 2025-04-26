#!/bin/bash

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
    NEW_VERSION="$MAJOR.$MINOR.$PATCH_NUM"
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
sed -i '' "s/^version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml

echo "Version bumped from $CURRENT_VERSION to $NEW_VERSION"

# Stage the changed file
git add pyproject.toml

# Commit the change
git commit -m "bump: version $CURRENT_VERSION → $NEW_VERSION"

# Create and push tag if on main
if [ "$BRANCH" = "main" ]; then
    git tag -a "v$NEW_VERSION" -m "Release version $NEW_VERSION"
    git push origin "v$NEW_VERSION"
fi

# Push the changes
git push origin $BRANCH

# Ask user if they want to release
read -p "Do you want to build and publish the package? (y/N) " RELEASE_CONFIRM

if [[ $RELEASE_CONFIRM =~ ^[Yy]$ ]]; then
    # Build and publish
    rm -rf dist && uv build && uv publish
else
    echo "Skipping release. Version bump committed and pushed."
fi