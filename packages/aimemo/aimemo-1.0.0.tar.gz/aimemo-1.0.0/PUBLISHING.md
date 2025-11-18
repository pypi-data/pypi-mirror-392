# Publishing AIMemo to PyPI

This guide walks you through publishing AIMemo to PyPI.

## Prerequisites

1. **PyPI Account**: Create at https://pypi.org
2. **API Token**: Get from https://pypi.org/manage/account/token/
3. **Build Tools**: Install with `pip install build twine`

## Step 1: Build the Package

```bash
cd /home/jason/Documents/GitHub/aimemo

# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build
python -m build
```

This creates:
- `dist/aimemo-1.0.0.tar.gz` (source)
- `dist/aimemo-1.0.0-py3-none-any.whl` (wheel)

## Step 2: Test Locally

```bash
# Install locally
pip install -e .

# Run tests
pytest

# Test examples
python examples/manual_memory.py
```

## Step 3: Upload to Test PyPI (Optional)

```bash
# Upload to Test PyPI
python -m twine upload --repository testpypi dist/*

# Test install
pip install --index-url https://test.pypi.org/simple/ aimemo
```

## Step 4: Upload to PyPI

```bash
python -m twine upload dist/*
```

Enter your credentials:
- Username: `__token__`
- Password: Your API token (starts with `pypi-`)

## Step 5: Verify

```bash
pip install aimemo
python -c "from aimemo import AIMemo; print('✓ Success!')"
```

## Version Updates

When releasing new versions:

1. Update version in `pyproject.toml`
2. Update version in `aimemo/__init__.py`
3. Clean and rebuild
4. Upload new version

## Using .pypirc

Create `~/.pypirc` to avoid entering credentials:

```ini
[pypi]
username = __token__
password = pypi-your_token_here

[testpypi]
username = __token__
password = pypi-your_test_token_here
```

Then simply run:
```bash
python -m twine upload dist/*
```

## Automation with GitHub Actions

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
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install build twine
      - name: Build
        run: python -m build
      - name: Publish
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
        run: twine upload dist/*
```

Add your PyPI token as `PYPI_TOKEN` in GitHub Secrets.

## Checklist

Before publishing:

- [ ] Update version numbers
- [ ] Run all tests (`pytest`)
- [ ] Update README if needed
- [ ] Test locally (`pip install -e .`)
- [ ] Clean build artifacts
- [ ] Build package (`python -m build`)
- [ ] Test on Test PyPI (optional)
- [ ] Upload to PyPI
- [ ] Test installation
- [ ] Create GitHub release
- [ ] Update documentation

---

**Your package is original work - no attribution needed!**

