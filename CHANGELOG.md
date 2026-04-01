# Changelog

All notable changes to the Debian-Based Gaming Setup Script will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [3.5.0] - 2026-03-26

### Changed 🔧
- **LICENSE expanded to 311 lines** — Comprehensive legal framework modeled on industry-standard templates: 10 sections covering warranty disclaimer (9 sub-clauses), limitation of liability (10 damage categories), indemnification, user responsibility (6 duties), authorized use, third-party dependencies (with actual project dependency list), no obligation of support, modifications/contributions, termination, and governing law/severability

### Fixed 🐛
- **Documentation staleness** — README "What's New" section was frozen at v3.4.2 while SCRIPT_VERSION was at v3.4.4. Updated to show all versions through v3.4.4
- **Inline version references** — FAQ and troubleshooting prose contained outdated "update to vX.Y.Z" instead of current version. Fixed and added Pattern 12–14 to `docs-sync` to catch these going forward
- **CI/CD essential file paths** — Corrected to standard root locations (LICENSE, CONTRIBUTING.md, CODE_OF_CONDUCT.md)

### Improved 📈
- **`docs-sync` Makefile target** — Added 3 new patterns (12–14): inline prose "update to vX.Y.Z" references, wiki security policy upgrade refs, and Makefile VERSION comment. Now covers 14 distinct version patterns
- **README "What's New"** — Restructured to show v3.4.0 through v3.4.4 with key highlights for each

---

## [3.4.4] - 2026-03-26

### Fixed 🐛
- **Node.js 20 deprecation warnings** — All GitHub Actions upgraded from v4/v5 (Node 20) to v6 (Node 24): `actions/checkout@v6`, `actions/setup-python@v6`, `actions/upload-artifact@v6`. Eliminates all deprecation warnings before the June 2026 forced migration

### Added ✨
- **8th lint check: f-string logging** — CI now detects and blocks multiline f-string logging calls (the pattern that caused the v3.4.1 runtime TypeError)
- **Test count regression guard** — CI verifies ≥136 tests exist; blocks if test cases are accidentally removed
- **Subprocess timeout verification** — CI uses AST analysis to verify every `subprocess.run()` has a `timeout` parameter
- **Full release workflow** — Triggered by version tags (`v*`): runs pre-release test verification, verifies tag matches `SCRIPT_VERSION`, creates ZIP + tar.gz + standalone archives, generates release notes with install instructions and statistics, publishes GitHub Release
- **Pipeline summary** — New `summary` job writes a formatted results table to `GITHUB_STEP_SUMMARY` for every run

### Improved 📈
- **CI/CD pipeline** — 7 → 8 jobs, ~620 → 698 lines, 43 → 49 steps
- **Lint checks** — 7 → 8 (added f-string logging detection)
- **Security job** — Added subprocess timeout verification step
- **Release job** — Pre-release test re-run, 3 archive formats (zip + tar.gz + standalone .py), auto-generated release notes with statistics

---

## [3.4.3] - 2026-03-26

### Fixed 🐛
- **CI test failure: `test_install_vm_tools_detects_existing`** — Test did not mock `shutil.which` or `run_command`, causing real `vmware-toolbox-cmd` and `apt-get` execution on GitHub Actions Ubuntu runners. Added proper mocks for both
- **README CI/CD badge broken** — GitHub-native `badge.svg` URL returns 404 until first workflow run; replaced with shields.io static badge that always renders

### Added ✨
- **Wiki: Launcher Guide** — Exhaustive documentation of the `launch-game.sh` performance launcher: creation process, all features (CPU governor, GameMode, MangoHud, Flatpak resolution, Steam handling, signal cleanup), configuration, and troubleshooting (~290 lines)
- **Wiki: Setup Guide** — Complete setup documentation covering system requirements, download methods, first run, dry-run mode, presets, development environment, full Makefile reference (43 targets across 9 categories), pre-commit hooks, testing, project structure, updating, and uninstalling (~310 lines)
- **Makefile `version-bump` target** — Single command (`make version-bump NEW=X.Y.Z`) updates SCRIPT_VERSION, header banner, VERSION field, and syncs all docs/wiki version references automatically
- **Makefile `docs-sync` target** — Synchronizes version string across 11 distinct patterns in docs, wiki, and tracking files with stale-reference verification
- **Wiki: Expanded Home page** — Full feature overview, navigation tables, support links (~110 lines, was 54)
- **Wiki: Sidebar updated** — Added Setup Guide and Launcher Guide navigation links

### Improved 📈
- **Wiki sidebar** — 2 new pages: Setup Guide, Launcher Guide
- **Bash shield clarified** — Added HTML comment explaining it represents the embedded `launch-game.sh`

---

## [3.4.2] - 2026-03-26

### Fixed 🐛
- **GE-Proton checksum fails in dry-run mode** — Checksum verification attempted to read the downloaded tarball even in `--dry-run` mode where wget didn't actually execute, causing `FileNotFoundError`. Now skips checksum verification in dry-run with an informational message
- **Health Check Summary lacks detail** — Summary section showed counts only ("Warnings: 3") without listing WHAT the warnings/failures were. Now collects specific details during each check and displays them with `→` arrows under the warning/failure count in the summary

---

## [3.4.1] - 2026-03-26

### Fixed 🐛
- **RUNTIME BUG: Mixed %-format/f-string logging** — `logging.info("...%s " f"{var}")` at line 1892 would cause `TypeError: not enough arguments for format string` when system detection ran. Converted to proper `logging.info("...%s %s", var1, var2)` format
- **AMD GPU false detection** — `'ati'` substring in lspci matched `'compatible'` present in every VGA output line (`VGA compatible controller`), causing Intel GPUs to be misidentified as AMD and potentially receiving wrong drivers. Fixed with word-boundary-safe patterns (`' ati '`, `'[ati]'`, `'ati/'`)
- **Multiarch `:i386` version display** — `install_essential_packages()` and `perform_uninstall()` stripped `:i386` suffix before querying dpkg/apt-cache, reporting incorrect versions for 32-bit packages. Removed stripping since dpkg and apt-cache natively support multiarch qualifiers

### Improved 📈
- **f-string logging elimination** — All 20 f-string logging calls (9 single-line from v3.2.0 + 11 multiline discovered in this audit) converted to lazy `%`-formatting for proper log-level filtering and performance
- **os.chown safety** — 2 unprotected `os.chown` call groups (GE-Proton file ownership loop, vkBasalt config ownership) wrapped in `try/except (OSError, PermissionError)` with warning logging
- **Atomic state file write** — `save_installation_state()` now uses temp-file + `os.replace()` atomic pattern (matching `save_rollback_manifest()`)
- **Test suite expanded** — 90 → 136 tests; new `test_extended_integration.py` with 46 tests covering package management, detection (GPU/VM/distro), prompts, state management, maintenance, system safety, and install methods. Critical method coverage raised from 19% to 100% (26/26 methods)

---

## [3.4.0] - 2026-03-25

### Added ✨
- **GitHub Sponsors funding configuration** — `.github/FUNDING.yml` (86 lines) with GitHub Sponsors active and 7 additional platforms documented as placeholders
- **Issue templates** — 3 YAML form-based templates: bug report (239 lines, 20 fields), feature request (180 lines, 13 fields), security vulnerability (197 lines, 13 fields) plus template chooser config with Discussions and private Security Advisory links
- **Pull request template** — `.github/PULL_REQUEST_TEMPLATE.md` (217 lines) with 13 sections, testing evidence table, cascade impact analysis, security gate, and 4 anti-pattern checks
- **Comprehensive .gitignore** — 353 lines, 170 patterns across 9 sections (Python, testing, venvs, packaging, docs, IDEs, OS, secrets, project-specific)
- **MIT LICENSE** — Full MIT License with explicit liability limitation and warranty disclaimer clauses
- **CONTRIBUTING.md** — Comprehensive contribution guide with code standards, PR process, security rules, and governance references
- **CODE_OF_CONDUCT.md** — Contributor Covenant v2.1 adapted with project-specific enforcement details

### Changed 🔧
- **Makefile expanded** — 482 lines → 43 targets across 9 categories: 7 lint checks (added encoding + imports), docs validation, security audit with Bandit, project health report, multi-format packaging (zip + tar.gz), coverage variants (HTML + XML), test-failed/test-verbose modes, clean variants, install-security
- **In-code annotations updated** — Header VERSION corrected to 3.4.0, REQUIREMENTS section added, 11 stub docstrings replaced, 6 stale "Exact same" fragments fixed, "— NEW" section labels cleaned, --uninstall usage examples added
- **All documentation updated** — 8 docs/ files and 13 wiki pages updated to v3.4.0 with new feature references, expanded FAQ, uninstall documentation

### Improved 📈
- **CI/CD pipeline expanded** — Added performance and security testing jobs, Bandit integration, coverage upload, expanded Python version matrix
- **Test suite expanded** — 90 → 136 tests (+46); new `test_extended_integration.py` with 46 tests covering 14 test classes; critical method coverage raised from 19% to 100% (26/26 methods)
- **Atomic state file write** — `save_installation_state()` now uses temp-file + `os.replace()` pattern matching `save_rollback_manifest()` to prevent corruption on crash
- **f-string logging converted** — 9 f-string logging calls converted to lazy `%`-formatting for proper log-level filtering

### Fixed 🐛
- **AMD GPU false detection** — `'ati'` substring in lspci matched `'compatible'` in every VGA line, causing Intel GPUs to be misidentified as AMD; fixed with word-boundary-safe patterns (`' ati '`, `'[ati]'`, `'ati/'`)
- **Multiarch `:i386` version display** — Removed unnecessary `.replace(":i386","")` stripping from `install_essential_packages()` and `perform_uninstall()`; dpkg and apt-cache natively support multiarch qualifiers
- **Stale version references** — SECURITY.md and Quick_Start.md updated from 3.3.0 to 3.4.0

---

## [3.3.0] - 2026-03-25

### Added ✨
- **Full `--uninstall` mode** — Scans for all installed gaming components (APT packages, Flatpak apps, GE-Proton, config files), displays categorized inventory with versions, then removes in reverse dependency order (Flatpak → APT → GE-Proton → configs → state) with confirmation gates at each stage
- **Flatpak available version querying** — `get_flatpak_available_version()` queries Flathub remote for latest version; `check_flatpak_updates_available()` compares installed vs available
- **OS support table in README** — 10 distributions with version, status, and notes

### Fixed 🐛
- **ZorinOS "no installation candidate"** — `_check_package_available()` now uses `apt-cache policy` instead of `apt-cache show`, verifying the Candidate field is not `(none)` before declaring a package available
- **VM Tools missing available version** — Pre-detection now queries and displays available version alongside installed version, with update/up-to-date/unknown status

### Changed 🔧
- **Version-aware prompts for all install methods** — `prompt_install_or_update()` now queries both APT and Flatpak sources for available versions, displays source type (APT/Flatpak), installed version, available version, and "Up to date" confirmation for every component
- **Essential packages pre-detection** — `install_essential_packages()` now shows which packages are already installed with current and available versions before prompting, distinguishes between missing and up-to-date packages
- **Codec per-package versioning** — `install_codecs()` now shows installed vs available version for each codec sub-package (ubuntu-restricted-extras, GStreamer plugins, FFmpeg, libavcodec-extra) and lists missing packages with available versions
- **README.md comprehensive rewrite** — Dynamic CI/CD badge from GitHub Actions, OS support table, uninstall documentation, updated project stats
- **All documentation updated** — 8 docs/ files, 13 wiki pages updated to v3.3.0

---

## [3.2.0] - 2026-03-25

### Fixed 🐛
- **System upgrade hang** — `update_system()` now uses `TIMEOUT_UPDATE` (600s) for the upgrade step, adds `--force-confold` and `--force-confdef` dpkg options to prevent interactive configuration prompts that caused indefinite hangs, and logs warnings with stderr content on non-zero exit
- **Missing upgrade logging** — `run_command()` now logs stdout/stderr at DEBUG level for all commands (success and failure), enabling troubleshooting of silent failures
- **GE-Proton pre-detection missing from prompt** — Existing GE-Proton versions are now displayed before the install/update prompt in `install_gaming_platforms()`, not just inside `_install_ge_proton()`

### Changed 🔧
- **Codec pre-install detection** — `install_codecs()` now checks 5 common codec packages (ubuntu-restricted-extras, gstreamer plugins, ffmpeg, libavcodec-extra) and displays which are already installed before prompting
- **Flatpak update checking** — `prompt_install_or_update()` now queries available versions for both APT (`get_available_version`) and Flatpak (`get_flatpak_available_version`) sources, displaying current version, available version, source type (APT/Flatpak), and "Up to date" confirmation
- **New method: `get_flatpak_available_version()`** — Queries Flathub remote for latest available version without downloading
- **New method: `check_flatpak_updates_available()`** — Compares installed vs available Flatpak versions
- **MangoHud update checking** — `install_mangohud()` now shows available version and distinguishes between update/reinstall
- **Mumble update checking** — `install_mumble()` now shows available version and distinguishes between update/reinstall
- **Dual-source detection** — Lutris, Discord, and OBS Studio prompts now pass both `package_name` and `flatpak_id` for comprehensive APT+Flatpak detection
- **Makefile rewrite** — Comprehensive 157-line Makefile with 18 targets: help, version, info, lint (5 sub-targets), test (5 sub-targets), coverage, security, verify, install-dev, package, clean, check

---

## [3.1.0] - 2026-03-23

### Added ✨
- **Automated test suite** — 90 tests across 3 modules: unit (42 tests), integration (24 tests), security & host safety (24 tests)
- **CI/CD pipeline** — GitHub Actions workflow with 4 jobs: lint, test (Python 3.12 + 3.13 matrix), security scan (Bandit), and automated release on version tags
- **Pre-commit hooks** — `.pre-commit-config.yaml` with py_compile, bash syntax check, anti-pattern grep, and no-shell-true validation
- **Makefile** — 9 development targets: `make test`, `make lint`, `make security`, `make check`, `make clean`, and sub-targets
- **Security test coverage** — Static analysis tests for CWE-78 (command injection), CWE-95 (eval injection), CWE-377 (temp files), CWE-400 (unbounded reads), CWE-367 (TOCTOU), CWE-755 (missing handlers), CWE-798 (hardcoded secrets)
- **Host safety tests** — Validates dry-run mode, confirmation requirements, no curl|bash patterns, SHA512 verification, tempfile module usage

---

## [3.0.0] - 2026-03-23

### ⚠️ Breaking Changes
- **Python 3.12+ required** — Minimum Python version raised from 3.7 to 3.12. The script now uses StrEnum, dataclass slots, walrus operators, and PEP 585/604 type hints that require Python 3.12+.

### Security 🔒
- **Bounded network reads** — All `response.read()` calls now enforce a 1MB size limit (`MAX_RESPONSE_BYTES`) to prevent memory exhaustion from oversized API responses
- **Secure temporary files** — GE-Proton downloads and Waydroid script now use `tempfile.mkdtemp()` instead of predictable `/tmp/` paths, preventing symlink attacks on multi-user systems
- **Guaranteed temp cleanup** — All temporary file operations wrapped in `try/finally` blocks ensuring cleanup even on unexpected exceptions
- **Eliminated eval in launcher** — `launch_game.sh` cleanup handler replaced `eval "$task"` pattern with direct function calls using `GOVERNOR_RESTORE_METHOD` variable
- **TOCTOU race condition fixes** — Three check-then-act patterns (`os.path.exists` → `os.remove`) replaced with atomic `try/except FileNotFoundError`

### Added ✨
- **Comprehensive security audit report** — `tasks/audit_report.md` with STRIDE threat model, CWE/SANS Top 25 mapping, and 25 classified findings
- **`MAX_RESPONSE_BYTES` constant** — 1MB network read limit for defense-in-depth

### Fixed 🐛
- **Missing JSONDecodeError handler** — `perform_update()` GE-Proton version check now catches `json.JSONDecodeError`, preventing unhandled crash on malformed API responses
- **Stale version in header** — Script header banner synced with `SCRIPT_VERSION`

### Changed 🔧 (Python 3.12+ Modernization)
- **Type hints** — Replaced `typing.Optional`, `List`, `Dict`, `Tuple` with native `X | None`, `list[]`, `dict[]`, `tuple[]` (PEP 585/604)
- **StrEnum** — Converted 5 string-valued Enums (`GPUVendor`, `VMType`, `DistroFamily`, `InstallationPhase`, `ActionType`) from `Enum` to `StrEnum` (PEP 659)
- **Dataclass slots** — Added `slots=True` to `SystemInfo`, `HardwareInfo`, `BackupEntry`, `RollbackAction` for memory efficiency
- **Walrus operator** — Applied 16 `:=` conversions across regex matches, environ lookups, and package resolution patterns
- **removeprefix** — Replaced `.lstrip()` single-char prefix removals with `.removeprefix()` (3 sites)
- **Logging performance** — Converted 70 f-string logging calls to lazy %-formatting for deferred evaluation
- Removed unused imports (`grp`, `time`) and added `tempfile`
- Added explicit `encoding='utf-8'` to all text-mode `open()` calls

---

## [2.6.0] - 2026-02-19

### Added ✨
- **Pre-install detection for 7 methods** — `install_vm_tools()`, `_install_ge_proton()`, `install_mangohud()`, `install_goverlay()`, `install_vkbasalt()`, `install_mumble()`, and `install_mod_managers()` now check for existing installations before prompting, reporting version info and offering reinstall/skip
- **VM tools version detection** — Per-VM-type binary checks (`vmware-toolbox-cmd -v`, `VBoxClient`, `qemu-guest-agent`, etc.) with version reporting
- **GE-Proton version comparison** — Scans `~/.steam/root/compatibilitytools.d/` for existing versions, compares with latest GitHub release, skips download if already up to date
- **Flatpak-aware command resolver in launch_game.sh** — `resolve_command()` function maps known app names (lutris, heroic, discord) to their Flatpak run commands when native binaries aren't found
- **launch_game.sh `--help` / `-h` flag** — Comprehensive inline usage documentation with supported launchers, examples, and enhancement descriptions
- **LAUNCHER_GUIDE.md** — Standalone documentation for the performance launcher covering all features, Flatpak resolution, Steam per-game config, environment variables, and troubleshooting
- **FAQ.md** — Comprehensive standalone FAQ with 50+ entries across 12 categories (General, Installation, GPU/Drivers, Gaming Platforms, Performance, Compatibility, Maintenance, Troubleshooting, Waydroid, Advanced, Security, Contributing)

### Fixed 🐛
- **Lutris URI error** (`[''] is not a valid URI`) — Empty arguments no longer passed to Flatpak apps; conditional array expansion prevents URI parsing failures
- **Heroic Games Launcher "command not found"** — Flatpak resolution maps `heroic` to `flatpak run com.heroicgameslauncher.hgl`
- **launch_game.sh `LAUNCH_CMD` array handling** — Resolved commands split into proper arrays via `read -ra` for correct `exec` behavior with multi-word Flatpak commands
- **Hallucinated vkBasalt GitHub URL** — `DadSchoworseorse` corrected to `DadSchoorse` (verified)

### Changed 🔄
- **launch_game.sh rewritten** — Now 239 lines (was 170); includes Flatpak resolver, `--help` flag, improved argument handling, `RESOLVED_CMD`/`LAUNCH_CMD` split
- **Pre-install check consistency** — All installation methods now follow the same detection pattern, aligning with existing `prompt_install_or_update()` behavior used by Steam, Lutris, Heroic, Wine, Discord, OBS, SOBER, Waydroid, and GWE

---

## [2.5.0] - 2026-02-17

### Security 🔒
- **Eliminated all `shell=True` subprocess calls** — Codecs installation now uses `subprocess.run(input=)` for debconf pipe and list-form for apt commands, preventing command injection
- **Fixed all bare `except` clauses** — 10 generic `except Exception` handlers replaced with specific types (`OSError`, `IOError`, `json.JSONDecodeError`, `subprocess.SubprocessError`, etc.); 1 documented outermost catch-all retained in `run()`
- **Waydroid secure install** — Replaced `curl -fsSL | bash` with a download-then-execute pattern that validates the downloaded script has a valid shebang before running

### Added ✨
- **`ensure_flatpak_ready()` method** — Single cached method for Flatpak/Flathub setup, replacing 7 duplicate blocks throughout the codebase with session-level caching
- **SIGTERM/SIGINT signal handling** — `_setup_signal_handlers()` registered in `__init__`, saves installation state and rollback manifest before clean exit on termination signals
- **Post-install health check** — `post_install_health_check()` verifies APT packages, key binaries (steam, lutris, wine, mangohud, gamemoded), Flatpak apps, and GPU drivers (NVIDIA via nvidia-smi, AMD via lsmod amdgpu) after installation completes
- **Categorized timeout constants** — 6 named constants (`TIMEOUT_QUICK` 5s, `TIMEOUT_NETWORK` 10s, `TIMEOUT_API` 15s, `TIMEOUT_DOWNLOAD` 120s, `TIMEOUT_INSTALL` 300s, `TIMEOUT_UPDATE` 600s) replacing 24 magic numbers throughout the codebase

### Fixed 🐛
- **Performance launcher (`launch-game.sh`) multilib issues** — Complete rewrite resolving 4 bugs:
  - `libgamemodeauto.so.0` "wrong ELF class" error: GameMode now validates library presence via `ldconfig -p` before enabling
  - MangoHud `/usr/$LIB/mangohud/libMangoHud.so` preload failure: Uses `MANGOHUD=1` env var (Vulkan implicit layer) instead of LD_PRELOAD
  - Steam 32-bit subprocess conflicts: Steam launched without `gamemoderun` wrapper; users directed to per-game Steam Launch Options
  - Missing MangoHud config: Script creates default `~/.config/MangoHud/MangoHud.conf` if absent
  - Added argument validation, cleanup trap, CPU governor save/restore, and `set -euo pipefail`

### Statistics 📊
- Lines of code: 4,955 (+404 from v2.4.0)
- Methods: 89 (+3 new)
- CLI arguments: 54
- Documentation: 3,000+ lines across 7 files

---

## [2.4.0] - 2026-02-17

### Added ✨
- **`--update` mode** — Reads `installation_state.json` to identify previously installed components, checks APT package versions for available upgrades, runs Flatpak updates, and detects newer GE-Proton releases from GitHub API
- **`--self-update` mechanism** — Queries the GitHub API for the latest release tag, compares using semantic version parsing (handles v-prefix, hyphens, varying parts), downloads new script, validates syntax via `py_compile`, backs up current version as `.v{version}.backup`, and replaces atomically via `os.replace()`
- **`--preset` configuration** — 4 named presets (`minimal`, `standard`, `complete`, `streaming`) that map to `InstallationConfig` flag combinations; presets overlay non-destructively onto explicit CLI flags so you can combine them
- **`--check-requirements` system pre-check** — Validates disk space (5 GB min / 10 GB warn), RAM (2 GB min), architecture (x86_64/amd64 expected), dpkg lock status, and Python version; also runs automatically at start of `run()`
- **`_preflight_packages()` validation** — Checks package availability via `apt-cache show` before batch installs, splitting lists into available/unavailable and skipping missing packages cleanly; integrated into `install_essential_packages()`
- **`_parse_version()` utility** — Semantic version comparison handling `v` prefix, hyphenated suffixes, and varying part counts

### Statistics 📊
- Lines of code: 4,551 (+627 from v2.3.0)
- Methods: 86
- CLI arguments: 54

---

## [2.3.0] - 2026-02-17

### Added ✨
- **Action-based rollback engine** — Every reversible operation records its reversal command via `record_action()`, with 7 action types: `apt_install`, `flatpak_install`, `repo_add`, `file_create`, `file_modify`, `sysctl_write`, `ge_proton_install`
- **Rollback manifest persistence** — Versioned JSON manifest (`rollback_manifest.json`) saved atomically (temp file + `os.replace()`) after every recorded action, survives script crashes and restarts
- **Rollback execution engine** — `perform_rollback()` loads manifest, filters successful reversible actions, displays grouped summary by type, offers dry-run preview showing exact commands, processes actions in LIFO order, and archives manifest after completion (not deleted — audit trail preserved)
- **Auto-recording hook** — `_auto_record_from_command()` injected into `run_command()` detects `apt-get install` and `flatpak install` calls, automatically recording packages for rollback without modifying individual install methods
- **Per-package state tracking** — `save_installation_state()` builds per-package inventory (APT packages, Flatpak apps, created files, added repos, failed operations) from rollback actions
- **GE-Proton SHA512 checksum verification** — Downloads `.sha512sum` asset from GitHub releases, parses hash, computes local SHA512, aborts on mismatch with user override option
- **6 convenience recording methods** — `_record_package_install()`, `_record_flatpak_install()`, `_record_repo_add()`, `_record_file_create()`, `_record_file_modify()`, and manual `record_action()` calls for sysctl configs, Wine repos, vkBasalt config, and performance launcher
- **`RollbackAction` dataclass** and **`ActionType` enum** — Structured types for rollback system with 9 fields and 7 action categories

### Statistics 📊
- Lines of code: 3,924 (+686 from v2.2.0)
- Methods: 79
- Rollback action types: 7

---

## [2.2.0] - 2026-02-16

### Added ✨
- **Dynamic distribution codename resolution** — 7-step fallback chain resolving codenames for any Debian/Ubuntu derivative: `UBUNTU_CODENAME` → `VERSION_CODENAME` for Ubuntu → derivative mapping table (Mint→Ubuntu, Elementary→Ubuntu, Zorin→Ubuntu) → `VERSION_ID` mapping → Debian-to-Ubuntu mapping → `ID_LIKE` fallback → empty string
- **Dynamic GPU driver detection** — NVIDIA drivers resolved via `ubuntu-drivers devices` (Ubuntu family) or `apt-cache search` (Debian), never hardcoded; AMD firmware-aware for Debian non-free repos; Intel Arc GPU support detection
- **Distro-aware package name resolution** — `_resolve_package_name()` and `_check_package_available()` handle package naming differences across Ubuntu, Debian, Mint, and derivatives (e.g., `ubuntu-restricted-extras` vs `mint-meta-codecs`)
- **Wine repository URL validation** — HTTP HEAD request verifies WineHQ sources file exists before adding repository; Debian and Ubuntu URL paths resolved separately
- **Network connectivity checking** — `check_network_connectivity()` tests reachability of distro-appropriate endpoints before remote operations
- **Interactive/targeted flow control** — `_is_interactive_mode()` determines whether to prompt for everything (no flags) or install only flagged components; replaced broken `or True` conditionals

### Fixed 🐛
- **Broken `or True` conditionals** — Config flags were short-circuited by `or True` in several places, making CLI flags ineffective. Replaced with proper `_is_interactive_mode()` check.

### Statistics 📊
- Lines of code: 3,238 (+?? from v2.1.0, integrated enhancement)
- Methods: 68

---

## [2.1.0] - 2026-01-05

### Added ✨
- **SOBER (Roblox on Linux)** - Full Roblox platform support via Flatpak
  - Smart installation with version checking
  - Automatic Flatpak setup
  - `--sober` CLI flag
- **Waydroid (Android Container)** - Run Android apps and mobile games
  - Wayland/X11 session detection
  - Automatic repository setup
  - Post-install instructions provided
  - `--waydroid` CLI flag
- **GreenWithEnvy (GWE)** - NVIDIA GPU control and monitoring
  - GPU vendor detection
  - Overclocking and fan control support
  - `--gwe` CLI flag
- **vkBasalt** - Vulkan post-processing layer (ReShade-like)
  - Automatic configuration file generation
  - CAS, FXAA, and other effects
  - Toggle key support (Home key default)
  - `--vkbasalt` CLI flag
- **ReShade Setup Information** - Comprehensive ReShade guidance for Linux
  - Multiple implementation options explained
  - Offers vkBasalt installation
  - `--reshade` CLI flag
- **Mod Manager Tools** - Game modding setup assistance
  - Mod Organizer 2 (via Lutris)
  - Vortex Mod Manager information
  - r2modman installation
  - `--mod-managers` CLI flag

### Fixed 🐛
- **Ubuntu 24.04 Compatibility**
  - Changed `linux-cpupower` to `linux-tools-generic` (package name fix)
  - Enhanced error handling for optional packages
  - Fallback logic for missing packages
- **MangoHud Installation on Ubuntu 24.04**
  - Added version detection before PPA usage
  - Default repository installation for Ubuntu 24.04+
  - PPA only used for older Ubuntu versions
  - Better error messages and manual installation guidance
- **Repository Cleanup**
  - Enhanced `clean_broken_repos()` to handle MangoHud PPAs
  - Automatic backup before removal
  - Both Lutris and MangoHud PPA cleanup

### Changed 🔄
- **--all-platforms flag** - Now excludes specialized platforms (SOBER, Waydroid)
- **Installation summary** - Added new tools (SOBER, GWE, vkBasalt, Waydroid)
- **Error handling** - Improved graceful degradation across all new features
- **Configuration system** - Added 6 new boolean flags to InstallationConfig

### Statistics 📊
- Lines of code: 3,341 (+414 from v2.0.1)
- CLI arguments: 51+ (+11 new flags)
- Major features: 33 (+8 new additions)
- Documentation: 2,700+ lines

---

## [2.0.1] - 2026-01-04

### Fixed 🐛
- **Ubuntu 24.04 Package Issues**
  - Fixed `linux-cpupower` package name (changed to `linux-tools-generic`)
  - Fixed MangoHud PPA issues on Ubuntu 24.04
  - Enhanced repository cleanup for broken PPAs

### Added
- Better error handling for package installation failures
- Fallback logic for optional packages
- Manual installation guidance when automated methods fail

### Documentation
- Created BUGFIX_CHANGELOG.md with detailed fix information
- Updated compatibility matrix for Ubuntu 24.04

---

## [2.0.0] - 2026-01-03

### Added ✨
- **CLI Automation System** - 40+ command-line arguments
  - `--dry-run` mode for safe testing
  - `--yes` flag for unattended installation
  - `--verbose` flag for debug output
  - Platform-specific flags (--nvidia, --amd, --intel, --vm-tools)
  - Tool-specific flags (--steam, --lutris, --heroic, etc.)
- **Multi-Distribution Support**
  - Ubuntu (20.04, 22.04, 24.04)
  - Linux Mint (20, 21, 22)
  - Debian (11, 12)
  - Pop!_OS, Elementary, Zorin, Kali
- **Enhanced System Detection**
  - Distribution family detection
  - Desktop environment detection
  - WSL detection
  - Extended VM type detection (Hyper-V, Xen, Parallels)
- **MangoHud Performance Overlay**
  - Automatic installation
  - Configuration guidance
  - Integration with performance launcher
- **Goverlay** - MangoHud GUI configuration tool
- **Mumble** - Voice chat for gaming
- **State Management System**
  - Installation state tracking (JSON)
  - Rollback framework (partial implementation)
  - Failed operations tracking
- **GE-Proton Auto-Installer**
  - Automatic latest version download from GitHub
  - Extraction to correct Steam directory
  - Proper ownership management
- **Enhanced Documentation**
  - Comprehensive README.md
  - Detailed Quick_Start.md
  - Complete Usage_Guide.md
  - COMPLETE_COMPARISON.md technical documentation

### Changed 🔄
- **InstallationConfig Dataclass** - Type-safe configuration system
- **Argument Parser** - Professional help formatting with examples
- **Error Handling** - Better error messages and graceful degradation
- **Package Management** - Enhanced version checking and update detection
- **Performance Launcher** - Improved error handling and feedback

### Statistics 📊
- Lines of code: 2,927 (was ~1,000 in v1.0)
- CLI arguments: 40+
- Documentation: 2,721 lines across 3 primary docs

---

## [1.0.0] - 2025-12-15

### Initial Release 🎉

The original Ubuntu 24.04 gaming setup script with core functionality:

### Features
- **Interactive Installation** - User-friendly prompts
- **GPU Driver Installation**
  - NVIDIA proprietary drivers
  - AMD Mesa drivers
  - Intel Mesa drivers
- **VM Guest Tools**
  - VMware Tools
  - VirtualBox Guest Additions
  - KVM/QEMU tools
- **Gaming Platforms**
  - Steam
  - Lutris (via Flatpak)
  - Heroic Games Launcher
  - GameMode
- **Compatibility Layers**
  - Wine Staging
  - Winetricks
  - ProtonUp-Qt
- **Additional Tools**
  - Discord
  - OBS Studio
  - Controller support
- **System Optimizations**
  - sysctl gaming parameters
  - CPU performance governor
  - Performance launcher script
- **Essential Features**
  - Smart version checking
  - Installation summary with versions
  - Repository cleanup
  - Comprehensive logging

### Statistics
- Lines of code: ~1,000
- Supported platforms: 4 (Steam, Lutris, Heroic, Discord)
- Utilities: 8 tools

---

## Version History Summary

| Version | Date | Key Addition | Lines of Code |
|---------|------|-------------|---------------|
| 1.0.0 | 2025-12-15 | Initial release | ~1,000 |
| 2.0.0 | 2026-01-03 | CLI automation, multi-distro | 2,927 |
| 2.0.1 | 2026-01-04 | Ubuntu 24.04 fixes | 2,927 |
| 2.1.0 | 2026-01-05 | New platforms & utilities | 3,341 |
| 2.2.0 | 2026-02-16 | Dynamic resolution, driver detection | 3,238 |
| 2.3.0 | 2026-02-17 | Rollback engine, SHA512 verification | 3,924 |
| 2.4.0 | 2026-02-17 | Update mode, presets, self-update | 4,551 |
| 2.5.0 | 2026-02-17 | Security hardening, health check, signal handling | 4,955 |

---

## Upgrade Notes

### From 2.1.x to 2.5.0

**No Breaking Changes** — All 2.1.x features preserved and enhanced.

**New Capabilities Available:**
```bash
# Use configuration presets
sudo python3 debian_gaming_setup.py --preset standard -y

# Rollback a previous installation
sudo python3 debian_gaming_setup.py --rollback

# Update previously installed components
sudo python3 debian_gaming_setup.py --update

# Check for script updates
sudo python3 debian_gaming_setup.py --self-update

# Validate system requirements
sudo python3 debian_gaming_setup.py --check-requirements
```

**Key Improvements:**
- All codenames and driver versions now resolved dynamically (no hardcoded values)
- GE-Proton downloads verified with SHA512 checksums
- All shell=True subprocess calls eliminated (security hardening)
- Performance launcher rewritten to fix multilib LD_PRELOAD issues
- Post-install health check verifies all components
- Signal handlers save state on SIGTERM/SIGINT

### From 2.0.x to 2.1.x

**No Breaking Changes** — All 2.0.x features preserved.

**New Features Available:**
```bash
# Try new platforms
sudo python3 debian_gaming_setup.py --sober
sudo python3 debian_gaming_setup.py --waydroid

# Try new utilities
sudo python3 debian_gaming_setup.py --gwe
sudo python3 debian_gaming_setup.py --vkbasalt
```

**Ubuntu 24.04 Users:**
- Package installation issues resolved
- MangoHud now installs from default repos
- No manual fixes needed

### From 1.0.0 to 2.x.x

**Major Changes:**
- 54 CLI arguments added (backward compatible)
- Interactive mode still works exactly as before
- New features available via CLI flags
- Enhanced error handling and logging
- Multi-distribution support

**To Upgrade:**
1. Download new version
2. Run with your preferred method:
   - Interactive: `sudo python3 debian_gaming_setup.py`
   - Automated: `sudo python3 debian_gaming_setup.py -y [OPTIONS]`
   - Preset: `sudo python3 debian_gaming_setup.py --preset standard -y`

---

## Future Roadmap

### Under Consideration
- [ ] GUI version of the script
- [ ] Integration tests for multiple distributions
- [ ] Package cache for known working configurations
- [ ] Custom kernel installation automation
- [ ] Game-specific optimizations database
- [ ] Privilege dropping for user-space operations

---

## Contributing

See [CONTRIBUTING.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/CONTRIBUTING.md) for how to contribute to this project.

---

## Links

- **Repository:** [Debian-Gaming-Setup-Project](https://github.com/Sandler73/Debian-Gaming-Setup-Project)
- **Issues:** [Issues](https://github.com/Sandler73/Debian-Gaming-Setup-Project/issues)
- **Releases:** [Releases](https://github.com/Sandler73/Debian-Gaming-Setup-Project/releases)
- **Documentation:** See [README.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/README.md), [Quick_Start.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/Quick_Start.md), and [Usage_Guide.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/Usage_Guide.md)

---

**Keep gaming on Linux! 🎮**
