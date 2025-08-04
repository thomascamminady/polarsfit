SHELL := /bin/bash

# Default Python executable
PYTHON := uv run python

# Phony targets
.PHONY: all setup install build dev test lint format check clean docs help
.PHONY: pre-commit update deps sync git remotegit coverage benchmark
.PHONY: rust-build rust-dev rust-clean

# Default target
all: setup build test lint

# Help target
help:
	@echo "Available targets:"
	@echo "  setup       - Initial project setup with dependencies"
	@echo "  install     - Install the package in development mode"
	@echo "  build       - Build the Rust extension and Python package"
	@echo "  dev         - Development setup (install + pre-commit)"
	@echo "  test        - Run stable tests (recommended for CI/development)"
	@echo "  test-all    - Run all tests (including experimental/flaky ones)"
	@echo "  lint        - Run linting (ruff check)"
	@echo "  format      - Format code (ruff format)"
	@echo "  check       - Run all checks (lint + type check)"
	@echo "  clean       - Clean build artifacts and caches"
	@echo "  docs        - Generate documentation"
	@echo "  coverage    - Run tests with coverage report"
	@echo "  benchmark   - Run benchmark tests"
	@echo "  pre-commit  - Run pre-commit hooks"
	@echo "  update      - Update dependencies"
	@echo "  sync        - Sync dependencies with lockfile"

# Setup and installation
setup: uv

uv:
	uv python install 3.11
	uv sync --all-extras
	uv tool install pre-commit
	uv tool install maturin

install: sync
	uv run maturin develop

build: install
	uv run maturin build --release

dev: install
	uvx pre-commit install
	uvx pre-commit autoupdate

# Testing targets
test:
	$(PYTHON) -m pytest tests/test_fit_performance_comparison.py tests/test_lazy_comprehensive.py tests/test_lazy_correctness.py tests/test_true.py tests/test_basic.py -v

test-all:
	$(PYTHON) -m pytest tests/ -v

test-fast:
	$(PYTHON) -m pytest tests/ -v -x --tb=short

test-adaptive:
	$(PYTHON) -m pytest tests/test_adaptive_multi_file.py -v -s

coverage:
	$(PYTHON) -m pytest tests/test_fit_performance_comparison.py tests/test_lazy_comprehensive.py tests/test_lazy_correctness.py tests/test_true.py tests/test_basic.py --cov=polarsfit --cov-report=html --cov-report=term

coverage-all:
	$(PYTHON) -m pytest tests/ --cov=polarsfit --cov-report=html --cov-report=term

benchmark:
	$(PYTHON) -m pytest tests/test_benchmark.py -v

# Code quality targets
lint:
	$(PYTHON) -m ruff check src/ tests/ scripts/

lint-fix:
	$(PYTHON) -m ruff check src/ tests/ scripts/ --fix

format:
	$(PYTHON) -m ruff format src/ tests/ scripts/

check: lint format
	@echo "✅ All checks passed!"

# Pre-commit and git
pre-commit:
	uvx pre-commit run --all-files

pre-commit-update:
	uvx pre-commit autoupdate

git:
	git init
	git lfs install
	uvx pre-commit autoupdate
	git add .
	uvx pre-commit run --all-files
	git commit -am "First commit after initializing the project."

remotegit:
	git branch -M main
	git remote add origin git@github.com:thomascamminady/polarsfit.git || true
	@echo "Attempting to push to remote repository..."
	@if git push -u origin main 2>/dev/null; then \
		echo "✅ Successfully pushed to GitHub!"; \
	else \
		echo "⚠️  Could not push to remote repository."; \
		echo "Please create the repository on GitHub first:"; \
		echo "https://github.com/new"; \
		echo "Repository name: polarsfit"; \
		echo "Then run: git push -u origin main"; \
	fi

# Documentation
docs:
	$(PYTHON) -m pdoc polarsfit --html --output-dir docs/

# Dependency management
update:
	uv lock --upgrade

sync:
	uv sync --all-extras

deps:
	@echo "📦 Dependency Information:"
	@echo "Python version: $(shell $(PYTHON) --version)"
	@echo "UV version: $(shell uv --version)"
	@$(PYTHON) -c "import polars as pl; print(f'Polars version: {pl.__version__}')"

# Rust specific targets
rust-build:
	cargo build --release

rust-dev:
	cargo build

rust-clean:
	cargo clean

# Cleaning targets
clean:
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf __pycache__/
	rm -rf target/
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
	@echo "🧹 Cleaned all build artifacts and caches"

# Utility targets
hello_world:
	uv run scripts/hello_world.py

# Development workflow
workflow: clean format lint test
	@echo "🎉 Development workflow completed successfully!"
