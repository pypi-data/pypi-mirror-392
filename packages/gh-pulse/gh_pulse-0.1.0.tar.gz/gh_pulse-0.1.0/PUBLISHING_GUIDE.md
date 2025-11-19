# 📦 Publishing Guide for gh-pulse

Complete guide for publishing `gh-pulse` to PyPI and creating GitHub releases.

## 🔍 Pre-Publishing Checklist

### 1. Verify Package Name Availability
```bash
# Check if the name is available on PyPI
pip index versions gh-pulse 2>&1 | grep -q "ERROR" && echo "✅ Available" || echo "❌ Taken"
```

### 2. Update Version Number
Edit `pyproject.toml`:
```toml
[project]
name = "gh-pulse"
version = "0.1.0"  # Update this for each release
```

### 3. Update Changelog
Create/update `CHANGELOG.md` with release notes:
```markdown
## [0.1.0] - 2024-11-18

### Added
- Initial release
- Repository statistics command
- User profile analytics
- Badge generation
- Data export functionality
- Local caching system
```

### 4. Clean Build Artifacts
```bash
rm -rf dist/ build/ *.egg-info src/*.egg-info
```

## 🏗️ Building the Package

### Option 1: Using uv (Recommended)
```bash
# Build the package
uv build

# Verify the build
ls -lh dist/
# Should show:
# gh_pulse-0.1.0-py3-none-any.whl
# gh_pulse-0.1.0.tar.gz
```

### Option 2: Using build module
```bash
# Install build in a virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install build

# Build the package
python -m build

# Deactivate when done
deactivate
```

## ✅ Verify the Package

### Check with twine
```bash
# Install twine
pip install twine

# Check the distribution files
twine check dist/*
```

Expected output:
```
Checking dist/gh_pulse-0.1.0-py3-none-any.whl: PASSED
Checking dist/gh_pulse-0.1.0.tar.gz: PASSED
```

### Inspect Package Contents
```bash
# List contents of wheel
unzip -l dist/gh_pulse-0.1.0-py3-none-any.whl

# Extract and check tar.gz
tar -tzf dist/gh_pulse-0.1.0.tar.gz
```

### Test Local Installation
```bash
# Create a test environment
python3 -m venv test_env
source test_env/bin/activate

# Install the local package
pip install dist/gh_pulse-0.1.0-py3-none-any.whl

# Test the commands
gh-pulse --version
gh-pulse --help
gitpulse --help  # Test legacy command

# Test imports
python -c "from gitpulse.cli import app; print('✅ Import successful')"

# Cleanup
deactivate
rm -rf test_env
```

## 🚀 Publishing to PyPI

### 1. Setup PyPI Account

1. Create account at https://pypi.org/account/register/
2. Verify your email
3. Enable 2FA (required for new projects)
4. Go to https://pypi.org/manage/account/token/
5. Create a new API token:
   - Token name: `gh-pulse-upload`
   - Scope: **Entire account** (for first upload)
   - Copy the token (starts with `pypi-`)

### 2. Configure Token

#### Option A: Environment Variable (Temporary)
```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-YOUR-TOKEN-HERE
```

#### Option B: .pypirc File (Persistent)
Create `~/.pypirc`:
```ini
[pypi]
username = __token__
password = pypi-YOUR-TOKEN-HERE
```

Set permissions:
```bash
chmod 600 ~/.pypirc
```

### 3. Upload to PyPI

#### Test PyPI First (Optional but Recommended)
```bash
# Register at https://test.pypi.org/
# Create token for test.pypi.org

# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ --no-deps gh-pulse

# Test the package
gh-pulse --version
```

#### Upload to Production PyPI
```bash
# Upload to PyPI
twine upload dist/*

# Or with explicit repository
twine upload --repository pypi dist/*
```

Expected output:
```
Uploading distributions to https://upload.pypi.org/legacy/
Uploading gh_pulse-0.1.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 18.5/18.5 kB • 00:00
Uploading gh_pulse-0.1.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 17.9/17.9 kB • 00:00

View at:
https://pypi.org/project/gh-pulse/0.1.0/
```

### 4. Verify Publication
```bash
# Wait 1-2 minutes for PyPI to index

# Check the package page
open https://pypi.org/project/gh-pulse/

# Install from PyPI
pip install gh-pulse

# Test it works
gh-pulse --version
```

## 🏷️ GitHub Release

### 1. Create Git Tag
```bash
# Ensure version matches pyproject.toml
VERSION="0.1.0"

# Create annotated tag
git tag -a "v${VERSION}" -m "Release v${VERSION}"

# Push tag to GitHub
git push origin "v${VERSION}"
```

### 2. GitHub Actions (Automated)

If you have the publish workflow set up:
```bash
# Just push the tag
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0

# GitHub Actions will automatically:
# 1. Build the package
# 2. Create GitHub Release
# 3. Upload to PyPI
```

### 3. Manual GitHub Release

1. Go to https://github.com/ruslanlap/gitpulse/releases/new
2. Choose the tag: `v0.1.0`
3. Release title: `v0.1.0`
4. Description:
   ```markdown
   ## 🚀 gh-pulse v0.1.0
   
   First release of gh-pulse - GitHub productivity CLI!
   
   ### Installation
   ```bash
   pip install gh-pulse
   ```
   
   ### Features
   - 📊 Repository statistics
   - 👤 User profile analytics
   - 🏷️ Badge generation
   - 📤 Data export
   - 💾 Local caching
   
   See [README](https://github.com/ruslanlap/gitpulse#readme) for full documentation.
   ```
5. Upload artifacts: `dist/*.whl` and `dist/*.tar.gz`
6. Click **Publish release**

## 🔄 Updating After First Release

### Update Scoped Token (Recommended)
After first successful upload:
1. Go to https://pypi.org/manage/project/gh-pulse/settings/
2. Create a new scoped token:
   - Token name: `gh-pulse-ci`
   - Scope: **Project: gh-pulse** (more secure)
3. Update your secrets/environment variables

### For GitHub Actions
1. Go to repository Settings → Secrets and variables → Actions
2. Update `PYPI_API_TOKEN` with the new scoped token

## 🐛 Troubleshooting

### Error: "The user isn't allowed to upload to project"
**Solution:** The package name already exists and you're not the owner.
```bash
# Choose a different name
# Update pyproject.toml with new name
# Rebuild and try again
```

### Error: "File already exists"
**Solution:** Version already published.
```bash
# Increment version in pyproject.toml
# Rebuild package
# Upload again
```

### Error: "Invalid or non-existent authentication"
**Solution:** Token is incorrect or expired.
```bash
# Verify token starts with pypi-
# Check token hasn't been revoked
# Create new token if needed
```

### Error: "HTTPError: 400 Bad Request"
**Solution:** Package metadata might be invalid.
```bash
# Check pyproject.toml syntax
# Verify all required fields
# Run: twine check dist/*
```

## 📝 Version Numbering Guide

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

Examples:
- `0.1.0` - Initial development release
- `0.2.0` - Added new features
- `0.2.1` - Fixed bugs
- `1.0.0` - First stable release
- `1.1.0` - Added features to stable release
- `2.0.0` - Breaking changes

Pre-release versions:
- `0.1.0-alpha.1` - Alpha version
- `0.1.0-beta.1` - Beta version
- `0.1.0-rc.1` - Release candidate

## 🔐 Security Best Practices

1. **Never commit tokens** to git
2. **Use scoped tokens** after first upload
3. **Enable 2FA** on PyPI account
4. **Use .pypirc** with 600 permissions
5. **Rotate tokens** periodically
6. **Use GitHub Secrets** for CI/CD
7. **Review upload** before confirming

## 📊 Post-Publication Tasks

### 1. Verify Installation
```bash
# Fresh environment
python3 -m venv fresh_env
source fresh_env/bin/activate
pip install gh-pulse
gh-pulse --version
deactivate
rm -rf fresh_env
```

### 2. Update Documentation
- ✅ Update README badges to show correct version
- ✅ Add release notes to CHANGELOG.md
- ✅ Update documentation site (if any)
- ✅ Announce on social media/forums

### 3. Monitor
- 📊 Check PyPI download stats: https://pypistats.org/packages/gh-pulse
- 🐛 Monitor GitHub Issues for bug reports
- 💬 Respond to community feedback

## 🎯 Quick Reference

### Complete Release Process
```bash
# 1. Update version
vim pyproject.toml

# 2. Update changelog
vim CHANGELOG.md

# 3. Commit changes
git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to 0.1.0"
git push

# 4. Clean and build
rm -rf dist/
uv build

# 5. Check package
twine check dist/*

# 6. Upload to PyPI
twine upload dist/*

# 7. Create and push tag
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0

# 8. Create GitHub Release (or let Actions do it)
# Go to GitHub → Releases → New Release

# 9. Verify
pip install --upgrade gh-pulse
gh-pulse --version
```

## 📚 Resources

- **PyPI Help**: https://pypi.org/help/
- **Packaging Guide**: https://packaging.python.org/
- **Twine Documentation**: https://twine.readthedocs.io/
- **Semantic Versioning**: https://semver.org/
- **PEP 517**: https://peps.python.org/pep-0517/
- **PEP 518**: https://peps.python.org/pep-0518/

---

**Questions?** Open an issue at https://github.com/ruslanlap/gitpulse/issues
