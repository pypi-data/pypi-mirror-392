.PHONY: help install install-dev test test-unit test-integration test-cov lint format type-check check clean build publish publish-test version-patch version-minor version-major

# Default target
help:
	@echo "Available targets:"
	@echo "  make install          - Install package in editable mode"
	@echo "  make install-dev      - Install package with dev dependencies"
	@echo "  make test             - Run all tests"
	@echo "  make test-unit        - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make test-cov         - Run tests with coverage report"
	@echo "  make lint             - Run ruff linter"
	@echo "  make format           - Format code with ruff"
	@echo "  make type-check       - Run mypy type checker"
	@echo "  make check            - Run all checks (lint, format-check, type-check, test)"
	@echo "  make clean            - Remove build artifacts and cache files"
	@echo "  make build            - Build wheel and source distribution"
	@echo "  make publish-test     - Publish to TestPyPI"
	@echo "  make publish          - Publish to PyPI"
	@echo "  make version-patch    - Bump patch version (0.1.0 -> 0.1.1)"
	@echo "  make version-minor    - Bump minor version (0.1.0 -> 0.2.0)"
	@echo "  make version-major    - Bump major version (0.1.0 -> 1.0.0)"

# Installation
install:
	uv pip install -e .

install-dev:
	uv pip install -e ".[dev]"

# Testing
test:
	uv run pytest

test-unit:
	uv run pytest -m unit

test-integration:
	uv run pytest -m integration

test-cov:
	uv run pytest --cov=src/pytennisscorer --cov-report=term-missing --cov-report=html

# Code Quality
lint:
	uv run ruff check .

format:
	uv run ruff format .

format-check:
	uv run ruff format --check .

type-check:
	uv run mypy src/pytennisscorer

# Run all checks (useful for CI or pre-commit)
check: lint format-check type-check test

# Cleaning
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete

# Building
build: clean
	uv build

build-wheel:
	uv build --wheel

build-sdist:
	uv build --sdist

# Publishing
publish-test: build
	uv publish --publish-url https://test.pypi.org/legacy/

publish: build
	@echo "WARNING: This will publish to PyPI. Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]
	uv publish

# Version management (manual - update pyproject.toml version)
version-patch:
	@echo "Current version: $$(grep '^version = ' pyproject.toml | cut -d'"' -f2)"
	@echo "Please update version manually in pyproject.toml (patch: X.Y.Z -> X.Y.Z+1)"

version-minor:
	@echo "Current version: $$(grep '^version = ' pyproject.toml | cut -d'"' -f2)"
	@echo "Please update version manually in pyproject.toml (minor: X.Y.Z -> X.Y+1.0)"

version-major:
	@echo "Current version: $$(grep '^version = ' pyproject.toml | cut -d'"' -f2)"
	@echo "Please update version manually in pyproject.toml (major: X.Y.Z -> X+1.0.0)"
