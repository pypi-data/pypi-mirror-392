# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

`build_harness` is a CI pipeline build harness utility for Python 3 projects. It provides a command-line interface to streamline Python project creation with best practices, including testing, static analysis, formatting, packaging, and publishing. The project uses cookiecutter templates to bootstrap new Python projects with a ready-to-run GitLab CI pipeline.

## Core Commands

### Development Workflow

```bash
# Install dependencies into .venv (creates venv if needed)
.venv/bin/build-harness install

# Check if dependencies are up to date
.venv/bin/build-harness install --check

# Format code (isort + black)
.venv/bin/build-harness formatting

# Check formatting without applying
.venv/bin/build-harness formatting --check

# Run all static analysis (formatting + flake8 + mypy)
.venv/bin/build-harness static-analysis

# Run specific static analysis
.venv/bin/build-harness static-analysis --analysis flake8
.venv/bin/build-harness static-analysis --analysis mypy

# Run all unit tests
.venv/bin/build-harness unit-test

# Run unit tests in specific directory
.venv/bin/build-harness unit-test --test-dir tests/ci/unit_tests

# Run unit tests with coverage threshold check (90%)
.venv/bin/build-harness unit-test --check 90

# Run unit tests with coverage console output
.venv/bin/build-harness unit-test --coverage-console

# Run acceptance tests (behave)
.venv/bin/build-harness acceptance tests

# Generate snippets for unimplemented BDD steps
.venv/bin/build-harness acceptance snippets

# Report BDD tags usage
.venv/bin/build-harness acceptance tags
```

### Release and Publishing

```bash
# Calculate release ID from git tags and commit history
release-flow --project . --default-branch main

# Package the project
.venv/bin/build-harness package --release-id <version>

# Publish to PyPI
.venv/bin/build-harness publish --user __token__ --password <token> --publish yes

# Check if should publish based on branch/tag
publish-flow --default-branch main
```

### Bootstrapping New Projects

```bash
# Create new project from template
.venv/bin/build-harness bootstrap my_new_project

# With options
.venv/bin/build-harness bootstrap my_new_project \
  --ci gitlabci \
  --packager flit \
  --default-branch main
```

### Invoke Tasks (Docker/Kaniko)

```bash
# Build Docker image using Kaniko
invoke build-docker-image --venv-path /venv
```

## Architecture

### Entry Points

The project provides three CLI entry points defined in `build_harness/entrypoint.py`:
- `build-harness`: Main command with subcommands (formatting, static-analysis, unit-test, acceptance, install, package, publish, bootstrap)
- `release-flow`: Standalone utility to compute PEP-440 release IDs from git tags and commit history
- `publish-flow`: Standalone utility to determine if artifacts should be published based on branch/tag

### Command Structure

Commands are organized in `build_harness/commands/`:
- `build_harness_group.py`: Main CLI group using Click
- `code_style.py`: Formatting commands (isort, black)
- `analysis.py`: Static analysis (flake8, mypy, pydocstyle)
- `unit_tests.py`: Pytest execution with coverage
- `bdd/`: Behave (BDD) acceptance testing commands
- `dependencies.py`: Virtual environment and dependency management
- `wheel.py`: Package building
- `publishing.py`: PyPI publishing
- `bootstrap.py`: Project template initialization
- `_release_flow.py`: Release ID calculation logic
- `_publish_flow.py`: Publishing decision logic

### Version Management

The project uses a `VERSION` file workflow:
- `build_harness/_version.py` reads version from `build_harness/VERSION` file
- If VERSION file missing, falls back to `DEFAULT_RELEASE_ID` from `_default_values.py`
- The `release-flow` command generates PEP-440 compliant version strings using git tags
- Format: `<tag>` for tagged commits, `<tag>-post<N>` for N commits after tag

### Tools Module

`build_harness/tools/` contains utilities for:
- `git.py`: Git operations, tag extraction, version calculation
- `pep426.py`: Package name pattern matching
- `pep440.py`: Version string parsing and validation
- `pep503.py`: Package name normalization (PyPI)
- `pytest.py`: Pytest execution helpers

### Templates

`build_harness/templates/` contains cookiecutter templates for new projects:
- `cookiecutter.json`: Template configuration
- `hooks/pre_gen_project.py`: Pre-generation validation
- `hooks/post_gen_project.py`: Post-generation setup (git init, venv creation, first commit)
- `{{cookiecutter.project_slug}}/`: Project template structure

### Testing Structure

- `tests/ci/unit_tests/`: Fast unit tests (run in pre-commit hooks)
- `tests/ci/integration_tests/`: Slower integration tests
- `tests/manual/`: Manual testing utilities
- `features/`: Behave (BDD) feature files organized by test pyramid levels:
  - `1_strategy/`: High-level strategic tests
  - `2_scope/`: Scope definition tests
  - `3_structure/`: Structural tests
  - `4_skeleton/`: Skeleton/framework tests
  - `5_surface/`: Surface-level tests
- `features/steps/structure/`: Step implementations for BDD tests

## CI/CD Pipeline

The GitLab CI pipeline (`.gitlab-ci.yml`) has stages:
1. **setup**: Dependency validation and package debugging
2. **static-analysis**: Formatting checks, flake8, mypy (parallel across Python 3.9, 3.10, 3.11)
3. **package**: Build wheel and sdist
4. **tests**: Unit tests, integration tests, acceptance tests, coverage checks (parallel across Python versions)
5. **publish**: Publish to PyPI on semantic version tags

Pipeline configuration snippets are in `.gitlab-ci/*.yml`.

## Python Version Support

- Minimum: Python 3.9
- Tested on: 3.9, 3.10, 3.11
- Uses pyenv for managing multiple Python versions in CI

## Code Quality Standards

- **Line length**: 80 characters (synced across black, isort, flake8, ruff)
- **Coverage threshold**: 90% (enforced in CI and pre-commit hooks)
- **Formatting**: PEP-8 via black and isort
- **Type checking**: mypy with strict settings
- **Linting**: flake8 with plugins:
  - flake8-annotations (type annotation enforcement)
  - flake8-bandit (security checks)
  - flake8-bugbear (bug detection)
  - flake8-comprehensions (comprehension improvements)
  - flake8-docstrings (docstring validation)

## Pre-commit Hooks

The `.pre-commit-config.yaml` runs:
1. Dependency check (`install --check`)
2. Code formatting (isort + black)
3. Flake8 analysis
4. Mypy type checking
5. Unit tests (unit_tests directory only, not integration tests)
6. Coverage check (90% threshold, unit tests only)

## Important Files

- `pyproject.toml`: Project metadata, dependencies, tool configuration (PDM build backend)
- `.flake8`: Flake8 configuration
- `setup.cfg`: Additional tool configuration
- `.python-version`: Pyenv Python version specification
- `pdm.lock`: PDM lockfile for reproducible builds

## Development Notes

- The `build_harness/templates/` directory is excluded from formatting, linting, and type checking because it contains template files with cookiecutter variables
- Virtual environment is expected at `.venv/` in project root
- The project uses PDM for dependency management but provides `build-harness install` for abstraction
- Git version requirement: >= 2.28.0 (for `--initial-branch` support)
- Coverage runs with branch coverage and multiprocessing concurrency to avoid arc data conflicts
- Integration tests are slow and should not be run in pre-commit hooks

## Release Workflow

1. Ensure all tests pass and coverage meets threshold
2. Tag commit with semantic version (e.g., `1.2.3`)
3. CI pipeline detects tag and publishes to PyPI using `PYPI_API_TOKEN` secret
4. For non-tagged commits, `release-flow` generates post-release versions (e.g., `1.2.3-post5`)

## Package Manager Context

The project supports multiple package managers through abstraction:
- Currently official: PDM + GitLab CI
- Planned: Support for other package managers (Poetry, Pipenv) and CI tools (GitHub Actions)
- The `install` command abstracts away package manager specifics