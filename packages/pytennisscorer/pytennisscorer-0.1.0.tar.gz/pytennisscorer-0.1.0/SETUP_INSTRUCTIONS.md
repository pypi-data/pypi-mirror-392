# Setup Instructions - Action Required

This document outlines the steps you need to take to complete the GitHub Actions workflows setup for pytennisscorer.

## ✅ Already Completed (by Claude)

- [x] Created 3 GitHub Actions workflows (CI, Release, Documentation)
- [x] Set up complete Sphinx documentation structure
- [x] Updated README with CI badges
- [x] Added documentation dependencies to pyproject.toml
- [x] Created comprehensive workflow documentation
- [x] Tested documentation build locally (successful)

## 📋 Actions Required from You

### 1. Commit and Push the Changes

All the workflow files and documentation have been created. You need to commit and push them:

```bash
# Review the changes
git status

# Stage all new files
git add .

# Commit the changes
git commit -m "feat: add GitHub Actions workflows and Sphinx documentation

- Add CI workflow for testing across Python 3.9-3.12 and multiple OS
- Add release workflow for automated PyPI publishing
- Add documentation workflow for GitHub Pages deployment
- Set up comprehensive Sphinx documentation with RTD theme
- Add CI badges to README
- Add documentation dependencies to pyproject.toml"

# Push to GitHub
git push origin main
```

### 2. Enable GitHub Pages (Already Done ✓)

You mentioned GitHub Pages is already set up. Verify it's configured correctly:

1. Go to: https://github.com/talktennisdata/pytennisscorer/settings/pages
2. Ensure **Source** is set to: **GitHub Actions**
3. After the first push, the docs workflow will deploy to:
   - https://talktennisdata.github.io/pytennisscorer/

### 3. Set Up PyPI Publishing (When Ready to Publish)

When you're ready to publish to PyPI, you need to configure **Trusted Publishing**:

#### For PyPI (Production)

1. Go to https://pypi.org and log in
2. Navigate to: **Account Settings** → **Publishing**
3. Click **Add a new pending publisher**
4. Fill in:
   - **PyPI Project Name**: `pytennisscorer`
   - **Owner**: `talktennisdata`
   - **Repository name**: `pytennisscorer`
   - **Workflow name**: `release.yml`
   - **Environment name**: `pypi`
5. Click **Add**

#### For TestPyPI (Testing - Optional but Recommended)

1. Go to https://test.pypi.org and log in
2. Navigate to: **Account Settings** → **Publishing**
3. Click **Add a new pending publisher**
4. Fill in:
   - **PyPI Project Name**: `pytennisscorer`
   - **Owner**: `talktennisdata`
   - **Repository name**: `pytennisscorer`
   - **Workflow name**: `release.yml`
   - **Environment name**: `testpypi`
5. Click **Add**

**Note:** You don't need to create the project on PyPI first. The first release will create it automatically using trusted publishing.

### 4. (Optional) Set Up Codecov for Coverage Reports

If you want coverage reports on your PRs:

1. Go to https://codecov.io
2. Sign in with GitHub
3. Add your repository: `talktennisdata/pytennisscorer`
4. No token needed - it uses GitHub Actions integration
5. Coverage reports will appear automatically on PRs

## 🧪 Testing the Workflows

### Test 1: CI Workflow (Automatic)

Once you push your changes, the CI workflow will run automatically. Check:

1. Go to: https://github.com/talktennisdata/pytennisscorer/actions
2. Look for the "CI" workflow
3. Verify all jobs pass:
   - Lint & Format Check
   - Type Check
   - Test Matrix (7 jobs)
   - Notebook Testing
   - Build Verification

### Test 2: Documentation (Automatic)

The documentation workflow will also run automatically and deploy to GitHub Pages.

Check deployment:
1. Go to: https://github.com/talktennisdata/pytennisscorer/actions
2. Look for "Documentation" workflow
3. After it completes, visit: https://talktennisdata.github.io/pytennisscorer/

### Test 3: Release Workflow (Manual - Later)

**DO NOT DO THIS YET** - Only when you're ready for the first release:

#### Option A: Test with TestPyPI First (Recommended)

```bash
# Manually trigger the workflow with TestPyPI
gh workflow run release.yml -f test_pypi=true
```

Or via GitHub UI:
1. Go to: https://github.com/talktennisdata/pytennisscorer/actions/workflows/release.yml
2. Click "Run workflow"
3. Select `test_pypi: true`
4. Click "Run workflow"

#### Option B: Create a Real Release

When ready for production release:

```bash
# Update version in pyproject.toml first
# Then create a GitHub release
gh release create v0.1.0 \
  --title "v0.1.0 - Initial Release" \
  --notes "First public release of pytennisscorer

Features:
- Tennis match scoring for multiple formats
- Support for Grand Slam, ATP, Davis Cup matches
- Comprehensive tiebreak support
- Undo functionality
- Zero dependencies"
```

This will automatically:
- Run all tests
- Build the package
- Publish to PyPI
- Create a git tag
- Generate a changelog PR

## 📊 What Happens After Push

### Immediate (on every push to main/develop)
- ✅ CI workflow runs tests across all Python versions and platforms
- ✅ Code quality checks (linting, type checking)
- ✅ Coverage reports generated
- ✅ Documentation builds

### On Main Branch Only
- ✅ Documentation deploys to GitHub Pages

### On Release Creation
- ✅ Package builds and publishes to PyPI
- ✅ Git tag created
- ✅ Changelog PR generated

## 🔍 Monitoring

After pushing, monitor the workflows:

```bash
# Watch workflow status (requires gh CLI)
gh run watch

# Or view in browser
open https://github.com/talktennisdata/pytennisscorer/actions
```

## 📚 Documentation

For detailed information about the workflows, see:
- `WORKFLOWS.md` - Comprehensive workflow documentation
- `.github/workflows/ci.yml` - CI workflow configuration
- `.github/workflows/release.yml` - Release workflow configuration
- `.github/workflows/docs.yml` - Documentation workflow configuration

## ❓ Troubleshooting

### CI Fails
- Check the logs in GitHub Actions
- Run `make check` locally to reproduce issues
- Ensure all tests pass with `make test`

### Documentation Fails to Build
- Check for Sphinx warnings in the workflow logs
- Test locally with: `cd docs && uv run sphinx-build -b html . _build/html`

### PyPI Publishing Fails
- Verify trusted publisher is configured correctly
- Check that version in `pyproject.toml` hasn't been published already
- Review workflow logs for detailed error messages

## 🎯 Next Steps After Setup

1. **Push the changes** (step 1 above)
2. **Verify CI passes** on GitHub Actions
3. **Check documentation** deployed to GitHub Pages
4. **Set up PyPI** when ready to publish first version
5. **Create first release** when version 0.1.0 is ready

## 💡 Tips

- Always test PyPI publishing with TestPyPI first
- Keep version numbers in sync between releases and `pyproject.toml`
- The workflows are configured to use `uv` for fast dependency management
- Coverage threshold is set to 80% - CI fails if coverage drops below

## ✨ You're Almost Done!

Just commit, push, and verify the workflows run successfully. Everything else is automated!

If you encounter any issues, check the GitHub Actions logs for detailed error messages.