<!-- ═══════════════════════════════════════════════════════════════════════════ -->
<!-- Debian Gaming Setup Script — Pull Request Template                      -->
<!-- Version: 3.5.0                                                          -->
<!--                                                                         -->
<!-- Fill in all applicable sections. Remove sections that don't apply.      -->
<!-- PRs that skip the checklist or lack testing evidence may be delayed.    -->
<!-- ═══════════════════════════════════════════════════════════════════════════ -->

## Summary

<!-- One paragraph describing what this PR does and why. -->

## Type of Change

<!-- Check all that apply. -->

- [ ] 🐛 **Bug fix** — Non-breaking change that fixes an issue
- [ ] ✨ **New feature** — Non-breaking change that adds functionality
- [ ] 💥 **Breaking change** — Fix or feature that would cause existing functionality to change
- [ ] 🔒 **Security** — Security hardening, vulnerability fix, or audit remediation
- [ ] 📖 **Documentation** — Changes to docs, wiki, comments, or inline help only
- [ ] 🧪 **Tests** — Adding or updating tests (no production code changes)
- [ ] 🔧 **Refactor** — Code restructuring without changing behavior
- [ ] ⚡ **Performance** — Optimization without changing behavior
- [ ] 🏗️ **Infrastructure** — CI/CD, Makefile, pre-commit, packaging changes
- [ ] 🧹 **Chore** — Dependency updates, formatting, or housekeeping

## Related Issues

<!--
  Link to the issue(s) this PR addresses. Use "Fixes #N" to auto-close.
  
  Examples:
    Fixes #42
    Closes #15
    Related to #28
-->

- Fixes #

## Changes Made

<!--
  Describe the specific changes in this PR. Use bullet points for clarity.
  Group by file or component if touching multiple areas.
-->

### Code Changes

- 

### Documentation Changes

- 

### Test Changes

- 

## How It Works

<!--
  For non-trivial changes, explain the approach and design decisions.
  Include relevant architecture details, algorithm choices, or patterns used.
  Reference sync_function.md dependency chains if touching core methods.
-->

## Testing Evidence

<!--
  REQUIRED. Show that your changes work and don't break existing functionality.
  Include the output of `make check` or equivalent commands.
-->

### Automated Tests

```
$ make check
<paste output here>
```

### Manual Testing

<!--
  Describe any manual testing you performed. Include:
  - Distribution tested on
  - Specific scenarios verified
  - Edge cases checked
-->

| Test | Result |
|------|--------|
| `make lint` | ✅ / ❌ |
| `make test` (90 tests) | ✅ / ❌ |
| `make security` | ✅ / ❌ |
| `py_compile` | ✅ / ❌ |
| `bash -n` (launch_game.sh) | ✅ / ❌ |
| Anti-pattern grep | ✅ / ❌ |
| Manual dry-run test | ✅ / ❌ / N/A |

## Cascade Impact Analysis

<!--
  If modifying debian_gaming_setup.py, check sync_function.md for downstream
  dependencies. List all affected methods and confirm they still work.
  
  Skip this section for documentation-only or test-only changes.
-->

### Methods Modified

| Method | Line | Downstream Dependents |
|--------|------|-----------------------|
| | | |

### Methods Verified (Downstream)

- [ ] All downstream callers still function correctly
- [ ] No new cascading changes needed

## Screenshots / Output

<!--
  For UI-visible changes (terminal output, prompts, banners), show
  before/after comparisons. Use code blocks for terminal output.
-->

<details>
<summary>Before</summary>

```
<paste before output>
```

</details>

<details>
<summary>After</summary>

```
<paste after output>
```

</details>

## Security Considerations

<!--
  For code changes, briefly assess security implications.
  Skip for docs-only or test-only changes.
-->

- [ ] No new subprocess calls added (or justified below)
- [ ] No `shell=True`, `eval()`, or `exec()` introduced
- [ ] No hardcoded paths in `/tmp/` (uses `tempfile`)
- [ ] All `open()` calls include `encoding='utf-8'`
- [ ] All network `response.read()` calls are bounded
- [ ] No hardcoded credentials, tokens, or secrets
- [ ] All new exception handlers catch specific types
- [ ] N/A — Documentation, test, or infrastructure change only

## Documentation Updates

<!--
  Check all documentation that was updated as part of this PR.
  Per governance rules, code changes require all 4 tracking files updated.
-->

- [ ] `tasks/todo.md` — Plan updated
- [ ] `tasks/todo_complete.md` — Delivery logged
- [ ] `docs/CHANGELOG.md` — User-facing changelog entry
- [ ] `tasks/sync_function.md` — Code cross-reference updated
- [ ] `tasks/lessons.md` — New lessons added (if applicable)
- [ ] `docs/README.md` — Updated (if user-facing behavior changed)
- [ ] `docs/FAQ.md` — Updated (if new user questions anticipated)
- [ ] `wiki/` pages — Updated (if applicable)
- [ ] N/A — No documentation updates required

## Version Bump

<!--
  If this PR warrants a version bump, indicate the new version.
  Follow semver: MAJOR.MINOR.PATCH
    - PATCH: Bug fixes, docs
    - MINOR: New features, non-breaking enhancements
    - MAJOR: Breaking changes
-->

- [ ] Version bumped to: `_._._`
- [ ] `SCRIPT_VERSION` constant updated
- [ ] Header banner updated
- [ ] N/A — No version bump needed

## Reviewer Notes

<!--
  Anything specific you'd like reviewers to focus on, questions about
  implementation choices, or areas of uncertainty.
-->

## Pre-Submission Checklist

<!-- ALL items must be checked before submitting. -->

- [ ] I have read the [Contributing Guide](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/docs/CONTRIBUTING.md)
- [ ] I have read `tasks/general_reminders.md` (governance rules)
- [ ] I have read `tasks/lessons.md` (anti-patterns to avoid)
- [ ] My code follows the project's coding standards (Python 3.12+, no shell=True, specific exceptions)
- [ ] I have added/updated tests for my changes (if applicable)
- [ ] `make check` passes (lint + 90 tests + security)
- [ ] I have verified no existing functionality was removed or broken
- [ ] I have updated all required tracking files
- [ ] I have checked for these known bad patterns:
  - [ ] No `TIMEOUT_API0` (substring corruption artifact)
  - [ ] No `GPUType` (correct: `GPUVendor`)
  - [ ] No `RoyalHighgrass` (correct: `Sandler73`)
  - [ ] No `DadSchoworseorse` (correct: `DadSchoorse`)
