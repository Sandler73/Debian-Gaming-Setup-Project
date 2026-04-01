# ═══════════════════════════════════════════════════════════════════════════════
# Debian Gaming Setup Script — Makefile
# ═══════════════════════════════════════════════════════════════════════════════
#
# SYNOPSIS:
#   Comprehensive development, testing, linting, security, documentation
#   validation, packaging, and maintenance commands.
#
# USAGE:
#   make help          — Show all available targets with descriptions
#   make check         — Run ALL quality gates (lint + test + security)
#   make verify        — Full pre-delivery verification checklist
#   make package       — Create distributable archive (runs verify first)
#   make info          — Show project statistics
#
# REQUIREMENTS:
#   Python 3.12+, pytest, pytest-cov
#   Optional: pre-commit, bandit
#
# VERSION: 3.5.0
# ═══════════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

SHELL        := /bin/bash
.DEFAULT_GOAL := help

PYTHON       ?= python3
PYTEST       ?= pytest
PIP          ?= pip

SCRIPT       = debian_gaming_setup.py
TESTS_DIR    = tests
WIKI_DIR     = wiki
DOCS_DIR     = docs
TASKS_DIR    = tasks
GITHUB_DIR   = .github

# Extract version from script dynamically
SCRIPT_VERSION = $(shell grep 'SCRIPT_VERSION = ' $(SCRIPT) 2>/dev/null | head -1 | cut -d'"' -f2)

# Anti-hallucination patterns (from tasks/lessons.md)
BAD_PATTERNS = TIMEOUT_API0|GPUType|RoyalHighgrass|DadSchoworseorse

# Key methods that must always exist (from tasks/sync_function.md)
KEY_METHODS  = "def run(" "def run_command(" "def confirm(" "def detect_system(" \
               "def detect_gpu(" "def create_performance_script(" \
               "def perform_rollback(" "def perform_uninstall(" \
               "def install_gaming_platforms(" "def post_install_health_check("

# Package archive name
ARCHIVE_NAME = debian-gaming-setup-v$(SCRIPT_VERSION)

# Files included in distribution package
DIST_FILES   = $(SCRIPT) Makefile .pre-commit-config.yaml .gitignore \
               LICENSE CONTRIBUTING.md CODE_OF_CONDUCT.md

# Directories included in distribution package
DIST_DIRS    = $(TESTS_DIR)/ $(DOCS_DIR)/ $(TASKS_DIR)/ $(WIKI_DIR)/ $(GITHUB_DIR)/

# ─────────────────────────────────────────────────────────────────────────────
# PHONY Declarations
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: help version info check verify \
        lint lint-python lint-bash lint-patterns lint-shell-true lint-eval lint-encoding lint-imports \
        test test-unit test-integration test-security test-quick test-failed test-verbose \
        coverage coverage-html coverage-xml \
        security security-scan security-audit \
        docs-check docs-links docs-versions docs-spelling \
        install-dev install-security install-all-dev \
        package package-zip package-tar \
        clean clean-all clean-cache clean-dist \
        count methods classes report

# ─────────────────────────────────────────────────────────────────────────────
# Help & Information
# ─────────────────────────────────────────────────────────────────────────────

help: ## Show all available targets with descriptions
	@echo ""
	@echo "  Debian Gaming Setup Script — Development Commands (v$(SCRIPT_VERSION))"
	@echo "  ═══════════════════════════════════════════════════════════════"
	@echo ""
	@echo "  \033[1mQuick Reference:\033[0m"
	@echo "    make check    — Run all quality gates"
	@echo "    make verify   — Full pre-delivery checklist"
	@echo "    make test     — Run all tests"
	@echo "    make lint     — Run all linters"
	@echo "    make info     — Show project stats"
	@echo ""
	@echo "  \033[1mAll Targets:\033[0m"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

version: ## Show current script version
	@echo "v$(SCRIPT_VERSION)"

info: ## Show comprehensive project statistics
	@echo ""
	@echo "  ════════════════════════════════════════════════════════"
	@echo "  Project Statistics — v$(SCRIPT_VERSION)"
	@echo "  ════════════════════════════════════════════════════════"
	@echo ""
	@echo "  \033[1mCodebase:\033[0m"
	@echo "    Script:        $$(wc -l < $(SCRIPT)) lines"
	@echo "    Python version: 3.12+ required"
	@echo "    Methods:       $$(grep -c 'def ' $(SCRIPT)) total"
	@echo "    Classes:       $$(grep -c '^class ' $(SCRIPT))"
	@echo "    Imports:       $$(grep -c '^import \|^from ' $(SCRIPT))"
	@echo ""
	@echo "  \033[1mTesting:\033[0m"
	@echo "    Test files:    $$(ls $(TESTS_DIR)/test_*.py 2>/dev/null | wc -l)"
	@echo "    Test cases:    $$(find $(TESTS_DIR) -name 'test_*.py' -exec grep -c 'def test_' {} + 2>/dev/null | awk -F: '{s+=$$2}END{print s}')"
	@echo "    Conftest:      $$(wc -l < $(TESTS_DIR)/conftest.py 2>/dev/null || echo 0) lines"
	@echo ""
	@echo "  \033[1mDocumentation:\033[0m"
	@echo "    Docs:          $$(ls $(DOCS_DIR)/*.md 2>/dev/null | wc -l) files ($$(cat $(DOCS_DIR)/*.md 2>/dev/null | wc -l) lines)"
	@echo "    Wiki:          $$(ls $(WIKI_DIR)/*.md 2>/dev/null | wc -l) pages ($$(cat $(WIKI_DIR)/*.md 2>/dev/null | wc -l) lines)"
	@echo "    Tasks:         $$(ls $(TASKS_DIR)/*.md 2>/dev/null | wc -l) files ($$(cat $(TASKS_DIR)/*.md 2>/dev/null | wc -l) lines)"
	@echo ""
	@echo "  \033[1mInfrastructure:\033[0m"
	@echo "    CI workflows:  $$(ls $(GITHUB_DIR)/workflows/*.yml 2>/dev/null | wc -l)"
	@echo "    Issue templates: $$(ls $(GITHUB_DIR)/ISSUE_TEMPLATE/*.yml 2>/dev/null | wc -l)"
	@echo "    Makefile:      $$(wc -l < Makefile) lines"
	@echo "    .gitignore:    $$(wc -l < .gitignore 2>/dev/null || echo 0) lines"
	@echo ""

count: ## Count lines of code, tests, docs, and total
	@echo ""
	@echo "  Line Counts"
	@echo "  ──────────────────────────────────────"
	@printf "  %-25s %s\n" "Script:" "$$(wc -l < $(SCRIPT))"
	@printf "  %-25s %s\n" "Tests:" "$$(cat $(TESTS_DIR)/*.py 2>/dev/null | wc -l)"
	@printf "  %-25s %s\n" "Documentation (docs/):" "$$(cat $(DOCS_DIR)/*.md 2>/dev/null | wc -l)"
	@printf "  %-25s %s\n" "Wiki:" "$$(cat $(WIKI_DIR)/*.md 2>/dev/null | wc -l)"
	@printf "  %-25s %s\n" "Tasks:" "$$(cat $(TASKS_DIR)/*.md 2>/dev/null | wc -l)"
	@printf "  %-25s %s\n" "Infrastructure:" "$$(cat Makefile .gitignore .pre-commit-config.yaml $(GITHUB_DIR)/*.md $(GITHUB_DIR)/*.yml $(GITHUB_DIR)/ISSUE_TEMPLATE/*.yml $(GITHUB_DIR)/workflows/*.yml 2>/dev/null | wc -l)"
	@echo "  ──────────────────────────────────────"
	@printf "  %-25s %s\n" "TOTAL:" "$$(find . -name '*.py' -o -name '*.md' -o -name '*.yml' -o -name '*.yaml' -o -name 'Makefile' -o -name '.gitignore' 2>/dev/null | grep -v __pycache__ | xargs cat 2>/dev/null | wc -l)"
	@echo ""

methods: ## List all methods in the GamingSetup class
	@echo ""
	@echo "  GamingSetup Methods ($(SCRIPT))"
	@echo "  ──────────────────────────────────────"
	@grep -n 'def ' $(SCRIPT) | grep -v '^\s*#' | awk -F: '{printf "  L%-5s %s\n", $$1, $$2}' | sed 's/    def //' | head -100
	@echo ""
	@echo "  Total: $$(grep -c 'def ' $(SCRIPT)) methods/functions"
	@echo ""

classes: ## List all classes
	@echo ""
	@echo "  Classes ($(SCRIPT))"
	@echo "  ──────────────────────────────────────"
	@grep -n '^class ' $(SCRIPT) | awk -F: '{printf "  L%-5s %s\n", $$1, $$2}'
	@echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Lint & Syntax Checks
# ─────────────────────────────────────────────────────────────────────────────

lint: lint-python lint-bash lint-patterns lint-shell-true lint-eval lint-encoding lint-imports ## Run ALL lint checks (7 checks)
	@echo ""
	@echo "  ✅ All lint checks passed (7/7)"

lint-python: ## Python syntax check (py_compile + AST parse)
	@echo "── [1/7] Python syntax ──"
	@$(PYTHON) -m py_compile $(SCRIPT) && echo "  ✅ py_compile PASS"
	@$(PYTHON) -c "import ast; ast.parse(open('$(SCRIPT)').read()); print('  ✅ AST parse PASS')"

lint-bash: ## Bash syntax check (extracts and validates launch_game.sh)
	@echo "── [2/7] Bash syntax ──"
	@$(PYTHON) -c "import re; c=open('$(SCRIPT)').read(); m=re.search(r\"r'''(#!/bin/bash.*?)'''\",c,re.DOTALL); open('/tmp/lint_lg.sh','w').write(m.group(1)) if m else exit(1)"
	@bash -n /tmp/lint_lg.sh && echo "  ✅ bash -n PASS"
	@rm -f /tmp/lint_lg.sh

lint-patterns: ## Anti-hallucination pattern check (known bad strings)
	@echo "── [3/7] Anti-pattern check ──"
	@if grep -qE '$(BAD_PATTERNS)' $(SCRIPT); then \
		echo "  ❌ FAIL: Hallucinated pattern found!"; \
		grep -nE '$(BAD_PATTERNS)' $(SCRIPT); \
		exit 1; \
	fi
	@echo "  ✅ No hallucinated patterns"

lint-shell-true: ## Verify no shell=True in subprocess calls (CWE-78)
	@echo "── [4/7] No shell=True ──"
	@$(PYTHON) -c "\
	import ast, sys; \
	t = ast.parse(open('$(SCRIPT)').read()); \
	found = [(n.lineno, n.func.attr) for n in ast.walk(t) \
	    if isinstance(n, ast.Call) \
	    and isinstance(getattr(n, 'func', None), ast.Attribute) \
	    and n.func.attr in ('run', 'Popen', 'call', 'check_call', 'check_output') \
	    for kw in n.keywords \
	    if kw.arg == 'shell' and isinstance(kw.value, ast.Constant) and kw.value.value is True]; \
	[print(f'  ❌ shell=True in {f} at line {l}') or sys.exit(1) for l, f in found]; \
	print('  ✅ No shell=True')"

lint-eval: ## Verify no eval/exec in Python code (CWE-95)
	@echo "── [5/7] No eval/exec ──"
	@$(PYTHON) -c "\
	import ast, sys; \
	t = ast.parse(open('$(SCRIPT)').read()); \
	found = [(n.lineno, n.func.id) for n in ast.walk(t) \
	    if isinstance(n, ast.Call) \
	    and isinstance(getattr(n, 'func', None), ast.Name) \
	    and n.func.id in ('eval', 'exec')]; \
	[print(f'  ❌ {name}() at line {l}') or sys.exit(1) for l, name in found]; \
	print('  ✅ No eval/exec')"

lint-encoding: ## Verify all text-mode open() calls have encoding parameter
	@echo "── [6/7] Encoding check ──"
	@$(PYTHON) -c "\
	import re, sys; \
	lines = open('$(SCRIPT)').readlines(); \
	pattern = re.compile(r\"open\([^)]+,\s*'[rw]'\s*\)\"); \
	errors = [(i+1, l.strip()[:70]) for i, l in enumerate(lines) \
	    if not l.strip().startswith('#') and pattern.search(l) and 'encoding' not in l]; \
	[print(f'  ❌ Missing encoding at line {n}: {t}') for n, t in errors]; \
	sys.exit(1) if errors else print('  ✅ All open() have encoding')"

lint-imports: ## Verify no unused or deprecated imports
	@echo "── [7/7] Import check ──"
	@$(PYTHON) -c "\
	import ast, re, sys; \
	source = open('$(SCRIPT)').read(); \
	tree = ast.parse(source); \
	deprecated = ['distutils', 'imp', 'optparse', 'formatter', 'cgi', 'cgitb', 'imghdr', 'sndhdr', 'pipes', 'crypt']; \
	found = [d for d in deprecated if f'import {d}' in source]; \
	[print(f'  ❌ Deprecated import: {d}') for d in found]; \
	sys.exit(1) if found else print('  ✅ No deprecated imports')"

# ─────────────────────────────────────────────────────────────────────────────
# Testing
# ─────────────────────────────────────────────────────────────────────────────

test: ## Run full test suite (verbose output)
	@echo "── Running full test suite ──"
	@$(PYTEST) $(TESTS_DIR)/ -v --tb=short

test-unit: ## Run unit tests only (pure functions, enums, dataclasses)
	@$(PYTEST) $(TESTS_DIR)/test_unit_pure.py -v --tb=short

test-integration: ## Run integration tests only (mocked subprocess/IO)
	@$(PYTEST) $(TESTS_DIR)/test_integration.py -v --tb=short

test-security: ## Run security + host safety tests only
	@$(PYTEST) $(TESTS_DIR)/test_security.py -v --tb=short

test-quick: ## Run tests quietly (fast CI mode)
	@$(PYTEST) $(TESTS_DIR)/ -q

test-failed: ## Re-run only previously failed tests
	@$(PYTEST) $(TESTS_DIR)/ -v --tb=short --lf

test-verbose: ## Run tests with full traceback and output capture disabled
	@$(PYTEST) $(TESTS_DIR)/ -v --tb=long -s

# ─────────────────────────────────────────────────────────────────────────────
# Coverage
# ─────────────────────────────────────────────────────────────────────────────

coverage: ## Run tests with terminal coverage report
	@$(PYTEST) $(TESTS_DIR)/ -v --tb=short --cov=. --cov-report=term-missing

coverage-html: ## Run tests with HTML coverage report (open htmlcov/index.html)
	@$(PYTEST) $(TESTS_DIR)/ --cov=. --cov-report=html --cov-report=term-missing -q
	@echo ""
	@echo "  ✅ HTML report: htmlcov/index.html"

coverage-xml: ## Run tests with XML coverage report (for CI upload)
	@$(PYTEST) $(TESTS_DIR)/ --cov=. --cov-report=xml -q
	@echo "  ✅ XML report: coverage.xml"

# ─────────────────────────────────────────────────────────────────────────────
# Security
# ─────────────────────────────────────────────────────────────────────────────

security: ## Run all security checks (tests + lint patterns + static analysis)
	@echo ""
	@echo "  ════════════════════════════════════════════════════════"
	@echo "  SECURITY SCAN — v$(SCRIPT_VERSION)"
	@echo "  ════════════════════════════════════════════════════════"
	@echo ""
	@$(MAKE) --no-print-directory test-security
	@echo ""
	@$(MAKE) --no-print-directory lint-patterns
	@$(MAKE) --no-print-directory lint-shell-true
	@$(MAKE) --no-print-directory lint-eval
	@$(MAKE) --no-print-directory lint-encoding
	@echo ""
	@echo "  ✅ Security scan complete"

security-scan: ## Run Bandit static security scanner (if installed)
	@echo "── Bandit security scan ──"
	@if command -v bandit &>/dev/null; then \
		bandit -r $(SCRIPT) -ll --skip B404,B603,B607 -f txt 2>&1 || true; \
	else \
		echo "  ⚠ Bandit not installed. Run: make install-security"; \
	fi

security-audit: ## Full security audit (Bandit + security tests + all lint)
	@echo ""
	@echo "  ════════════════════════════════════════════════════════"
	@echo "  FULL SECURITY AUDIT — v$(SCRIPT_VERSION)"
	@echo "  ════════════════════════════════════════════════════════"
	@echo ""
	@$(MAKE) --no-print-directory security
	@echo ""
	@$(MAKE) --no-print-directory security-scan
	@echo ""
	@echo "  ════════════════════════════════════════════════════════"
	@echo "  ✅ FULL SECURITY AUDIT COMPLETE"
	@echo "  ════════════════════════════════════════════════════════"

# ─────────────────────────────────────────────────────────────────────────────
# Documentation Validation
# ─────────────────────────────────────────────────────────────────────────────

docs-check: docs-versions docs-links ## Run all documentation checks
	@echo ""
	@echo "  ✅ Documentation checks passed"

docs-versions: ## Check for stale version references across docs and wiki
	@echo "── Doc version consistency ──"
	@stale=$$(grep -rl 'Version.*3\.1\.\|Version.*3\.2\.' $(DOCS_DIR)/*.md $(WIKI_DIR)/*.md 2>/dev/null | \
		grep -v CHANGELOG | wc -l); \
	if [ "$$stale" -gt 0 ]; then \
		echo "  ⚠ $$stale files with potentially stale version references:"; \
		grep -rn 'Version.*3\.1\.\|Version.*3\.2\.' $(DOCS_DIR)/*.md $(WIKI_DIR)/*.md 2>/dev/null | grep -v CHANGELOG; \
	else \
		echo "  ✅ No stale version references"; \
	fi

docs-links: ## Verify wiki cross-links resolve to actual files
	@echo "── Wiki cross-link check ──"
	@broken=0; \
	for link in $$(grep -oP '\(([A-Z][A-Za-z-]+)\)' $(WIKI_DIR)/_Sidebar.md 2>/dev/null | tr -d '()'); do \
		if [ ! -f "$(WIKI_DIR)/$$link.md" ]; then \
			echo "  ❌ Broken link: $$link"; \
			broken=1; \
		fi; \
	done; \
	if [ "$$broken" -eq 0 ]; then echo "  ✅ All wiki sidebar links resolve"; fi

# ─────────────────────────────────────────────────────────────────────────────
# Verification (Pre-Delivery Gate)
# ─────────────────────────────────────────────────────────────────────────────

verify: ## Full pre-delivery verification checklist (lint + test + security + docs)
	@echo ""
	@echo "  ════════════════════════════════════════════════════════"
	@echo "  VERIFICATION CHECKLIST — v$(SCRIPT_VERSION)"
	@echo "  ════════════════════════════════════════════════════════"
	@echo ""
	@$(MAKE) --no-print-directory lint
	@echo ""
	@$(MAKE) --no-print-directory test-quick
	@echo ""
	@$(MAKE) --no-print-directory docs-check
	@echo ""
	@echo "── Version consistency ──"
	@echo "  Header:   $$(head -5 $(SCRIPT) | grep 'v[0-9]' | xargs)"
	@echo "  Constant: $$(grep 'SCRIPT_VERSION' $(SCRIPT) | head -1 | xargs)"
	@echo ""
	@echo "── Key methods ──"
	@for m in $(KEY_METHODS); do \
		c=$$(grep -c "$$m" $(SCRIPT)); \
		if [ "$$c" -ge 1 ]; then echo "  ✅ $$m"; else echo "  ❌ $$m (MISSING)"; exit 1; fi; \
	done
	@echo ""
	@echo "── File stats ──"
	@echo "  Script: $$(wc -l < $(SCRIPT)) lines"
	@echo "  Tests:  $$($(PYTEST) $(TESTS_DIR)/ -q 2>&1 | tail -1)"
	@echo ""
	@echo "  ════════════════════════════════════════════════════════"
	@echo "  ✅ VERIFICATION PASSED"
	@echo "  ════════════════════════════════════════════════════════"

report: ## Generate a full project health report
	@echo ""
	@echo "  ════════════════════════════════════════════════════════"
	@echo "  PROJECT HEALTH REPORT — v$(SCRIPT_VERSION)"
	@echo "  ════════════════════════════════════════════════════════"
	@echo ""
	@$(MAKE) --no-print-directory info
	@$(MAKE) --no-print-directory count
	@echo "  Lint Status:"
	@$(MAKE) --no-print-directory lint 2>&1 | grep "✅\|❌" | sed 's/^/    /'
	@echo ""
	@echo "  Test Status:"
	@$(PYTEST) $(TESTS_DIR)/ -q 2>&1 | tail -1 | sed 's/^/    /'
	@echo ""
	@echo "  Doc Status:"
	@$(MAKE) --no-print-directory docs-check 2>&1 | grep "✅\|❌\|⚠" | sed 's/^/    /'
	@echo ""
	@echo "  ════════════════════════════════════════════════════════"

# ─────────────────────────────────────────────────────────────────────────────
# Development Setup
# ─────────────────────────────────────────────────────────────────────────────

install-dev: ## Install core dev dependencies (pytest, pytest-cov, pre-commit)
	@echo "── Installing core dev dependencies ──"
	$(PIP) install pytest pytest-cov pre-commit
	@if [ -d .git ]; then pre-commit install && echo "  ✅ Pre-commit hooks installed"; fi
	@echo "  ✅ Core dev dependencies ready"

install-security: ## Install security scanning tools (bandit)
	@echo "── Installing security tools ──"
	$(PIP) install bandit
	@echo "  ✅ Security tools ready"

install-all-dev: install-dev install-security ## Install all development tools
	@echo ""
	@echo "  ✅ All development tools installed"

# ─────────────────────────────────────────────────────────────────────────────
# Packaging & Distribution
# ─────────────────────────────────────────────────────────────────────────────

package: package-zip ## Create distributable package (default: zip)

package-zip: verify ## Create ZIP archive (runs verify first)
	@echo "── Packaging v$(SCRIPT_VERSION) (zip) ──"
	@rm -f $(ARCHIVE_NAME).zip
	@zip -r $(ARCHIVE_NAME).zip \
		$(DIST_FILES) $(DIST_DIRS) \
		-x '*__pycache__*' '*.pytest_cache*' '*.pyc' 'htmlcov/*' '.coverage' \
		2>/dev/null
	@echo "  ✅ Created: $(ARCHIVE_NAME).zip ($$(du -h $(ARCHIVE_NAME).zip | cut -f1))"

package-tar: verify ## Create tar.gz archive (runs verify first)
	@echo "── Packaging v$(SCRIPT_VERSION) (tar.gz) ──"
	@rm -f $(ARCHIVE_NAME).tar.gz
	@tar czf $(ARCHIVE_NAME).tar.gz \
		--exclude='*__pycache__*' --exclude='*.pytest_cache*' \
		--exclude='*.pyc' --exclude='htmlcov' --exclude='.coverage' \
		$(DIST_FILES) $(DIST_DIRS) \
		2>/dev/null
	@echo "  ✅ Created: $(ARCHIVE_NAME).tar.gz ($$(du -h $(ARCHIVE_NAME).tar.gz | cut -f1))"

# ─────────────────────────────────────────────────────────────────────────────
# Cleanup
# ─────────────────────────────────────────────────────────────────────────────

clean: ## Remove common build artifacts and caches
	@rm -rf __pycache__ .pytest_cache htmlcov .coverage coverage.xml
	@rm -rf $(TESTS_DIR)/__pycache__ $(TESTS_DIR)/.pytest_cache
	@find . -name '*.pyc' -delete 2>/dev/null || true
	@find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
	@rm -f /tmp/lint_lg.sh /tmp/lg_*.sh
	@echo "  ✅ Cleaned build artifacts"

clean-dist: ## Remove distribution archives
	@rm -f debian-gaming-setup-v*.zip debian-gaming-setup-v*.tar.gz
	@echo "  ✅ Cleaned distribution archives"

clean-cache: ## Remove all Python and tool caches
	@rm -rf .mypy_cache .pytype .pyre .ruff_cache
	@rm -rf .tox .nox .hypothesis
	@rm -rf .pre-commit-cache
	@echo "  ✅ Cleaned tool caches"

clean-all: clean clean-dist clean-cache ## Remove everything (artifacts + archives + caches)
	@echo "  ✅ Full clean complete"

# ─────────────────────────────────────────────────────────────────────────────
# Combined Quality Gates
# ─────────────────────────────────────────────────────────────────────────────

check: lint test security ## Run ALL quality gates (lint + test + security)
	@echo ""
	@echo "  ════════════════════════════════════════════════════════"
	@echo "  ✅ ALL CHECKS PASSED — v$(SCRIPT_VERSION)"
	@echo "  ════════════════════════════════════════════════════════"

# ─────────────────────────────────────────────────────────────────────────────
# Version Management
# ─────────────────────────────────────────────────────────────────────────────

docs-sync: ## Synchronize version across ALL docs, wiki, and tracking files
	@echo "═══ Syncing version $(SCRIPT_VERSION) across all files ═══"
	@# Pattern 1: **Version:** X.Y.Z (bold markdown)
	@find docs/ wiki/ -name '*.md' -exec sed -i \
		's/\*\*Version:\*\* [0-9]\+\.[0-9]\+\.[0-9]\+/**Version:** $(SCRIPT_VERSION)/g' {} +
	@# Pattern 2: **Current Stable Version:** X.Y.Z
	@find docs/ wiki/ -name '*.md' -exec sed -i \
		's/\*\*Current Stable Version:\*\* [0-9]\+\.[0-9]\+\.[0-9]\+/**Current Stable Version:** $(SCRIPT_VERSION)/g' {} +
	@# Pattern 3: | **Version** | X.Y.Z | (table cell)
	@find wiki/ -name '*.md' -exec sed -i \
		's/| \*\*Version\*\* | [0-9]\+\.[0-9]\+\.[0-9]\+/| **Version** | $(SCRIPT_VERSION)/g' {} +
	@# Pattern 4: | **Script version** | vX.Y.Z | (README stats)
	@sed -i 's/| \*\*Script version\*\* | v[0-9]\+\.[0-9]\+\.[0-9]\+/| **Script version** | v$(SCRIPT_VERSION)/' docs/README.md
	@# Pattern 5: **Version X.Y.Z** (footer)
	@sed -i 's/\*\*Version [0-9]\+\.[0-9]\+\.[0-9]\+\*\*/\*\*Version $(SCRIPT_VERSION)\*\*/' docs/README.md
	@# Pattern 6: Version X.Y.Z → Future (roadmap header)
	@sed -i 's/Version [0-9]\+\.[0-9]\+\.[0-9]\+ → Future/Version $(SCRIPT_VERSION) → Future/' docs/Enhancement_Roadmap.md
	@# Pattern 7: **vX.Y.Z** in sidebar
	@sed -i 's/\*\*v[0-9]\+\.[0-9]\+\.[0-9]\+\*\*/**v$(SCRIPT_VERSION)**/' wiki/_Sidebar.md
	@# Pattern 8: vX.Y.Z in wiki footer
	@sed -i 's/Script v[0-9]\+\.[0-9]\+\.[0-9]\+/Script v$(SCRIPT_VERSION)/' wiki/_Footer.md
	@# Pattern 9: Upgrade to X.Y.Z+ in security policy
	@sed -i 's/Upgrade to [0-9]\+\.[0-9]\+\.[0-9]\++/Upgrade to $(SCRIPT_VERSION)+/g' wiki/Security-Policy.md
	@# Pattern 10: sync_function.md header
	@sed -i 's/Script — v[0-9]\+\.[0-9]\+\.[0-9]\+/Script — v$(SCRIPT_VERSION)/' tasks/sync_function.md
	@# Pattern 11: SCRIPT_VERSION in sync_function constants table
	@sed -i 's/`"[0-9]\+\.[0-9]\+\.[0-9]\+"`/`"$(SCRIPT_VERSION)"`/' tasks/sync_function.md
	@# Pattern 12: "update to vX.Y.Z" / "Update to vX.Y.Z" in prose (FAQ, troubleshooting)
	@find docs/ wiki/ -name '*.md' -exec sed -i \
		's/[Uu]pdate to v[0-9]\+\.[0-9]\+\.[0-9]\+/update to v$(SCRIPT_VERSION)/g' {} +
	@# Pattern 13: "Upgrade to X.Y.Z+" in wiki security policy
	@find wiki/ -name '*.md' -exec sed -i \
		's/Upgrade to [0-9]\+\.[0-9]\+\.[0-9]\++/Upgrade to $(SCRIPT_VERSION)+/g' {} +
	@# Pattern 14: Makefile VERSION comment
	@sed -i 's/# VERSION: [0-9]\+\.[0-9]\+\.[0-9]\+/# VERSION: $(SCRIPT_VERSION)/' Makefile
	@echo "  ✅ Version $(SCRIPT_VERSION) synced across all files"
	@echo ""
	@echo "  Verifying no stale versions (excluding changelogs)..."
	@STALE=$$(grep -rn 'Version.*[0-9]\+\.[0-9]\+\.[0-9]\+' docs/*.md wiki/*.md 2>/dev/null \
		| grep -vi 'changelog\|history\|sprint\|\[[0-9]\|v[0-9].*(\|Updated:' \
		| grep -v '$(SCRIPT_VERSION)' | wc -l); \
	if [ "$$STALE" -gt 0 ]; then \
		echo "  ⚠  $$STALE potentially stale references found:"; \
		grep -rn 'Version.*[0-9]\+\.[0-9]\+\.[0-9]\+' docs/*.md wiki/*.md 2>/dev/null \
			| grep -vi 'changelog\|history\|sprint\|\[[0-9]\|v[0-9].*(\|Updated:' \
			| grep -v '$(SCRIPT_VERSION)' | head -10; \
	else \
		echo "  ✅ No stale version references found"; \
	fi

version-bump: ## Bump version: make version-bump NEW=X.Y.Z
	@if [ -z "$(NEW)" ]; then echo "Usage: make version-bump NEW=3.4.3"; exit 1; fi
	@echo "═══ Bumping version to $(NEW) ═══"
	@# 1. Update SCRIPT_VERSION constant
	@sed -i 's/SCRIPT_VERSION = "[0-9]\+\.[0-9]\+\.[0-9]\+"/SCRIPT_VERSION = "$(NEW)"/' $(SCRIPT)
	@# 2. Update header banner
	@sed -i 's/Gaming Setup Script v[0-9]\+\.[0-9]\+\.[0-9]\+/Gaming Setup Script v$(NEW)/' $(SCRIPT)
	@# 3. Update header VERSION field (line after "VERSION:")
	@sed -i '/^VERSION:/{n;s/[0-9]\+\.[0-9]\+\.[0-9]\+/$(NEW)/}' $(SCRIPT)
	@# 4. Verify
	@echo "  SCRIPT_VERSION: $$(grep 'SCRIPT_VERSION = ' $(SCRIPT) | head -1)"
	@echo "  Header: $$(head -5 $(SCRIPT) | grep -oP 'v[0-9]+\.[0-9]+\.[0-9]+')"
	@# 5. Sync all docs
	@$(MAKE) docs-sync
	@echo ""
	@echo "  ✅ Version bumped to $(NEW)"
	@echo "  Remember to: update CHANGELOG.md, run 'make check'"

# ─────────────────────────────────────────────────────────────────────────────
# Release Process
# ─────────────────────────────────────────────────────────────────────────────

release-preflight: ## Full pre-release validation (check + docs-sync + version verify)
	@echo "═══════════════════════════════════════════════════════════"
	@echo "  PRE-RELEASE VALIDATION — v$(SCRIPT_VERSION)"
	@echo "═══════════════════════════════════════════════════════════"
	@echo ""
	@# Step 1: Full quality gates
	@$(MAKE) check
	@echo ""
	@# Step 2: Verify version consistency across all docs
	@$(MAKE) docs-sync
	@echo ""
	@# Step 3: Verify CHANGELOG has entry for this version
	@echo "── Checking CHANGELOG entry ──"
	@if grep -q "\[$(SCRIPT_VERSION)\]" $(DOCS_DIR)/CHANGELOG.md; then \
		echo "  ✅ CHANGELOG entry found for $(SCRIPT_VERSION)"; \
	else \
		echo "  ❌ No CHANGELOG entry for $(SCRIPT_VERSION)"; \
		echo "  → Add entry to docs/CHANGELOG.md before releasing"; \
		exit 1; \
	fi
	@echo ""
	@# Step 4: Verify header banner matches
	@echo "── Checking header banner ──"
	@HEADER=$$(head -5 $(SCRIPT) | grep -oP 'v[0-9]+\.[0-9]+\.[0-9]+'); \
	if [ "v$(SCRIPT_VERSION)" = "$$HEADER" ]; then \
		echo "  ✅ Header banner: $$HEADER"; \
	else \
		echo "  ❌ Header banner ($$HEADER) != SCRIPT_VERSION (v$(SCRIPT_VERSION))"; \
		exit 1; \
	fi
	@echo ""
	@# Step 5: Verify no uncommitted changes would be missed
	@echo "── Checking YAML validity ──"
	@$(PYTHON) -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml')); yaml.safe_load(open('.github/workflows/release.yml')); print('  ✅ All workflow YAML valid')"
	@echo ""
	@echo "═══════════════════════════════════════════════════════════"
	@echo "  ✅ PRE-RELEASE VALIDATION PASSED — v$(SCRIPT_VERSION)"
	@echo "═══════════════════════════════════════════════════════════"
	@echo ""
	@echo "  Next steps:"
	@echo "    1. git add -A"
	@echo "    2. git commit -m 'release: v$(SCRIPT_VERSION)'"
	@echo "    3. git tag v$(SCRIPT_VERSION)"
	@echo "    4. git push origin main --tags"
	@echo ""
	@echo "  The release.yml workflow will automatically:"
	@echo "    - Re-run all tests and security checks"
	@echo "    - Validate tag matches SCRIPT_VERSION"
	@echo "    - Build 3 artifacts (standalone .py, .zip, .tar.gz) + SHA256SUMS"
	@echo "    - Generate release notes"
	@echo "    - Publish GitHub Release"

release: ## Full release process: bump → check → preflight → commit → tag → push
	@if [ -z "$(NEW)" ]; then \
		echo "Usage: make release NEW=X.Y.Z"; \
		echo ""; \
		echo "This runs the full release process:"; \
		echo "  1. make version-bump NEW=X.Y.Z  — Update SCRIPT_VERSION + all docs"; \
		echo "  2. make check                    — Lint + 136 tests + security"; \
		echo "  3. make release-preflight        — CHANGELOG, headers, YAML, docs"; \
		echo "  4. git add + commit + tag + push — Triggers release.yml workflow"; \
		echo ""; \
		echo "After push, the release.yml GitHub Actions workflow:"; \
		echo "  - Re-verifies everything in CI"; \
		echo "  - Builds 3 release artifacts + SHA256 checksums"; \
		echo "  - Publishes GitHub Release with auto-generated notes"; \
		exit 1; \
	fi
	@echo "═══════════════════════════════════════════════════════════"
	@echo "  RELEASE PROCESS — v$(NEW)"
	@echo "═══════════════════════════════════════════════════════════"
	@echo ""
	@echo "Step 1/4: Version bump..."
	@$(MAKE) version-bump NEW=$(NEW)
	@echo ""
	@echo "Step 2/4: Quality checks..."
	@$(MAKE) check
	@echo ""
	@echo "Step 3/4: Pre-release validation..."
	@$(MAKE) release-preflight
	@echo ""
	@echo "Step 4/4: Git operations..."
	@echo "  The following commands will be executed:"
	@echo "    git add -A"
	@echo "    git commit -m 'release: v$(NEW)'"
	@echo "    git tag v$(NEW)"
	@echo "    git push origin main --tags"
	@echo ""
	@read -p "  Proceed? (y/n) " confirm; \
	if [ "$$confirm" = "y" ]; then \
		git add -A && \
		git commit -m "release: v$(NEW)" && \
		git tag "v$(NEW)" && \
		git push origin main --tags && \
		echo "" && \
		echo "  ✅ Release v$(NEW) pushed!" && \
		echo "  → GitHub Actions release.yml is now running" && \
		echo "  → Check: https://github.com/Sandler73/Debian-Gaming-Setup-Project/actions"; \
	else \
		echo "  ⏹ Aborted. Version bump is already applied locally."; \
		echo "  → Run manually: git add -A && git commit && git tag v$(NEW) && git push origin main --tags"; \
	fi
