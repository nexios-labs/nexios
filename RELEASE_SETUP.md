# Automated Release Setup

This project uses GitHub Actions with Commitizen for automated releases. The workflow is split into two parts:

## Workflows

### 1. Merge to Main (`merge-to-main.yml`)
- Triggers when code is pushed to the `main` branch
- Uses Commitizen to analyze commit messages and determine version bumps
- Automatically updates `CHANGELOG.md` and version in `pyproject.toml`
- Creates git tags for new versions

### 2. On Tag Creation (`release.yml`)
- Triggers when a version tag is pushed (e.g., `v1.0.0`)
- Builds and publishes the package to PyPI using `uv`
- Creates GitHub releases with changelog notes

## Required Secrets

You need to set up the following secrets in your GitHub repository:

### 1. PERSONAL_ACCESS_TOKEN
- Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
- Generate a new token with the following scopes:
  - `repo` (full control of private repositories)
  - `workflow` (update GitHub Action workflows)
- Add this token as a repository secret named `PERSONAL_ACCESS_TOKEN`

### 2. PYPI_TOKEN
- Go to PyPI → Account settings → API tokens
- Create a new token with scope "Entire account (all projects)"
- Add this token as a repository secret named `PYPI_TOKEN`

## Commit Message Format

The workflow uses conventional commits format:

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
```
feat(auth): add JWT authentication support
fix(api): handle null values in response
feat(api): change response format

BREAKING CHANGE: API response format has changed
```

## How It Works

1. **Development**: Make commits using conventional commit format
2. **Merge to Main**: When code is merged to main, Commitizen analyzes commits and:
   - Determines if a version bump is needed
   - Updates `pyproject.toml` version
   - Updates `CHANGELOG.md`
   - Creates a git tag
3. **Release**: When a tag is pushed, the package is:
   - Built using `uv build`
   - Published to PyPI using `uv publish`
   - GitHub release created with changelog notes

## Manual Release

If you need to create a release manually:

1. Update version in `pyproject.toml`
2. Create and push a tag:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

## Troubleshooting

- **Permission Errors**: Ensure `PERSONAL_ACCESS_TOKEN` has correct scopes
- **PyPI Publishing Errors**: Check `PYPI_TOKEN` is valid and has correct permissions
- **Commitizen Issues**: Verify commit messages follow conventional format 