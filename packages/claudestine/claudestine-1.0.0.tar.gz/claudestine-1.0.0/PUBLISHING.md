# Publishing to PyPI

## Prerequisites

1. **PyPI account**: Create account at https://pypi.org/account/register/
2. **API token**: Generate at https://pypi.org/manage/account/token/
3. **Test PyPI account** (optional): https://test.pypi.org/account/register/
4. **Install twine**: `uv add --dev twine`

## Setup API Token

Create `~/.pypirc`:

```ini
[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmc...  # Your PyPI API token

[testpypi]
username = __token__
password = pypi-AgENdGVzdC5weXBp...  # Your TestPyPI token (optional)
```

Set proper permissions:

```bash
chmod 600 ~/.pypirc
```

## Build and Publish

### 1. Update Version

Edit `pyproject.toml`:

```toml
[project]
version = "1.0.1"  # Increment version
```

### 2. Build Distribution

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build wheel and source distribution
uv build
```

This creates:
- `dist/claudestine-1.0.0-py3-none-any.whl` (wheel)
- `dist/claudestine-1.0.0.tar.gz` (source)

### 3. Check Distribution

```bash
# Verify package metadata and contents
uv run twine check dist/*
```

Should output:
```
Checking dist/claudestine-1.0.0-py3-none-any.whl: PASSED
Checking dist/claudestine-1.0.0.tar.gz: PASSED
```

### 4. Publish to Test PyPI (Optional but Recommended)

```bash
# Upload to Test PyPI first
uv run twine upload --repository testpypi dist/*
```

Verify installation:

```bash
uv add --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ claudestine
```

### 5. Publish to Production PyPI

```bash
# Upload to PyPI
uv run twine upload dist/*
```

Or use `uv publish` (wrapper around twine):

```bash
uv publish
```

## Post-Publication

### Verify Installation

```bash
# Install from PyPI
uv add claudestine

# Or with pip
pip install claudestine
```

### Update README Installation Instructions

Update `README.md`:

```markdown
## Installation

\`\`\`bash
uv add claudestine
\`\`\`

Or using pip:

\`\`\`bash
pip install claudestine
\`\`\`
```

### Create Git Tag

```bash
# Tag release
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

## Version Numbering

Follow semantic versioning (semver):

- **MAJOR** (1.x.x): Breaking changes
- **MINOR** (x.1.x): New features, backward compatible
- **PATCH** (x.x.1): Bug fixes, backward compatible

## Checklist

Before publishing:

- [ ] Tests pass (`uv run pytest`)
- [ ] Version bumped in `pyproject.toml`
- [ ] CHANGELOG.md updated (if exists)
- [ ] README.md accurate
- [ ] LICENSE file present
- [ ] Build succeeds (`uv build`)
- [ ] Test PyPI upload works (optional)
- [ ] Production PyPI upload
- [ ] Git tag created
- [ ] GitHub release created (optional)

## Complete Workflow

```bash
# 1. Update version
# Edit pyproject.toml

# 2. Clean and build
rm -rf dist/ build/ *.egg-info
uv build

# 3. Verify build
uv run twine check dist/*

# 4. Test on TestPyPI (optional)
uv run twine upload --repository testpypi dist/*

# 5. Publish to PyPI
uv run twine upload dist/*

# 6. Tag release
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

## Troubleshooting

### Authentication Failed

```bash
# Check ~/.pypirc exists and has correct token
cat ~/.pypirc

# Or pass token via environment
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-...
uv run twine upload dist/*

# Or prompt for password
uv run twine upload dist/* --username __token__
```

### Version Already Exists

```bash
# PyPI doesn't allow re-uploading same version
# Increment version in pyproject.toml
# Rebuild and republish
rm -rf dist/
# Edit version in pyproject.toml
uv build
uv run twine upload dist/*
```

### Check What Will Be Included

```bash
# Inspect wheel contents
unzip -l dist/claudestine-1.0.0-py3-none-any.whl

# Inspect source distribution
tar -tzf dist/claudestine-1.0.0.tar.gz
```

### Build Warnings

```bash
# Ensure all required files included
# Check [tool.hatch.build.targets.wheel]
# Verify src/ structure correct
tree src/
```

## Automated Publishing (GitHub Actions)

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v2

      - name: Build package
        run: uv build

      - name: Publish to PyPI
        env:
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
        run: uv publish
```

Add `PYPI_TOKEN` secret to GitHub repository settings.

## Resources

- PyPI: https://pypi.org
- Test PyPI: https://test.pypi.org
- Packaging guide: https://packaging.python.org
- uv docs: https://docs.astral.sh/uv/
