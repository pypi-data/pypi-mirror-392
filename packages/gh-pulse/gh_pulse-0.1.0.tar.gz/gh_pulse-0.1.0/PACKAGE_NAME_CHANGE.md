# Package Name Change: gitpulse → gh-pulse

## 🔄 Migration Guide

The package name has been changed from `gitpulse` to `gh-pulse` on PyPI due to naming conflicts.

### Why the Change?

The name `gitpulse` was already registered on PyPI by another developer (versions 1.0-1.2). To publish this package, we needed to choose an available name.

### New Package Name: `gh-pulse`

We chose `gh-pulse` because:
- ✅ Short and memorable
- ✅ Follows GitHub CLI naming conventions (gh = GitHub)
- ✅ Easy to type and pronounce
- ✅ Professional and descriptive
- ✅ Available on PyPI

## 📦 Installation

### Old (Won't Work)
```bash
pip install gitpulse  # This installs a different package!
```

### New (Correct)
```bash
pip install gh-pulse
```

Or with uv:
```bash
uv pip install gh-pulse
```

## 🔧 Command Line Usage

### Commands Work Both Ways

For convenience, both command names are available:

```bash
# New primary command
gh-pulse --help
gh-pulse repo owner/name
gh-pulse user username
gh-pulse badges owner/repo

# Legacy command (also works)
gitpulse --help
gitpulse repo owner/name
```

**Note:** The `gitpulse` command still works after installing `gh-pulse` for backward compatibility.

## 📝 Code Changes Required

### Python Imports (No Change)
```python
# Internal package name stays the same
from gitpulse.github_api import GitHubClient
from gitpulse.badges import BadgeGenerator
```

### CI/CD Updates

#### Before
```yaml
- name: Install gitpulse
  run: pip install gitpulse
  
- name: Generate badges
  run: gitpulse badges ${{ github.repository }}
```

#### After
```yaml
- name: Install gh-pulse
  run: pip install gh-pulse
  
- name: Generate badges
  run: gh-pulse badges ${{ github.repository }}
  # OR use: gitpulse badges ${{ github.repository }}
```

### Documentation Links

Update all references:
- PyPI: `https://pypi.org/project/gh-pulse/`
- Installation: `pip install gh-pulse`
- Badge URLs: Use `gh-pulse` in shields.io badges

## 🚀 Quick Migration Checklist

- [ ] Uninstall old package (if any): `pip uninstall gitpulse`
- [ ] Install new package: `pip install gh-pulse`
- [ ] Update CI/CD workflows to use `gh-pulse` or keep `gitpulse` command
- [ ] Update documentation references
- [ ] Test that commands work: `gh-pulse --version`

## 📊 Version Information

- **Old Package**: `gitpulse` (Different project, not ours)
- **New Package**: `gh-pulse` v0.1.0+
- **Command Names**: Both `gh-pulse` and `gitpulse` work
- **Import Name**: `gitpulse` (unchanged)

## 🔗 URLs

- **PyPI**: https://pypi.org/project/gh-pulse/
- **GitHub**: https://github.com/ruslanlap/gitpulse
- **Issues**: https://github.com/ruslanlap/gitpulse/issues

## ❓ FAQ

### Q: Why is the command still called `gitpulse`?
**A:** For backward compatibility. Both `gh-pulse` and `gitpulse` commands are available after installation.

### Q: Do I need to change my Python imports?
**A:** No! The internal package structure remains `gitpulse`. Only the PyPI package name changed to `gh-pulse`.

### Q: What about the GitHub repository name?
**A:** The repository remains at `github.com/ruslanlap/gitpulse`. Only the PyPI distribution name changed.

### Q: Will this break my existing scripts?
**A:** No! If you were using the command `gitpulse`, it will continue to work. Just install from `gh-pulse` instead.

### Q: Can I still use environment variables?
**A:** Yes! All configuration remains the same:
- `GITHUB_TOKEN` environment variable
- `~/.gitpulse/config` file location
- `~/.gitpulse/cache/` directory

## 📅 Timeline

- **2024-11-18**: Package renamed from `gitpulse` to `gh-pulse`
- **v0.1.0**: First release under new name

## 💡 Recommendations

1. **Use `gh-pulse` command** in new scripts for clarity
2. **Update CI/CD** to install `gh-pulse` package
3. **Keep `gitpulse` command** for local convenience if preferred
4. **Python imports** don't need changes

---

**Questions?** Open an issue at https://github.com/ruslanlap/gitpulse/issues
