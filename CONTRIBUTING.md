<!-- ═══════════════════════════════════════════════════════════════════════════ -->
<!-- Debian Gaming Setup Script — Contributing Guide                         -->
<!-- Version: 3.5.0                                                          -->
<!-- ═══════════════════════════════════════════════════════════════════════════ -->

# Contributing to the Debian Gaming Setup Script

Thank you for your interest in contributing! This guide covers everything you need to know to make effective contributions to the project.

## Table of Contents

- [Ways to Contribute](#ways-to-contribute)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Project Architecture](#project-architecture)
- [Code Standards](#code-standards)
- [Security Requirements](#security-requirements)
- [Testing Requirements](#testing-requirements)
- [Documentation Standards](#documentation-standards)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)
- [Governance & Tracking](#governance--tracking)
- [Review Process](#review-process)
- [Release Process](#release-process)
- [Community Guidelines](#community-guidelines)
- [Recognition](#recognition)

---

## Ways to Contribute

There are many ways to contribute, regardless of your experience level:

| Contribution | Description | Skill Level |
|:---|:---|:---:|
| 🐛 **Bug Reports** | Report issues you encounter | Beginner |
| 📖 **Documentation** | Fix typos, improve guides, add examples | Beginner |
| 🧪 **Testing** | Test on your distro and report results | Beginner |
| ✨ **Feature Requests** | Suggest new features or improvements | Beginner |
| 💬 **Discussions** | Answer questions, help other users | Intermediate |
| 🔧 **Bug Fixes** | Fix reported issues | Intermediate |
| 🆕 **New Features** | Implement new functionality | Advanced |
| 🔒 **Security** | Security review, vulnerability fixes | Advanced |
| ⚡ **Performance** | Optimize code, reduce overhead | Advanced |
| 🏗️ **Infrastructure** | CI/CD, testing, packaging improvements | Advanced |

---

## Getting Started

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR-USERNAME/Debian-Gaming-Setup-Project.git
cd Debian-Gaming-Setup-Project
```

### 2. Install Development Dependencies

```bash
make install-dev
```

This installs pytest, pytest-cov, and pre-commit hooks. For security scanning tools:

```bash
make install-all-dev  # Includes Bandit
```

### 3. Verify Your Setup

```bash
make check  # Run all quality gates (lint + test + security)
```

All 90 tests must pass before you begin making changes.

### 4. Create a Branch

```bash
git checkout -b type/description
```

Use descriptive branch names:
- `fix/zorin-cpupower-detection`
- `feature/timeshift-integration`
- `docs/faq-waydroid-section`
- `test/mangohud-install-coverage`
- `infra/ci-performance-testing`

### 5. Read Project Context

Before making code changes, review these files:

| File | Purpose | Required Reading |
|:---|:---|:---:|
| `tasks/general_reminders.md` | Governance rules and workflow | ✅ Always |
| `tasks/lessons.md` | Anti-patterns and past mistakes | ✅ Always |
| `tasks/sync_function.md` | Code cross-reference and dependencies | ✅ For code changes |
| `tasks/audit_report.md` | Security audit findings | For security changes |
| `docs/SECURITY.md` | Security policy and model | For security changes |

---

## Development Environment

### Requirements

| Tool | Version | Purpose |
|:---|:---|:---|
| Python | 3.12+ | Runtime (uses StrEnum, slots, walrus, PEP 585/604) |
| pytest | 7.0+ | Testing framework |
| pytest-cov | 4.0+ | Coverage reporting |
| pre-commit | 3.0+ | Git hook management |
| Bandit | 1.7+ | Security scanning (optional) |
| GNU Make | 4.0+ | Build system |
| Bash | 5.0+ | Embedded script validation |

### Project Structure

```
debian-gaming-setup/
├── debian_gaming_setup.py          # Main script (5,764 lines, single file)
├── Makefile                        # 43 development targets
├── .pre-commit-config.yaml         # 4 pre-commit hooks
├── .gitignore                      # 170 exclusion patterns
├── LICENSE                         # MIT License
├── CONTRIBUTING.md                 # This file
├── CODE_OF_CONDUCT.md              # Contributor Covenant v2.1
├── .github/
│   ├── FUNDING.yml                 # Sponsor button configuration
│   ├── PULL_REQUEST_TEMPLATE.md    # PR template (13 sections)
│   ├── workflows/
│   │   └── ci.yml                  # CI/CD pipeline (4 jobs)
│   └── ISSUE_TEMPLATE/
│       ├── config.yml              # Template chooser
│       ├── bug_report.yml          # Bug report form
│       ├── feature_request.yml     # Feature request form
│       └── security_vulnerability.yml  # Security report form
├── tests/
│   ├── conftest.py                 # Shared fixtures
│   ├── test_unit_pure.py           # 42 unit tests
│   ├── test_integration.py         # 24 integration tests
│   └── test_security.py            # 24 security + host safety tests
├── docs/                           # User documentation (8 files)
├── wiki/                           # GitHub Wiki pages (13 files)
└── tasks/                          # Development tracking (8 files)
```

---

## Project Architecture

The script is a **single-file Python application** (zero external dependencies) centered on the `GamingSetup` class with 92+ methods. Key design principles:

### Single-File Design

The entire tool is one `.py` file by design — this enables zero-dependency deployment via `wget` and direct execution. Do not split into multiple modules.

### Key Code Patterns

1. **Pre-install detection before prompting** — Every install method must detect existing installations and show version information before asking the user to proceed.

2. **`run_command()` for all subprocess calls** — Never call `subprocess.run()` directly in install methods. Use the wrapper which provides logging, timeout, dry-run, and rollback recording.

3. **Version-aware prompts** — `prompt_install_or_update()` queries both APT and Flatpak for installed and available versions. Custom install methods should follow the same pattern.

4. **Dynamic resolution** — No hardcoded codenames, driver versions, or repository URLs. Everything is resolved at runtime.

5. **Rollback recording** — All install actions are auto-recorded via `_auto_record_from_command()`. New action types should be added to the `ActionType` enum.

### Dependency Cross-Reference

Before modifying any method, check `tasks/sync_function.md` for its callers and dependents. This prevents cascading breakage.

---

## Code Standards

### Python Requirements

| Requirement | Details |
|:---|:---|
| **Minimum version** | Python 3.12+ (enforced) |
| **Type hints** | PEP 585/604: `list[str]`, `dict[str, Any]`, `str \| None` |
| **Enums** | `StrEnum` (not `Enum`) for string enumerations |
| **Dataclasses** | `@dataclass(slots=True)` for data containers |
| **String formatting** | f-strings for print, `%`-formatting for logging |
| **Walrus operator** | Use `:=` where it improves clarity |
| **Imports** | Standard library only — zero external dependencies |
| **Encoding** | `encoding='utf-8'` on all text-mode `open()` calls |
| **Exceptions** | Specific types only — no bare `except:` or `except Exception` |
| **Docstrings** | Required on all public methods — descriptive, not stubs |

### Naming Conventions

| Element | Convention | Example |
|:---|:---|:---|
| Classes | PascalCase | `GamingSetup`, `SystemInfo` |
| Methods | snake_case | `install_steam`, `detect_gpu` |
| Private methods | `_` prefix | `_resolve_package_name`, `_install_ge_proton` |
| Constants | UPPER_SNAKE | `TIMEOUT_INSTALL`, `MAX_RESPONSE_BYTES` |
| Enums | PascalCase class, snake_case members | `GPUVendor.nvidia` |
| CLI flags | `--kebab-case` | `--ge-proton`, `--all-platforms` |

### Code Comments

All code must include:
- Descriptive docstrings on every public method
- Inline comments for non-obvious logic
- Section separators (`# ═══...`) for major code sections
- No stub docstrings (`"""...- """`) or placeholder comments

---

## Security Requirements

Security is non-negotiable. Every contribution must satisfy these constraints:

### Absolute Rules (Violations Block Merge)

| Rule | CWE | Rationale |
|:---|:---|:---|
| No `shell=True` in subprocess | CWE-78 | Command injection prevention |
| No `eval()` or `exec()` in Python | CWE-95 | Code injection prevention |
| No `eval` in embedded bash | CWE-95 | Code injection prevention |
| No hardcoded `/tmp/` paths | CWE-377 | Insecure temporary file prevention |
| No bare `except:` | CWE-755 | Improper exception handling |
| No hardcoded credentials | CWE-798 | Secret exposure prevention |
| All `response.read()` must be bounded | CWE-400 | Resource consumption prevention |
| All `open()` must specify `encoding` | — | Consistent text handling |

### Best Practices

- Use `tempfile.mkdtemp()` with `try/finally` cleanup for temp files
- Use `try/except FileNotFoundError` instead of check-then-act (TOCTOU prevention)
- Use `os.replace()` for atomic file writes (state, manifests)
- Verify SHA512 checksums for all downloaded archives
- Use `py_compile` validation before replacing script files

### Automated Security Checks

The CI/CD pipeline and pre-commit hooks automatically verify:
- `py_compile` syntax validation
- `bash -n` embedded script validation
- AST-based shell=True detection
- AST-based eval/exec detection
- Anti-hallucination pattern grep (4 known bad strings)
- Encoding parameter validation
- Deprecated import detection
- Bandit static security scan

---

## Testing Requirements

### Test Suite Structure

| File | Tests | Coverage |
|:---|:---:|:---|
| `test_unit_pure.py` | 42 | Pure functions: version parser, argparse, Color, Enums, dataclasses, constants |
| `test_integration.py` | 24 | Mocked subprocess/IO: run_command, package detection, file I/O, utilities |
| `test_security.py` | 24 | 13 static security (CWE-mapped) + 11 host safety runtime tests |

### Testing Rules

1. **All PRs must pass the full test suite** — `make check` (90 tests)
2. **New features require new tests** — At minimum, unit tests for pure logic and integration tests for methods with side effects
3. **No real system changes in tests** — All external calls must be mocked. Tests must be safe to run anywhere.
4. **Never hardcode SCRIPT_VERSION in assertions** — Use `gaming_module.SCRIPT_VERSION` dynamically
5. **Security tests are required** for any code touching subprocess, file I/O, or network

### Running Tests

```bash
make check         # Full quality gate (lint + test + security)
make test          # All 90 tests (verbose)
make test-unit     # Unit tests only (42)
make test-integration  # Integration tests only (24)
make test-security # Security + host safety tests (24)
make test-failed   # Re-run only previously failed tests
make coverage      # Tests with coverage report
```

---

## Documentation Standards

### Required Updates

Every code change must update these files (per governance rules):

| File | When to Update |
|:---|:---|
| `tasks/todo.md` | Always — mark items complete |
| `tasks/todo_complete.md` | Always — log delivery |
| `docs/CHANGELOG.md` | Always — user-facing changelog entry |
| `tasks/sync_function.md` | When code structure changes |
| `tasks/lessons.md` | When a new anti-pattern is discovered |

### Documentation Quality

- Markdown formatting consistent with existing docs
- Version references must match `SCRIPT_VERSION`
- No broken links — verify with `make docs-check`
- Wiki cross-links verified with `make docs-links`

---

## Commit Message Guidelines

### Format

```
type(scope): brief description

Longer explanation if needed (what, why, how).

Refs: #issue-number
```

### Types

| Type | Usage |
|:---|:---|
| `fix` | Bug fix |
| `feat` | New feature |
| `docs` | Documentation only |
| `test` | Adding or updating tests |
| `refactor` | Code restructuring (no behavior change) |
| `security` | Security hardening or fix |
| `perf` | Performance improvement |
| `infra` | CI/CD, Makefile, pre-commit, packaging |
| `chore` | Housekeeping, formatting |

### Examples

```
fix(codecs): add pre-install detection for multimedia packages

install_codecs() now checks 5 codec packages and displays installed
vs available versions before prompting the user.

Refs: #42
```

```
feat(uninstall): implement full --uninstall mode

Scans for all known gaming components (APT, Flatpak, GE-Proton,
configs), displays categorized inventory, removes in reverse
dependency order with confirmation gates.

Refs: #38
```

---

## Pull Request Process

### Before Submitting

1. **Run all quality gates:** `make check` (must pass)
2. **Run verification:** `make verify` (recommended)
3. **Check for anti-patterns:** Review `tasks/lessons.md`
4. **Update tracking files:** All 4 required files
5. **Bump version** (if warranted): Update `SCRIPT_VERSION` + header banner

### PR Template

The repository includes a [PR template](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/.github/PULL_REQUEST_TEMPLATE.md) with 13 sections. Key sections:

- **Testing Evidence** — `make check` output required
- **Cascade Impact Analysis** — Check `sync_function.md` for downstream effects
- **Security Considerations** — 8-point security checklist
- **Documentation Updates** — 4-file tracking requirement enforced
- **Pre-Submission Checklist** — 9 mandatory checks including 4 anti-pattern verifications

### Review Timeline

- Initial review: within 72 hours
- Follow-up reviews: within 48 hours
- Security-related PRs: prioritized for expedited review

---

## Issue Guidelines

Use the structured issue templates:

| Template | Use For |
|:---|:---|
| [🐛 Bug Report](https://github.com/Sandler73/Debian-Gaming-Setup-Project/issues/new?template=bug_report.yml) | Bugs, errors, unexpected behavior |
| [✨ Feature Request](https://github.com/Sandler73/Debian-Gaming-Setup-Project/issues/new?template=feature_request.yml) | New features, enhancements |
| [🔒 Security Vulnerability](https://github.com/Sandler73/Debian-Gaming-Setup-Project/security/advisories/new) | Security issues (use private reporting) |

For questions and general discussion, use [GitHub Discussions](https://github.com/Sandler73/Debian-Gaming-Setup-Project/discussions).

---

## Governance & Tracking

The project follows strict governance rules defined in `tasks/general_reminders.md`:

### Workflow

**Plan → Review → Execute → Validate → Record**

### 4-File Tracking Rule

Every change must update:

1. `tasks/todo.md` — Active plan
2. `tasks/todo_complete.md` — Delivery history
3. `docs/CHANGELOG.md` — User-facing changelog
4. `tasks/sync_function.md` — Code cross-reference (if code changed)

### Verification Checklist

Before any delivery:
- `python3 -m py_compile debian_gaming_setup.py` passes
- `bash -n` passes on extracted launch_game.sh
- `grep -E 'TIMEOUT_API0|GPUType|RoyalHighgrass|DadSchoworseorse'` finds nothing
- `make check` passes (lint + 90 tests + security)
- No removed functionality (unless explicitly approved)

---

## Review Process

### What Reviewers Check

1. **Correctness** — Does it work? Are edge cases handled?
2. **Security** — No new shell=True, eval, hardcoded secrets, or unsafe patterns
3. **Testing** — Are new features tested? Do existing tests still pass?
4. **Code quality** — PEP 8, proper type hints, descriptive names, good docstrings
5. **Documentation** — Are tracking files updated? Is the changelog entry clear?
6. **Cascade impact** — Are downstream methods unaffected?
7. **No functionality removal** — Changes must not break existing features

### Common Review Feedback

- "Missing encoding parameter on open()"
- "Add pre-install detection before the confirm prompt"
- "Use run_command() instead of direct subprocess.run()"
- "Update sync_function.md with the new method"
- "Test assertion hardcodes version — use gaming_module.SCRIPT_VERSION"

---

## Release Process

Releases are automated via the CI/CD pipeline:

1. Maintainer updates `SCRIPT_VERSION` and header banner
2. `make verify` passes
3. Commit and tag: `git tag v3.5.0 && git push origin v3.5.0`
4. CI validates tag matches `SCRIPT_VERSION`
5. GitHub Release is created automatically with the script attached

### Version Numbering (Semver)

| Bump | When |
|:---|:---|
| **PATCH** (x.x.1) | Bug fixes, documentation updates |
| **MINOR** (x.1.0) | New features, non-breaking enhancements |
| **MAJOR** (1.0.0) | Breaking changes (e.g., dropped Python 3.11 support) |

---

## Community Guidelines

All participants must follow the [Code of Conduct](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/CODE_OF_CONDUCT.md). In summary:

- Be respectful, inclusive, and constructive
- Focus on the work, not the person
- Accept feedback gracefully
- Ask questions — there are no dumb questions

---

## Recognition

Contributors are recognized in:
- Pull request merge messages
- CHANGELOG.md entries
- Release notes

We value all contributions — code, docs, testing, bug reports, and community support.

---

**Thank you for contributing to Linux gaming!** 🎮🐧
