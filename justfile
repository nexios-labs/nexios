# Justfile for Nexios project
# Install just: https://github.com/casey/just#installation
# Install commitizen: pip install commitizen

# Default target when running just
set shell := ["powershell", "-c"]

default:
    @just --list

# Bump version and generate changelog using commitizen
bump:
    #!/usr/bin/env bash
    set -e
    
    # Check if commitizen is installed
    if ! command -v cz &> /dev/null; then
        echo "Error: commitizen is not installed. Install it with: pip install commitizen"
        exit 1
    fi
    
    # Bump version and update changelog
    cz bump --changelog --increment patch --yes
    
    # Show the new version
    NEW_VERSION=$(cz version --project)
    echo "✅ Bumped to version: $NEW_VERSION"
    echo "📝 Changelog has been updated"

# Push the new version and tag to remote
release:
    #!/usr/bin/env bash
    set -e
    
    # Get current branch name
    CURRENT_BRANCH=$(git branch --show-current)
    
    # Get the latest tag
    LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
    
    echo "🚀 Preparing release..."
    echo "• Current branch: $CURRENT_BRANCH"
    echo "• Latest tag: $LATEST_TAG"
    
    # First push the changelog updates
    git push origin $CURRENT_BRANCH
    
    # Get the new tag (should be created by cz bump)
    NEW_TAG=$(git describe --tags --abbrev=0 2>/dev/null)
    
    if [ "$NEW_TAG" != "$LATEST_TAG" ]; then
        echo "• Pushing new tag: $NEW_TAG"
        git push origin $NEW_TAG
    else
        echo "⚠️  No new tag to push. Did you run 'just bump' first?"
        exit 1
    fi
    
    echo "✅ Release completed successfully!"

# Run both bump and release in sequence
full-release:
    just bump
    just release

# Show current version
version:
    cz version --project
