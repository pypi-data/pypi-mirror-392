# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]


## [3.0.1] - 2025-11-16

### Added

- Run `twine check` during publish dryrun

### Fixed

- Older version of twine rejecting current Python package metadata


## [3.0.0] - 2025-11-15

### Added

- CLAUDE.md documentation for AI coding assistants
- Ruff configuration for modern Python linting
- Container tool discovery (nerdctl, docker, podman) in invoke tasks
- .dockerignore file for Docker CI builds
- Test fixture for logging handler cleanup to prevent test contamination

### Changed

- Updated to click-logging-config 2.1.1 or higher
- Updated Docker base image to python:3.14-slim
- Updated Docker container dependencies: libcurl4 and related APT packages
- Consolidated tool configuration into pyproject.toml (mypy, pydocstyle)
- Updated dependencies: black (24.4.2+), mypy (1.10+), wheel (0.43.0+),
  twine (5.1.0+), pip (<25)
- Enhanced GitLab CI conditional logic documentation

### Removed

- Python 3.8 and 3.9 support (end of life)
- Click dependency now transitive via click-logging-config

### Fixed

- Flake8 compatibility with version 7.3 and higher
- Test isolation issues with logging handlers between test runs


## [2.5.0] - 2024-06-11

### Added

- SonarCloud integration for code quality analysis
- Support for configurable virtual environment in cookiecutter templates
- Gated publish workflow that depends on test outcomes

### Changed

- Updated dependencies: pydantic, flake8, sphinx, pytest, pre-commit
- Updated click-logging-config dependency to resolve pendulum transitive
  dependency issue

### Fixed

- SonarCloud job stage configuration
- Docker image venv initialization within pyenv environment


## [2.4.0] - 2023-12-31

### Added

- Python 3.9, 3.10, 3.11 support in CI pipeline
- Install template check job to verify template integrity
- Package debug job for troubleshooting CI builds

### Changed

- Migrated to PEP-621 compliant pyproject.toml format
- Updated Python version management using pyenv
- Reorganized Docker image build with split APT requirements
- Updated dependencies: black, isort, mypy, pip, curl, wget

### Removed

- Python 3.7 support (end of life)
- Python 3.12 temporary support removal due to pendulum dependency conflicts
- Upper bound constraint on requires-python version

### Fixed

- Package version acquisition logic
- Dockerfile escaping and quote handling
- Install check validation
- Raw regex string formatting for Python 3.12 compatibility


## [2.3.0] - 2023-08-13

### Added

- Support for Flit PEP-621 pyproject.toml format
- Enhanced git repository testing

### Changed

- Updated flake8 and related dependencies
- Improved Dockerfile linting with allowed failures for dependency pinning

### Fixed

- Flake8 C419 errors for list comprehension usage
- Git release ID resolution in Dockerfile
- Shell variable quoting in CI scripts
- Project slug substitution in Flit GitLab CI tests


## [2.2.0] - 2022-12-22

### Added

- Automatic project_slug generation from project_name in templates

### Changed

- Reorganized Flit configuration within pyproject.toml
- Enhanced cookiecutter post-generation hook for GitLab CI

### Fixed

- Template variable substitution for project_name and project_slug


## [2.1.1] - 2022-12-21

### Changed

- Moved coverage threshold configuration to pyproject.toml
- Updated click_logging_config to version 0.2.1 or higher

### Fixed

- Template build-harness version range specification
- Publish flow logging default configuration


## [2.1.0] - 2022-11-11

### Removed

- Standalone pydocstyle analysis (now integrated via flake8-docstrings plugin)


## [2.0.0] - 2022-11-11

### Changed

- Integrated click_logging_config for unified logging configuration
- Enhanced logging with version information at startup
- Added configurable log level via CI variables
- Code formatting improvements

### Removed

- Obsolete GitLab CI job variables

### Fixed

- Multiline command handling in CI scripts


## [1.1.0] - 2022-11-11

### Changed

- Integrated click_logging_config for unified logging configuration
- Enhanced logging with version information at startup
- Added configurable log level via CI variables
- Code formatting improvements

### Removed

- Obsolete GitLab CI job variables

### Fixed

- Multiline command handling in CI scripts


## [1.0.8] - 2022-11-09

### Removed

- Automatic VERSION file deletion during package build


## [1.0.7] - 2022-11-08

### Changed

- Configured Git strategy and depth settings for GitLab CI

### Fixed

- Variable formatting in error messages
- Stack trace reporting for better debugging


## [1.0.6] - 2022-11-08

### Added

- Project metadata classifiers for PyPI
- Default branch argument support in release-flow and publish-flow templates

### Changed

- Enhanced error reporting for release-flow utility
- Reorganized logging module location


## [1.0.5] - 2022-10-22

### Changed

- Code cleanup: removed unused imports

### Fixed

- Logging configuration for publish-flow and release-flow utilities


## [1.0.4] - 2022-08-18

### Changed

- Updated cookiecutter to version 2.1.1 or higher
- Updated Flit build-system to support version 4
- Required Git version 2.28 or higher for --initial-branch support

### Fixed

- Bootstrap command default branch handling in integration tests
- Project template dependency version specifications


## [1.0.3] - 2022-08-11

### Added

- Flake8 plugins: annotations, bandit, bugbear, comprehensions, docstrings

### Changed

- Relocated Dockerfile to docker/ci/ directory
- Updated maintainer email address
- Standardized line length to 80 characters across all tools
- Renamed internal module from _project to project

### Removed

- Standalone pydocstyle analysis (replaced by flake8-docstrings)
- Redundant template CI tasks

### Fixed

- Default branch name handling in various test scenarios
- Path handling for macOS temporary files and directories


## [1.0.2] - 2022-04-07

### Changed

- Relaxed dependency version constraints to allow floating updates


## [1.0.1] - 2022-04-01

### Added

- `--disable-pr-publish` option for publish-flow utility

### Changed

- Updated dependencies: mypy (0.942+), black (22.3+)
- Relaxed dependency version constraints to allow updates
- Hard-coded dry-run behavior for non-release publishes

### Fixed

- Main branch publishing to test PyPI
- PEP-440 dev suffix validation
- Acceptance test module naming
- Byte string output formatting


## [1.0.0] - 2022-02-05

### Changed

- Updated GitPython to version 3.1.24 or higher
- Relocated Dockerfile directory
- Reverted to GitLab stock runners
- Updated Git version requirements
- Relaxed dependency version constraints


## [0.2.1] - 2021-09-23

### Changed

- Updated GitPython to version 3.1.24 or higher (security update)
- Relocated Dockerfile directory
- Reverted to GitLab stock runners
- Relaxed dependency version constraints


## [0.2.0] - 2021-07-24

### Added

- Bootstrap command for initializing new projects from templates
- publish-flow utility for determining when to publish artifacts
- Console status prompts for formatting and static analysis
- Semantic version compliant post-release suffix format
- Docker image dependency caching for faster CI builds
- Cookiecutter template system for project generation

### Changed

- Enhanced coverage reporting with console output option
- Updated GitLab CI workflow with publish command substitution
- Implemented hadolint Dockerfile linting
- Updated package dependencies
- Optimized CI pipeline performance with custom runners
- Enhanced logging configuration

### Fixed

- Git tools module relocation
- Project dependency installation in templates
- Post-release ID formatting


## [0.1.1] - 2021-05-13

### Added

- Documentation for maintaining coverage thresholds

### Changed

- Improved error handling for missing pyproject.toml files
- Enhanced README with release identity and git tagging strategy
- Expanded installation instructions
- Moved flit from dev to runtime dependencies

### Removed

- Obsolete setup.cfg behave default_tags configuration

### Fixed

- Misplaced twine dependency (moved to runtime)
- CLI argument help text formatting


## [0.1.0] - 2021-03-12

### Added

- Core build-harness CLI with subcommands: formatting, static-analysis,
  unit-test, acceptance, install, package, publish
- release-flow command for calculating PEP-440 compliant release IDs from
  git history
- BDD acceptance testing support using behave
- Project dependency management with automatic virtual environment creation
- Unit test execution with pytest
- Coverage reporting (console, HTML, XML, JUnit)
- Static code analysis with flake8, black, isort
- Package building and publishing to PyPI via flit
- Pre-commit hook integration
- GitLab CI pipeline configuration

### Changed

- Established project structure and core architecture
- Configured development tooling (black, isort, flake8, mypy)
- Set minimum Python version to 3.7
- Organized tests into CI sub-packages

### Fixed

- Static analysis error reporting
- Click command documentation strings
- Test discovery and execution


## [0.0.0] - 2020-08-20

### Added

- Initial project structure with MIT license
