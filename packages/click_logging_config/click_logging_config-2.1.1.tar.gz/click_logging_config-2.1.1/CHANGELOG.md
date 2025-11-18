# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Python PEP-440](https://peps.python.org/pep-0440/)
compliant parts of [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [2.1.0] - 2010-11-10

### Added

  - Optional rich-click support for enhanced CLI help formatting
    - Added rich-click>=1.8 as optional extra dependency
    - Automatic fallback to standard click if rich-click not installed
    - Install with: `pip install click-logging-config[rich-click]`

### Fixed

  - Bash conditionals in build_harness/scripts/publish-mode.sh
  - Bash conditionals in tests/ci/test-publish-packages.sh


## [2.0.2] - 2025-11-10

### Changed

  - Replaced build-harness with uv publish in CI/CD pipeline for simplified
    package publishing workflow


## [2.0.1] - 2025-11-10

### Added

  - publish-packages.sh script to encapsulate package publishing logic
  - publish-mode.sh script to determine publish mode based on git context
  - test-publish-packages.sh for testing publish package logic

### Fixed

  - Syntax error in .gitlab-ci/publish.yml
  - Output handling from publish-packages.sh script
  - Shebangs in local-build-image.sh and local-run-hadolint.sh scripts

### Changed

  - Refactored publish job scripting into dedicated build_harness scripts


## [2.0.0] - 2025-11-09

### Added

  - Python 3.13 and 3.14 support
  - Build harness scripts for improved CI/CD and local development workflows
    - build-packages.sh, check-formatting.sh, check-linting.sh
    - check-package-install.sh, define-venv-bin.sh, define-uv.sh
    - install-precommit-hooks.sh, logging.sh, set-python-release.sh
    - run-ci-tests.sh, run-ci-tests-coverage.sh, run-hadolint.sh, run-kaniko.sh
    - local-build-image.sh, local-run-hadolint.sh
  - Comprehensive logging infrastructure for build harness scripts
  - Test cleanup fixture to prevent logging handler accumulation across tests
  - mypy type checking to linting CI stage
  - Rust toolchain support in Docker build environment
  - .dockerignore file to optimize Docker build context
  - GitLab CI rule to only publish on semver-tagged releases

### Changed

  - BREAKING: Dropped support for EOL Python 3.8 and 3.9
  - BREAKING: Migrated from PDM to uv for package management
  - BREAKING: Updated to pydantic>=2 (migrated tests and code accordingly)
  - Updated to Python 3.14 as default Python version for CI
  - Updated dependencies:
    - click to 8.3
    - pytz to 2025.2
    - pendulum to 3.1
  - Updated hadolint to v2.14.0
  - Replaced deprecated click.BaseCommand with click.Command
  - Replaced .flake8 configuration with ruff
  - Updated Dockerfiles to use Python 3.14-slim base image
  - Improved CI/CD workflow with better diagnostics and logging
  - Enhanced test robustness by filtering non-JSON output in JSON-based tests

### Fixed

  - Console handler re-initialization bug causing duplicate handlers in 
    LoggingState.__set_console_logging()
  - Logging handler accumulation across pytest test runs
  - Missing before_script in install-check CI job causing venv initialization 
    failures
  - Non-PEP-440 compliant release IDs for untagged releases
  - Docker multi-stage build issues affecting multiple Python version support
  - Pre-commit hook removing all dev/doc/test dependencies during pip sync

### Removed

  - Support for Python 3.8 (EOL)
  - Support for Python 3.9 (EOL)
  - .flake8 configuration file (replaced with ruff)
  - pdm.lock file (replaced with uv.lock)
  - Obsolete .gitlab-ci/build_harness.yml configuration
  - Obsolete .gitlab-ci/pyenv.yml configuration
  - GCC dependency from Dockerfile (no longer needed)
  - Obsolete docker/ci/requirements-dev.txt
