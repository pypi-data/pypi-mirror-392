# Makefile for argparse-utils-tddschn
# Targets: build, publish, bump, format, test, lint, check, release

SHELL := /bin/bash
PYTHON ?= python
VENV := .venv
ACTIVATE := source $(VENV)/bin/activate || true
TYPE ?= patch

.DEFAULT_GOAL := help

.PHONY: help install-dev build publish bump-patch bump-minor bump-major bump format test lint check release clean

help:
	@echo "Available make targets:"
	@echo "  build        Build sdist and wheel (python -m build)"
	@echo "  publish      Upload distributions to PyPI using uvx twine (uses dist/*)"
	@echo "  bump         Bump package version (bump2version). Usage: make bump type=patch|minor|major"
	@echo "  bump-patch   Convenience: bump2version patch"
	@echo "  bump-minor   Convenience: bump2version minor"
	@echo "  bump-major   Convenience: bump2version major"
	@echo "  format       Format sources using ruff (ruff format src tests)"
	@echo "  lint         Run ruff in check mode (ruff check src tests)"
	@echo "  test         Run pytest"
	@echo "  check        lint + test + build"
	@echo "  release      Bump -> build -> publish. Example: make release type=minor"
	@echo "  clean        Remove build artifacts"

install-dev:
	@echo "Installing project in editable mode with dev dependencies..."
	$(ACTIVATE) && $(PYTHON) -m pip install -e .[dev]

build:
	@echo "Building source and wheel distributions..."
	$(ACTIVATE) && $(PYTHON) -m build

publish: build
	@echo "Publishing dist/* to PyPI via uvx twine..."
	uvx twine upload dist/*

test:
	@echo "Running tests..."
	$(ACTIVATE) && pytest

format:
	@echo "Formatting source files with ruff..."
	ruff format src tests

lint:
	@echo "Checking formatting/lint with ruff..."
	ruff check src tests

bump-patch:
	@echo "Bumping patch version..."
	bump2version patch

bump-minor:
	@echo "Bumping minor version..."
	bump2version minor

bump-major:
	@echo "Bumping major version..."
	bump2version major

bump:
	@echo "Bumping version with type: $(TYPE)"
	bump2version $(TYPE)

bump-dry:
	@echo "Preview version bump (dry-run). Use type=patch|minor|major"
	@echo "Note: adds --dry-run so this won't commit or tag"
	bump2version --dry-run $(TYPE)

release: bump build publish
	@echo "Release completed. Consider pushing tags and commits if bump2version created them."

check: lint test build

clean:
	rm -rf build dist *.egg-info
	@echo "Cleaned build artifacts"
