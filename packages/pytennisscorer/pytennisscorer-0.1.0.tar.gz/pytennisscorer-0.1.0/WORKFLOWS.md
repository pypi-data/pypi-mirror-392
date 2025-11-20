# GitHub Actions Workflows Documentation

This document describes the GitHub Actions workflows configured for pytennisscorer.

## Overview

The project uses three main workflows:
- **CI** - Continuous Integration for testing and code quality
- **Release** - Automated PyPI publishing and tagging
- **Documentation** - Sphinx docs building and GitHub Pages deployment

## CI Workflow (`.github/workflows/ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches
- Ignores changes to documentation-only files

**Jobs:**

### 1. Lint & Format Check
- Runs `ruff` for code formatting and linting
- Ensures code style consistency
- Uses Python 3.11

### 2. Type Check
- Runs `mypy` in strict mode
- Verifies type hints are correct
- Uses Python 3.11

### 3. Test Matrix
- Tests across Python versions: 3.9, 3.10, 3.11, 3.12
- Tests on multiple OS: Ubuntu, Windows, macOS
- Runs full test suite with coverage
- Uploads coverage to Codecov
- Fails if coverage drops below 80%

### 4. Notebook Testing
- Validates Jupyter notebook examples
- Ensures documentation notebooks execute without errors

### 5. Build Verification
- Builds wheel and source distributions
- Validates package metadata with `twine check`

## Release Workflow (`.github/workflows/release.yml`)

**Triggers:**
- GitHub Release publication
- Manual workflow dispatch (with TestPyPI option)

**Jobs:**

### 1. Build Distribution
- Creates wheel and source distributions
- Validates package integrity

### 2. Test Installation
- Tests package installation on multiple platforms
- Verifies basic functionality after installation
- Matrix: Ubuntu/Windows/macOS × Python 3.9/3.12

### 3. Publish to TestPyPI (Optional)
- Publishes to TestPyPI for testing
- Only runs on manual trigger with `test_pypi: true`
- Uses trusted publishing (OIDC)

### 4. Publish to PyPI
- Publishes to official PyPI
- Runs on release creation or manual trigger
- Uses trusted publishing (OIDC)

### 5. Create Git Tag
- Creates version tag after successful publish
- Format: `v{version}` (e.g., `v0.1.0`)

### 6. Update Changelog
- Automatically creates PR with changelog updates
- Extracts release notes from GitHub release

## Documentation Workflow (`.github/workflows/docs.yml`)

**Triggers:**
- Push to `main` (deploys to GitHub Pages)
- Pull requests (creates preview)
- Manual workflow dispatch
- Changes to docs or source files

**Jobs:**

### 1. Build Documentation
- Installs Sphinx and dependencies
- Builds HTML documentation
- Fails on any warnings

### 2. Test Documentation
- Lints documentation with `doc8`
- Checks for broken links
- Validates documentation structure

### 3. Deploy to GitHub Pages
- Only runs on `main` branch
- Deploys to https://your-username.github.io/pytennisscorer/
- Requires GitHub Pages to be enabled in repository settings

### 4. Preview for Pull Requests
- Creates downloadable preview artifact
- Comments on PR with download link
- Artifacts retained for 3 days

## Setup Instructions

### 1. PyPI Publishing Setup

To enable automated PyPI publishing:

1. Create PyPI account at https://pypi.org
2. Go to Account Settings → Publishing
3. Add a new pending publisher:
   - PyPI Project Name: `pytennisscorer`
   - Owner: Your GitHub username
   - Repository: `pytennisscorer`
   - Workflow name: `release.yml`
   - Environment: `pypi`

4. For TestPyPI, repeat at https://test.pypi.org with environment `testpypi`

### 2. GitHub Pages Setup

To enable documentation hosting:

1. Go to repository Settings → Pages
2. Source: GitHub Actions
3. After first deployment, docs will be available at:
   https://[username].github.io/pytennisscorer/

### 3. Codecov Setup (Optional)

For coverage reporting:

1. Sign up at https://codecov.io
2. Add your repository
3. Coverage reports will automatically appear on PRs

## Usage Examples

### Creating a Release

1. Update version in `pyproject.toml`
2. Commit and push changes
3. Create a new release on GitHub:
   ```bash
   gh release create v0.1.0 \
     --title "v0.1.0" \
     --notes "Release notes here"
   ```
4. Workflows will automatically:
   - Run all tests
   - Build and publish to PyPI
   - Create git tag
   - Update changelog
   - Deploy documentation

### Testing PyPI Publishing

To test publishing without creating a release:

1. Go to Actions tab
2. Select "Release" workflow
3. Click "Run workflow"
4. Select `test_pypi: true`
5. Package will be published to TestPyPI

### Building Documentation Locally

```bash
# Install documentation dependencies
uv pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints
uv pip install sphinx-copybutton myst-parser

# Build documentation
cd docs
make html

# View documentation
open _build/html/index.html  # macOS
xdg-open _build/html/index.html  # Linux
```

## Workflow Configuration

### Using `uv` Package Manager

All workflows use `uv` for fast, reliable Python package management:
- Caches dependencies between runs
- Ensures consistent dependency resolution
- Faster than traditional pip

### Matrix Testing Strategy

CI runs a smart matrix to balance coverage and speed:
- Full matrix: 3 OS × 4 Python versions = 12 jobs
- Optimized: Skip older Python on Windows/macOS
- Result: 7 jobs with good coverage

### Security

- Uses OIDC trusted publishing (no API tokens needed)
- Workflows have minimal required permissions
- Separate environments for PyPI and TestPyPI

## Troubleshooting

### CI Failures

1. **Linting errors**: Run `make format` locally
2. **Type errors**: Run `make type-check` locally
3. **Test failures**: Run `make test` locally
4. **Coverage drop**: Add tests for new code

### Release Issues

1. **PyPI publish fails**: Check publisher configuration
2. **Tag already exists**: Delete tag or bump version
3. **Documentation fails**: Check Sphinx warnings

### Documentation Problems

1. **Pages not deploying**: Check GitHub Pages settings
2. **Build warnings**: Run `make html` locally to debug
3. **Missing modules**: Ensure all dependencies in `conf.py`

## Best Practices

1. **Always run `make check` before pushing**
2. **Keep CI green on main branch**
3. **Test releases on TestPyPI first**
4. **Document breaking changes in release notes**
5. **Update version consistently across files**

## Support

For workflow issues:
- Check GitHub Actions logs for detailed error messages
- Review this documentation
- Open an issue with workflow logs attached