# Development Guide

This document explains how to set up, build, test, and release the d361 project.

## Table of Contents

- [Development Setup](#development-setup)
- [Build System](#build-system)
- [Testing](#testing)
- [Release Process](#release-process)
- [CI/CD Pipeline](#cicd-pipeline)
- [Binary Distribution](#binary-distribution)
- [Contributing](#contributing)

## Development Setup

### Prerequisites

- Python 3.10 or newer (3.12 recommended)
- [uv](https://github.com/astral-sh/uv) – fast Python package installer
- [hatch](https://hatch.pypa.io/) – project management tool
- Git

### Quick Setup

```bash
# Clone the repo
git clone https://github.com/twardoch/d361.git
cd d361

# Install uv if missing
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install hatch
uv pip install hatch

# Activate dev environment
hatch shell

# Install Playwright browsers
playwright install chromium

# Run tests to confirm setup
hatch run test:test
```

## Build System

### Local Build Scripts

The `scripts/` directory contains useful automation tools:

#### Build Script (`scripts/build.sh`)

```bash
# Full build with checks
./scripts/build.sh

# Quick build (skip tests and linting)
./scripts/build.sh --quick

# Clean previous builds
./scripts/build.sh --clean

# Show options
./scripts/build.sh --help
```

#### Test Script (`scripts/test.sh`)

```bash
# All tests
./scripts/test.sh

# Unit tests only
./scripts/test.sh --quick

# Include integration tests
./scripts/test.sh --integration

# Install Playwright browsers
./scripts/test.sh --install-browsers

# Auto-fix lint issues
./scripts/test.sh --fix
```

#### Release Script (`scripts/release.sh`)

```bash
# Tag and release version 1.0.0
./scripts/release.sh --version 1.0.0

# Dry run using Test PyPI
./scripts/release.sh --version 1.0.0 --dry-run

# Skip steps like testing or GitHub actions
./scripts/release.sh --version 1.0.0 --skip-tests --skip-github
```

### Hatch Commands

Hatch handles virtual environments and tasks:

```bash
# Run tests with coverage report
hatch run test:test-cov

# Lint and format code
hatch run lint:fix

# Type check
hatch run lint:typing

# Run all quality checks
hatch run lint:all

# Build package
hatch run build
```

## Testing

### Test Structure

```
tests/
├── test_package.py           # Basic package tests
├── offline/
│   ├── test_offline_core.py  # Core offline functionality
│   ├── test_parser.py        # Sitemap parsing tests
│   ├── test_content.py       # Content extraction tests
│   ├── test_navigation.py    # Navigation extraction tests
│   └── test_integration.py  # Integration tests
```

### Test Categories

- **Unit Tests** – Test single components
- **Integration Tests** – Test component interactions
- **End-to-End Tests** – Test full workflows

### Running Tests

```bash
# Run all tests
hatch run test:test

# With coverage
hatch run test:test-cov

# Specific file
hatch run test:test tests/offline/test_parser.py

# Match pattern
hatch run test:test -k "test_navigation"

# Verbose output
hatch run test:test -v
```

### Test Configuration

Defined in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
markers = [
    "unit: unit tests",
    "integration: integration tests",
    "slow: slow tests"
]
```

## Release Process

### Semantic Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** – Breaking changes
- **MINOR** – New features (backward compatible)
- **PATCH** – Bug fixes (backward compatible)

### Version Management

Versions come from Git tags via `hatch-vcs`:

- Tag format: `v1.0.0`, `v1.0.0-alpha.1`
- No manual version strings in source

### Release Steps

1. **Prepare Release**
   ```bash
   git checkout main
   git pull origin main
   ./scripts/test.sh
   ./scripts/build.sh
   ```

2. **Create Release**
   ```bash
   ./scripts/release.sh --version 1.0.0
   ```

3. **Verify Release**
   - Check GitHub Actions
   - Confirm PyPI upload
   - Test binary downloads
   - Review GitHub release

### Pre-release Testing

```bash
# Dry run to Test PyPI
./scripts/release.sh --version 1.0.0-beta.1 --dry-run

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ d361==1.0.0-beta.1
```

## CI/CD Pipeline

### GitHub Actions Workflows

#### Push Workflow (`.github/workflows/push.yml`)

Triggers on every push to `main` or PR:

- Code quality checks (lint, format)
- Type checking with MyPy
- Tests on Ubuntu, Windows, macOS
- Python 3.10–3.12 support
- Build verification
- Installation test

#### Release Workflow (`.github/workflows/release.yml`)

Triggers on tag push (`v*`):

- Full test matrix
- Source and wheel builds
- PyInstaller binaries for all platforms
- PyPI publish
- GitHub release with assets
- Post-release install test

### Workflow Features

- Cancels outdated runs
- Caches dependencies using UV
- Matrix testing across OS and Python versions
- Secure action permissions

## Binary Distribution

### PyInstaller Configuration

Standalone executables built with PyInstaller:

```bash
pyinstaller --onefile --name d361-offline-linux \
    --add-data "src/d361/offline/d361_offline.css:d361/offline" \
    src/d361/offline/__main__.py
```

### Binary Artifacts

Each release includes:

- Linux: `d361-offline-ubuntu-latest`
- Windows: `d361-offline-windows-latest.exe`
- macOS: `d361-offline-macos-latest`

### Usage

```bash
# Download binary
curl -L -o d361-offline https://github.com/twardoch/d361/releases/latest/download/d361-offline-ubuntu-latest

# Make executable
chmod +x d361-offline

# Run
./d361-offline --help
```

## Contributing

### Code Quality

- Use Ruff for linting and formatting
- Use MyPy for type checking
- Keep test coverage high

### Development Workflow

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR-USERNAME/d361.git
   cd d361
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Develop and Test**
   ```bash
   # Make changes
   ./scripts/test.sh
   ./scripts/build.sh
   ```

4. **Commit and Push**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Target `main` branch
   - Describe changes clearly
   - Ensure CI passes

### Code Standards

- Follow PEP 8
- Add type hints everywhere
- Write docstrings for public functions
- Include tests for new code
- Update docs when needed

### Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new feature
fix: resolve bug
docs: update documentation
test: add test coverage
refactor: improve code structure
```

## Troubleshooting

### Common Issues

1. **Playwright Browser Issues**
   ```bash
   playwright install chromium
   ```

2. **Build Failures**
   ```bash
   ./scripts/build.sh --clean
   ./scripts/build.sh
   ```

3. **Test Failures**
   ```bash
   hatch run test:test tests/offline/test_parser.py -v
   ```

4. **Version Issues**
   ```bash
   git describe --tags --abbrev=0
   hatch version
   ```

### Getting Help

- [GitHub Issues](https://github.com/twardoch/d361/issues)
- [GitHub Discussions](https://github.com/twardoch/d361/discussions)
- [README.md](README.md)

## Resources

- [Hatch Documentation](https://hatch.pypa.io/)
- [UV Documentation](https://github.com/astral-sh/uv)
- [Pytest Documentation](https://docs.pytest.org/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
- [PyInstaller Documentation](https://pyinstaller.org/)
- [Semantic Versioning](https://semver.org/)