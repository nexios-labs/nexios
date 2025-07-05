# Scripts

This directory contains helper scripts for the Nexios project.

## setup_commitizen.py

A helper script to set up and test commitizen configuration for automated changelog generation.

### Usage

```bash
python scripts/setup_commitizen.py
```

This script will:
1. Install commitizen if not already installed
2. Test the commitizen configuration
3. Show you how to make conventional commits for testing

### Conventional Commit Format

For the automated changelog to work, commits must follow the conventional format:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Commit Types:
- `feat`: New features (minor version bump)
- `fix`: Bug fixes (patch version bump)
- `BREAKING CHANGE`: Breaking changes (major version bump)
- `chore`, `ci`, `docs`, etc.: No version bump

### Examples:
```bash
git commit -m "feat(auth): add JWT authentication support"
git commit -m "fix(api): handle null values in response"
git commit -m "feat(api): change response format

BREAKING CHANGE: API response format has changed"
``` 