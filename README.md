# Debian-Based Gaming Setup Script v2.6

**A comprehensive automated gaming environment setup for Debian-based Linux distributions**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Ubuntu](https://img.shields.io/badge/Ubuntu-24.04%20%7C%2022.04%20%7C%2020.04-orange.svg)](https://ubuntu.com/)
[![Maintained](https://img.shields.io/badge/Maintained-Yes-green.svg)](https://github.com/Sandler73/Debian-Gaming-Setup-Project)

Transform your Debian-based Linux system into a complete gaming powerhouse with a single command. This script automates the installation and configuration of GPU drivers, gaming platforms, compatibility layers, performance tools, and system optimizations with both interactive and automated modes.

---

## 🌟 What's New in v2.6

- ✨ **Pre-install detection for 7 methods** — `install_vm_tools()`, `_install_ge_proton()`, `install_mangohud()`, `install_goverlay()`, `install_vkbasalt()`, `install_mumble()`, and `install_mod_managers()` now check for existing installations before prompting, reporting version info and offering reinstall/skip
- ✨ **VM tools version detection** — Per-VM-type binary checks (`vmware-toolbox-cmd -v`, `VBoxClient`, `qemu-guest-agent`, etc.) with version reporting
- ✨ **GE-Proton version comparison** — Scans `~/.steam/root/compatibilitytools.d/` for existing versions, compares with latest GitHub release, skips download if already up to date
- ✨ **Flatpak-aware command resolver in launch_game.sh** — `resolve_command()` function maps known app names (lutris, heroic, discord) to their Flatpak run commands when native binaries aren't found
- ✨ **launch_game.sh `--help` / `-h` flag** — Comprehensive inline usage documentation with supported launchers, examples, and enhancement descriptions
- ✨ **LAUNCHER_GUIDE.md** — Standalone documentation for the performance launcher covering all features, Flatpak resolution, Steam per-game config, environment variables, and troubleshooting
- ✨ **FAQ.md** — Comprehensive standalone FAQ with 50+ entries across 12 categories (General, Installation, GPU/Drivers, Gaming Platforms, Performance, Compatibility, Maintenance, Troubleshooting, Waydroid, Advanced, Security, Contributing)

---

## 🌟 What's New in v2.5

- ✨ **Action-Based Rollback Engine** - Full undo capability with `--rollback` (7 action types, LIFO reversal, dry-run preview)
- ✨ **Update Mode** - Centralized component updating with `--update` (APT, Flatpak, GE-Proton)
- ✨ **Self-Update** - Check for newer script versions from GitHub with `--self-update`
- ✨ **Configuration Presets** - `--preset minimal|standard|complete|streaming` for quick setup
- ✨ **System Pre-Checks** - Disk space, RAM, architecture, and dpkg lock validation
- ✨ **Post-Install Health Check** - Automated verification of all installed components
- ✨ **Signal Handling** - Graceful SIGTERM/SIGINT cleanup with state preservation
- ✨ **GE-Proton SHA512 Verification** - Checksum validation for all GE-Proton downloads
- ✨ **Dynamic Distribution Resolution** - No hardcoded codenames; supports any Debian derivative
- ✨ **Dynamic GPU Driver Detection** - NVIDIA/AMD/Intel drivers resolved at runtime
- ✨ **Security Hardening** - No shell=True, no bare except clauses, categorized timeouts, secure external script handling
- 🛠 **Performance Launcher Rewrite** - Fixed multilib LD_PRELOAD issues with Steam/MangoHud/GameMode
- 📖 **Enhanced Documentation** - Complete usage guides, security policy, changelog

[See CHANGELOG.md for full details](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/CHANGELOG.md)

---

## 🚀 Quick Start

### One-Command Installation

```bash
# Download
wget https://raw.githubusercontent.com/Sandler73/Debian-Gaming-Setup-Project/main/debian_gaming_setup.py

# Interactive mode (recommended for first-time users)
sudo python3 debian_gaming_setup.py

# Or use a preset for quick automated setup
sudo python3 debian_gaming_setup.py --preset standard -y

# Or fully targeted (NVIDIA example)
sudo python3 debian_gaming_setup.py -y \
    --nvidia --all-platforms --optimize --launcher
```

**That's it!** Reboot after installation and start gaming! 🎮

See [Quick_Start.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/Quick_Start.md) for detailed first-time setup guide.

---

## ⭐ Key Features

- ✅ **8 Gaming Platforms** - Steam, Lutris, Heroic, ProtonUp-Qt, Roblox (SOBER), Android (Waydroid), Discord, OBS
- ✅ **All GPU Vendors** - NVIDIA, AMD, Intel with fully dynamic detection and driver selection
- ✅ **VM Support** - VMware, VirtualBox, KVM, Hyper-V, Xen, Parallels
- ✅ **54 CLI Arguments** - Full automation across 9 argument groups
- ✅ **4 Configuration Presets** - minimal, standard, complete, streaming
- ✅ **Action-Based Rollback** - Undo any installation with 7 tracked action types
- ✅ **Update Mode** - Refresh all previously installed components in one command
- ✅ **Self-Update** - Check GitHub for newer script versions automatically
- ✅ **Smart Prompts** - Shows versions, detects updates, intelligent recommendations
- ✅ **Dry-Run Mode** - Test before installing with `--dry-run`
- ✅ **Performance Tools** - GameMode, MangoHud, vkBasalt, CPU governor
- ✅ **Visual Enhancement** - vkBasalt post-processing, ReShade guidance
- ✅ **GE-Proton** - Automatic installation with SHA512 checksum verification
- ✅ **Security Hardened** - No shell=True, specific exception types, categorized timeouts
- ✅ **Post-Install Health Check** - Automated verification of packages, binaries, GPU drivers
- ✅ **Signal Handling** - Graceful cleanup on SIGTERM/SIGINT with state preservation
- ✅ **Comprehensive Logging** - Detailed logs with error tracking
- ✅ **10+ Distributions** - Ubuntu, Mint, Debian, Pop!_OS, Elementary, Zorin, Kali, and any derivative

---

## 📦 What Gets Installed

### Core Components
- **GPU Drivers** - NVIDIA/AMD/Intel or VM guest tools (dynamically detected)
- **Gaming Platforms** - Steam, Lutris, Heroic, ProtonUp-Qt
- **Compatibility** - Wine (WineHQ with codename validation), Winetricks, GE-Proton (SHA512 verified)
- **Performance** - GameMode, MangoHud, Goverlay
- **Utilities** - Discord, OBS, Mumble, controller support

### Specialized Platforms ✨
- **SOBER** - Roblox on Linux via Flatpak
- **Waydroid** - Full Android container for mobile games (secure download-then-execute install)
- **GreenWithEnvy** - NVIDIA GPU control and monitoring
- **vkBasalt** - Vulkan post-processing (ReShade-like)
- **Mod Managers** - r2modman setup

### State Management & Safety
- **Rollback Engine** - 7 action types tracked with LIFO reversal and dry-run preview
- **Update Mode** - Centralized APT, Flatpak, and GE-Proton updating
- **Self-Update** - GitHub API version checking with syntax validation before replacement
- **Pre-Flight Checks** - System requirements, package availability, network connectivity
- **Post-Install Health Check** - Verifies APT packages, key binaries, Flatpak apps, GPU drivers
- **Signal Handling** - SIGTERM/SIGINT handlers save state before clean exit

[See complete list in Usage_Guide.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/Usage_Guide.md)

---

## 💻 Supported Systems

### Tested & Verified ✅
- Ubuntu 24.04, 22.04, 20.04
- Linux Mint 22, 21, 20 (including LMDE)
- Debian 12 (Bookworm), 11 (Bullseye)
- Pop!_OS 22.04+
- Elementary OS 6+
- Zorin OS 16+
- Kali Linux 2020+

### Hardware Support
- **Physical GPUs** - NVIDIA GeForce/Quadro/Tesla, AMD Radeon, Intel HD/Iris/Arc
- **Virtual Machines** - VMware, VirtualBox, KVM/QEMU, Hyper-V, Xen, Parallels

All distribution codenames are resolved dynamically — no hardcoded values. Any Debian/Ubuntu derivative is auto-detected via `/etc/os-release` with a 7-step fallback chain.

---

## 🎯 Usage Examples

### Complete Setups

**NVIDIA Gaming PC (Maximum Features):**
```bash
sudo python3 debian_gaming_setup.py -y \
    --nvidia --all-platforms --sober --wine --ge-proton \
    --gamemode --mangohud --gwe --vkbasalt \
    --discord --obs --mod-managers --controllers \
    --essential --codecs --optimize --launcher
```

**AMD Gaming PC (Complete):**
```bash
sudo python3 debian_gaming_setup.py -y \
    --amd --all-platforms --wine --ge-proton \
    --gamemode --mangohud --vkbasalt \
    --discord --controllers --essential --codecs --optimize
```

**Intel Laptop (Battery-Conscious):**
```bash
sudo python3 debian_gaming_setup.py -y \
    --intel --steam --lutris --gamemode --mangohud --essential
```

**Virtual Machine:**
```bash
sudo python3 debian_gaming_setup.py -y \
    --vm-tools --steam --lutris --gamemode --essential
```

### Preset Setups

| Preset | Components |
|--------|-----------|
| `minimal` | GPU drivers + Steam |
| `standard` | + Wine, Lutris, Heroic, ProtonUp-Qt, GameMode, MangoHud, codecs, optimizations, launcher |
| `complete` | All components including SOBER, Waydroid, Discord, OBS, vkBasalt, mod managers |
| `streaming` | Standard + OBS, Discord, Mumble |

```bash
# Presets combine with explicit flags (non-destructive overlay)
sudo python3 debian_gaming_setup.py --preset standard --waydroid --vkbasalt -y
```

### Maintenance Operations

```bash
sudo python3 debian_gaming_setup.py --update           # Update installed components
sudo python3 debian_gaming_setup.py --rollback          # Undo previous installation
sudo python3 debian_gaming_setup.py --self-update       # Check for script updates
sudo python3 debian_gaming_setup.py --check-requirements # Validate system
```

### Specialized Setups

**Roblox Player:**
```bash
sudo python3 debian_gaming_setup.py -y --sober --essential --controllers
```

**Mobile/Android Gaming:**
```bash
sudo python3 debian_gaming_setup.py -y --waydroid --controllers --essential
```

**Streaming Setup:**
```bash
sudo python3 debian_gaming_setup.py --preset streaming -y
```

[See more examples in Usage_Guide.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/Usage_Guide.md#usage-examples-by-scenario)

---

## 🎛️ Command-Line Options

### Quick Reference
```
General:          -y, --yes, --dry-run, --verbose, --no-backup, --skip-update
GPU/Drivers:      --nvidia, --amd, --intel, --vm-tools
Platforms:        --steam, --lutris, --heroic, --protonup, --sober, --waydroid, --all-platforms
Compatibility:    --wine, --winetricks, --ge-proton, --dxvk, --vkd3d
Performance:      --gamemode, --mangohud, --goverlay, --gwe
Graphics:         --vkbasalt, --reshade
Tools:            --discord, --obs, --mumble, --mod-managers, --controllers, --essential, --codecs
System:           --optimize, --launcher, --custom-kernel
Maintenance:      --rollback, --update, --self-update, --check-requirements, --cleanup
Presets:          --preset {minimal,standard,complete,streaming}
```

[Complete CLI reference in Usage_Guide.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/Usage_Guide.md#all-command-line-options)

---

## 🔄 Rollback System

Every reversible operation is automatically tracked. The rollback engine records 7 action types:

| Action Type | What's Tracked | Reversal |
|-------------|---------------|----------|
| `apt_install` | APT package installs | `apt-get remove` |
| `flatpak_install` | Flatpak app installs | `flatpak uninstall` |
| `repo_add` | Repository additions | Remove repo files + update |
| `file_create` | Files created by script | Remove |
| `file_modify` | Files modified (backed up) | Restore from backup |
| `sysctl_write` | sysctl config changes | Remove + reload |
| `ge_proton_install` | GE-Proton extraction | Remove directory |

```bash
# Rollback with dry-run preview before execution
sudo python3 debian_gaming_setup.py --rollback
```

---

## 🎮 Post-Installation

1. **Reboot** — `sudo reboot` (required for drivers)
2. **Verify GPU** — `nvidia-smi` or `glxinfo | grep renderer`
3. **Configure Steam** — Settings → Compatibility → Enable Steam Play → Proton Experimental
4. **Test a game** — Native: CS2, Portal 2 | Proton: Stardew Valley, Terraria
5. **Performance launcher** — `~/launch-game.sh steam`

---

## 📁 File Locations

| File | Path | Purpose |
|------|------|---------|
| Logs | `~/gaming_setup_logs/gaming_setup_*.log` | Timestamped operation logs |
| State | `~/gaming_setup_logs/installation_state.json` | Installed component inventory |
| Rollback | `~/gaming_setup_logs/rollback_manifest.json` | Action history for rollback |
| Backups | `~/gaming_setup_backups/` | Pre-modification file backups |
| Launcher | `~/launch-game.sh` | Performance game launcher |
| MangoHud | `~/.config/MangoHud/MangoHud.conf` | HUD overlay settings |

---

## 📖 Documentation

| Document | Purpose | Best For |
|----------|---------|----------|
| [README.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/README.md) | Overview & quick start | Everyone |
| [Quick_Start.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/Quick_Start.md) | Step-by-step guide | First-time users |
| [Usage_Guide.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/Usage_Guide.md) | Complete reference | All users |
| [CHANGELOG.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/CHANGELOG.md) | Version history | Tracking changes |
| [CONTRIBUTING.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/CONTRIBUTING.md) | Contribution guide | Contributors |
| [SECURITY.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/SECURITY.md) | Security policies | Reporting issues |
| [CODE_OF_CONDUCT.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/CODE_OF_CONDUCT.md) | Community guidelines | Contributors |

---

## 🛠 Troubleshooting

### Common Issues

**"Package has no installation candidate"**
```bash
sudo apt-get update && sudo apt-get upgrade
```

**NVIDIA driver not loading**
```bash
sudo apt-get install --reinstall nvidia-driver-*
sudo update-initramfs -u && sudo reboot
```

**Steam won't launch**
```bash
steam  # Run from terminal to see errors
rm -rf ~/.steam/steam/appcache/  # Clear cache
```

**GameMode "cannot open shared object" errors**
```bash
sudo apt install libgamemode0 libgamemode0:i386
```

**MangoHud not showing**
- Performance launcher uses `MANGOHUD=1` env var (Vulkan implicit layer)
- Steam per-game: set Launch Options to `mangohud %command%`
- Config: `~/.config/MangoHud/MangoHud.conf`

**Check logs**
```bash
cat ~/gaming_setup_logs/gaming_setup_*.log | tail -100
grep ERROR ~/gaming_setup_logs/gaming_setup_*.log
```

[Full troubleshooting guide in Usage_Guide.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/Usage_Guide.md#troubleshooting)

---

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/CONTRIBUTING.md) for guidelines.

---

## 📊 Project Stats

- **4,955 lines** of Python code
- **54 CLI arguments** for automation across 9 groups
- **89 methods** in the GamingSetup class
- **8 gaming platforms** supported
- **15+ utilities** included
- **4 configuration presets**
- **7 rollback action types** tracked
- **10+ distributions** tested
- **0 external Python dependencies** — standard library only
- **Active maintenance** ongoing

---

## 📜 License

[MIT License](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/LICENSE) - Free to use, modify, and distribute.

---

## ⚠️ Disclaimer

This script makes system-level changes. Always:
- ✅ Backup important data
- ✅ Test with `--dry-run` first
- ✅ Review logs for errors
- ✅ Understand what's being installed

**Use at your own risk.** No warranty provided.

---

<div align="center">

**⭐ Star this repo if it helped you! ⭐**

Made with ❤️ for the Linux gaming community

**Version 2.5.0** | Updated February 2026

[Report Issue](https://github.com/Sandler73/Debian-Gaming-Setup-Project/issues) | [Request Feature](https://github.com/Sandler73/Debian-Gaming-Setup-Project/issues/new) | [Contribute](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/CONTRIBUTING.md)

</div>
