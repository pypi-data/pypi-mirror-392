# Publishing ConnectVM CLI to PyPI

This guide explains how to publish the `python-cvmclient` package to PyPI so users can install it via `pip install python-cvmclient`.

## Prerequisites

1. **PyPI Account**: Create accounts on:
   - PyPI (production): https://pypi.org/account/register/
   - TestPyPI (testing): https://test.pypi.org/account/register/

2. **Install Build Tools**:
```bash
pip install --upgrade build twine
```

3. **API Tokens**: Generate API tokens for authentication:
   - Go to https://pypi.org/manage/account/token/
   - Create a new API token
   - Save it securely (you'll need it for publishing)

## Step 1: Prepare the Package

### 1.1 Set Version Number

Edit the version in your package. Since we're using pbr, create a git tag:

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial commit of ConnectVM CLI"

# Create a version tag
git tag -a 0.1.0 -m "Release version 0.1.0"
```

Or manually set version in `setup.cfg`:
```ini
[metadata]
version = 0.1.0
```

### 1.2 Update Package Metadata

Ensure `setup.cfg` and `pyproject.toml` have correct information:
- Package name: `python-cvmclient`
- Author: ConnectVM
- Homepage: https://console.connectvm.com/
- License: Apache-2.0

### 1.3 Create Required Files

Ensure you have:
- `README.rst` or `README.md` (we have README.rst)
- `LICENSE` (we have this from OpenStack)
- `pyproject.toml` (we have this)
- `setup.cfg` (we have this)

## Step 2: Build the Package

### 2.1 Clean Previous Builds

```bash
# Remove old build artifacts
rm -rf build/ dist/ *.egg-info/
```

### 2.2 Build Distribution Files

```bash
# Build source distribution and wheel
python -m build
```

This creates:
- `dist/python-cvmclient-0.1.0.tar.gz` (source distribution)
- `dist/python_cvmclient-0.1.0-py3-none-any.whl` (wheel distribution)

### 2.3 Verify the Build

```bash
# Check the distribution files
ls -la dist/

# Verify package metadata
tar -tzf dist/python-cvmclient-0.1.0.tar.gz | head -20
```

## Step 3: Test on TestPyPI First

### 3.1 Configure TestPyPI Credentials

Create `~/.pypirc`:
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-production-token-here

[testpypi]
username = __token__
password = pypi-your-test-token-here
```

Or use environment variables:
```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-token-here
```

### 3.2 Upload to TestPyPI

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*
```

### 3.3 Test Installation from TestPyPI

```bash
# Create a test virtual environment
python -m venv test-env
source test-env/bin/activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    python-cvmclient

# Test the command
cvm --version
cvm --help

# Clean up
deactivate
rm -rf test-env
```

## Step 4: Publish to Production PyPI

### 4.1 Final Checks

```bash
# Run tests
tox -e py311

# Check package with twine
python -m twine check dist/*

# Verify all files are included
tar -tzf dist/python-cvmclient-0.1.0.tar.gz
```

### 4.2 Upload to PyPI

```bash
# Upload to production PyPI
python -m twine upload dist/*
```

You'll see output like:
```
Uploading distributions to https://upload.pypi.org/legacy/
Uploading python_cvmclient-0.1.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 
Uploading python-cvmclient-0.1.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

View at:
https://pypi.org/project/python-cvmclient/0.1.0/
```

### 4.3 Verify Publication

```bash
# Check the package page
open https://pypi.org/project/python-cvmclient/

# Test installation
pip install python-cvmclient

# Test the command
cvm --version
```

## Step 5: Publish Updates

For subsequent releases:

```bash
# 1. Update version number
git tag -a 0.2.0 -m "Release version 0.2.0"

# 2. Clean and rebuild
rm -rf build/ dist/ *.egg-info/
python -m build

# 3. Upload new version
python -m twine upload dist/*
```

## Using GitHub Actions for Automated Publishing

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
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    
    - name: Build package
      run: python -m build
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: python -m twine upload dist/*
```

Then add your PyPI token as a GitHub secret named `PYPI_API_TOKEN`.

## Manual Publishing Checklist

- [ ] Version number updated (git tag or setup.cfg)
- [ ] All tests passing (`tox`)
- [ ] README.rst is accurate and up-to-date
- [ ] LICENSE file is present
- [ ] Clean build directory (`rm -rf build/ dist/ *.egg-info/`)
- [ ] Build package (`python -m build`)
- [ ] Check package (`python -m twine check dist/*`)
- [ ] Test on TestPyPI first
- [ ] Verify test installation works
- [ ] Upload to production PyPI (`python -m twine upload dist/*`)
- [ ] Verify on PyPI website
- [ ] Test production installation
- [ ] Create GitHub release (if using GitHub)
- [ ] Update documentation with new version

## Common Issues

### Issue: "File already exists"
**Solution**: You're trying to upload a version that already exists. Increment the version number.

### Issue: "Invalid credentials"
**Solution**: Check your `~/.pypirc` file or `TWINE_PASSWORD` environment variable.

### Issue: "Package name already taken"
**Solution**: The package name `python-cvmclient` must be unique on PyPI. Check if it's available first at https://pypi.org/project/python-cvmclient/

### Issue: Missing dependencies during installation
**Solution**: Ensure all dependencies are listed in `requirements.txt` and properly specified in `pyproject.toml`.

### Issue: "README not rendering"
**Solution**: Validate your README.rst format:
```bash
pip install readme-renderer
python -m readme_renderer README.rst -o /tmp/README.html
```

## Package Name Availability

Before publishing, check if the name is available:

```bash
# Try installing - if it doesn't exist, you'll get an error
pip install python-cvmclient
# ERROR: Could not find a version that satisfies the requirement python-cvmclient

# Or check on PyPI
open https://pypi.org/project/python-cvmclient/
```

If `python-cvmclient` is already taken, you might need to choose an alternative name like:
- `connectvm-cli`
- `cvmclient`
- `connectvm-client`

## Security Best Practices

1. **Never commit tokens**: Add `.pypirc` to `.gitignore`
2. **Use API tokens**: Don't use username/password
3. **Scope tokens**: Create project-specific tokens when possible
4. **Rotate tokens**: Regularly update your API tokens
5. **Use 2FA**: Enable two-factor authentication on PyPI

## After Publishing

Once published, users can install with:

```bash
pip install python-cvmclient
```

And use it immediately:

```bash
cvm --version
cvm --help
cvm server list
```

## Versioning Strategy

Follow Semantic Versioning (semver):
- **MAJOR** version (1.0.0): Incompatible API changes
- **MINOR** version (0.1.0): Add functionality (backwards-compatible)
- **PATCH** version (0.0.1): Bug fixes (backwards-compatible)

Example:
- `0.1.0` - Initial release
- `0.1.1` - Bug fix
- `0.2.0` - New features
- `1.0.0` - Stable release
