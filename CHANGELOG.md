# Changelog

All notable changes to the Debian-Based Gaming Setup Script will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
