# Usage Guide v2.5

**Complete reference for all features and command-line options**

This guide provides detailed documentation for every feature, option, and use case of the Debian-Based Gaming Setup Script.

---

## 📚 Table of Contents

- [Basic Usage](#basic-usage)
- [All Command-Line Options](#all-command-line-options)
- [Configuration Presets](#configuration-presets)
- [Usage Examples by Scenario](#usage-examples-by-scenario)
- [Platform Details](#platform-details)
- [Utility Details](#utility-details)
- [Performance Optimization](#performance-optimization)
- [Performance Launcher](#performance-launcher)
- [Rollback System](#rollback-system)
- [Update Mode](#update-mode)
- [Self-Update](#self-update)
- [System Requirements Check](#system-requirements-check)
- [Advanced Configuration](#advanced-configuration)
- [File Locations & Logs](#file-locations--logs)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)
- [FAQ](#faq)

---

## Basic Usage

### Interactive Mode (Default)

```bash
sudo python3 debian_gaming_setup.py
```

**Best for:**
- First-time installation
- Want to see what's installed
- Review each component
- Unsure which options to choose

**Features:**
- Shows current installed versions
- Detects available updates
- Prompts for each component
- Provides explanations
- Safe for beginners

### Automated Mode

```bash
sudo python3 debian_gaming_setup.py -y [OPTIONS]
```

**Best for:**
- Know exactly what you want
- Deploying to multiple systems
- Scripting/automation
- Prefer command-line control

**Features:**
- No prompts (auto-yes)
- Faster installation
- Scriptable
- Reproducible

### Preset Mode ✨

```bash
sudo python3 debian_gaming_setup.py --preset standard -y
```

**Best for:**
- Quick setup with curated component bundles
- Don't want to pick individual flags
- Combine with explicit flags for customization

**Presets are non-destructive:** They only set flags you didn't explicitly set via CLI.

### Dry-Run Mode

```bash
sudo python3 debian_gaming_setup.py --dry-run [OPTIONS]
```

**Best for:**
- Testing before actual installation
- Verifying what will be installed
- Learning about components
- Debugging issues

**Features:**
- Shows what would be done
- No actual changes
- Safe for testing
- Educational

### Maintenance Modes ✨

```bash
# Update all previously installed components
sudo python3 debian_gaming_setup.py --update

# Rollback a previous installation
sudo python3 debian_gaming_setup.py --rollback

# Check for newer script version
sudo python3 debian_gaming_setup.py --self-update

# Validate system requirements only
sudo python3 debian_gaming_setup.py --check-requirements
```

---

## All Command-Line Options

### General Options

```
-h, --help              Display help message and exit
-y, --yes               Auto-answer yes (unattended mode)
--dry-run               Test mode - show what would be done
--verbose               Enable verbose debug output
--no-backup             Skip creating backups before modifications
--skip-update           Skip system package update
```

### GPU/Driver Options

```
--nvidia                Install NVIDIA proprietary drivers (dynamically detected)
--amd                   Install AMD Mesa drivers with Vulkan support
--intel                 Install Intel Mesa drivers with media acceleration
--vm-tools              Install VM guest tools (auto-detected type)
```

**NVIDIA:** Dynamic driver selection via `ubuntu-drivers` (Ubuntu family) or `apt-cache search` (Debian). Never hardcoded.
**AMD:** mesa-vulkan-drivers, libvulkan1, vulkan-tools, firmware-amd-graphics (Debian)
**Intel:** mesa-vulkan-drivers, intel-media-va-driver, i965-va-driver, Intel Arc support
**VM:** Detects VMware/VirtualBox/KVM/Hyper-V/Xen/Parallels and installs appropriate tools

### Gaming Platform Options

```
--steam                 Install Valve Steam
--lutris                Install Lutris (Epic, GOG, Battle.net)
--heroic                Install Heroic Games Launcher
--protonup              Install ProtonUp-Qt (Proton version manager)
--sober                 Install SOBER (Roblox on Linux)
--waydroid              Install Waydroid (Android container)
--all-platforms         Install all standard platforms (excludes specialized)
```

**--all-platforms includes:** Steam, Lutris, Heroic, ProtonUp-Qt
**--all-platforms excludes:** SOBER, Waydroid (specialized use cases)

### Compatibility Layer Options

```
--wine                  Install Wine Staging (WineHQ with codename validation)
--winetricks            Install Winetricks (Wine configuration tool)
--ge-proton             Install GE-Proton (latest from GitHub, SHA512 verified)
--dxvk                  Show DXVK installation information
--vkd3d                 Show VKD3D-Proton installation information
```

### Performance Tool Options

```
--gamemode              Install Feral GameMode
--mangohud              Install MangoHud performance overlay
--goverlay              Install Goverlay (MangoHud GUI)
--gwe                   Install GreenWithEnvy (NVIDIA GPU control)
```

### Graphics Enhancement Options ✨

```
--vkbasalt              Install vkBasalt (Vulkan post-processing)
--reshade               Show ReShade setup information for Linux
```

### Additional Tool Options

```
--discord               Install Discord (via Flatpak)
--obs                   Install OBS Studio (streaming/recording)
--mumble                Install Mumble (low-latency voice chat)
--mod-managers          Install mod management tools (r2modman)
--controllers           Install controller support (Xbox, PlayStation)
--essential             Install essential gaming packages
--codecs                Install multimedia codecs
```

### System Optimization Options

```
--optimize              Apply gaming system optimizations (sysctl tuning)
--launcher              Create performance launcher script
--custom-kernel         Install custom gaming kernel (planned)
```

### Maintenance Options ✨

```
--rollback              Rollback previous installation (full action-based reversal)
--update                Update all previously installed components
--self-update           Check GitHub for newer script version and install
--check-requirements    Validate system requirements without installing
--cleanup               Clean up installation files and logs
```

### Preset Options ✨

```
--preset minimal        GPU drivers + Steam only
--preset standard       Drivers, Steam, Lutris, Heroic, ProtonUp-Qt, Wine,
                        GameMode, MangoHud, codecs, optimizations, launcher
--preset complete       All components: platforms, tools, communication apps
--preset streaming      Standard + OBS, Discord, Mumble
```

---

## Configuration Presets

Presets are **non-destructive overlays** — they only enable components that weren't already set by explicit CLI flags.

| Preset | Components Included |
|--------|-------------------|
| `minimal` | GPU drivers, Steam |
| `standard` | minimal + Wine, Winetricks, Lutris, Heroic, ProtonUp-Qt, GameMode, MangoHud, essential packages, codecs, system optimizations, performance launcher |
| `complete` | standard + SOBER, Waydroid, GE-Proton, DXVK, VKD3D, Discord, OBS, Mumble, GreenWithEnvy, Goverlay, vkBasalt, mod managers, controllers |
| `streaming` | standard + OBS, Discord, Mumble |

**Combining presets with flags:**
```bash
# Standard preset plus Waydroid and vkBasalt
sudo python3 debian_gaming_setup.py --preset standard --waydroid --vkbasalt -y
```

Explicit CLI flags always take precedence over presets.

---

## Usage Examples by Scenario

### Complete Gaming Setups

**1. NVIDIA Desktop (Maximum Features)**
```bash
sudo python3 debian_gaming_setup.py -y \
    --nvidia --all-platforms --sober --wine --ge-proton \
    --gamemode --mangohud --gwe --vkbasalt \
    --discord --obs --mod-managers --controllers \
    --essential --codecs --optimize --launcher
```

**2. AMD Desktop (Complete)**
```bash
sudo python3 debian_gaming_setup.py -y \
    --amd --all-platforms --wine --ge-proton \
    --gamemode --mangohud --vkbasalt \
    --discord --controllers --essential --codecs --optimize
```

**3. Intel Laptop (Battery-Conscious)**
```bash
sudo python3 debian_gaming_setup.py -y \
    --intel --steam --lutris --gamemode --mangohud --essential
# Note: Skip --optimize on laptops (CPU governor drains battery)
```

**4. Virtual Machine**
```bash
sudo python3 debian_gaming_setup.py -y \
    --vm-tools --steam --lutris --gamemode --essential
```

### Specialized Setups

**5. Roblox Player**
```bash
sudo python3 debian_gaming_setup.py -y \
    --sober --essential --controllers
```

**6. Mobile/Android Gaming**
```bash
sudo python3 debian_gaming_setup.py -y \
    --waydroid --controllers --essential
# Requires: Wayland session for best performance
# Post-install: sudo waydroid init
```

**7. Visual Enhancement Focus**
```bash
sudo python3 debian_gaming_setup.py -y \
    --vkbasalt --reshade --mangohud --goverlay
```

**8. Modding Setup**
```bash
sudo python3 debian_gaming_setup.py -y \
    --mod-managers --wine --lutris --essential
```

**9. Streaming Setup**
```bash
sudo python3 debian_gaming_setup.py --preset streaming -y
```

**10. Minimal Setup (Steam Only)**
```bash
sudo python3 debian_gaming_setup.py --preset minimal -y
```

---

## Platform Details

### Steam

**Installation:** APT package (steam-installer)
**Size:** ~500MB
**Features:** 50,000+ games, Proton, Workshop, Cloud Saves

**Post-Install:**
1. Launch: `steam`
2. Settings → Compatibility
3. Enable "Steam Play for all other titles"
4. Select Proton Experimental

**Launch Options:**
```
mangohud %command%              # Performance overlay
gamemoderun %command%           # GameMode optimization
ENABLE_VKBASALT=1 %command%    # Post-processing effects
gamemoderun mangohud %command%  # Combined
```

### Lutris

**Installation:** Flatpak (net.lutris.Lutris)
**Size:** ~200MB
**Features:** Epic, GOG, Battle.net, Origin, Ubisoft, Emulators

**Usage:**
1. Browse: https://lutris.net/games
2. Click Install on game page
3. Follow on-screen instructions

### Heroic Games Launcher

**Installation:** Flatpak (com.heroicgameslauncher.hgl)
**Size:** ~150MB
**Features:** Epic Games Store, GOG, Amazon Prime Gaming

### SOBER (Roblox) ✨

**Installation:** Flatpak (org.vinegarhq.Sober)
**Size:** ~100MB
**Features:** Full Roblox client for Linux
**Launch:** `flatpak run org.vinegarhq.Sober`

### Waydroid (Android) ✨

**Installation:** APT package + repository (secure download-then-execute)
**Size:** ~300MB
**Features:** Full Android system (not emulation!)

**Requirements:** Wayland session (best performance), compatible kernel modules

**Post-Install:**
```bash
sudo waydroid init
waydroid session start
waydroid show-full-ui
```

---

## Utility Details

### GameMode

**What:** CPU/IO optimization daemon by Feral Interactive
**Features:** Automatic performance mode, I/O priority, GPU performance
**Usage:** Automatic in Lutris, manual with `gamemoderun`

### MangoHud

**What:** Performance monitoring overlay
**Features:** FPS, frame time, CPU/GPU usage, temperatures
**Config:** `~/.config/MangoHud/MangoHud.conf` (created by installer if missing)
**Toggle:** Shift+F12 (default)

**Example config:**
```ini
fps
frame_timing=1
cpu_temp
gpu_temp
position=top-left
```

### GreenWithEnvy (GWE) ✨

**What:** NVIDIA GPU monitoring and overclocking
**Requirements:** NVIDIA GPU
**Launch:** `flatpak run com.leinardi.gwe`

### vkBasalt ✨

**What:** Vulkan post-processing layer (ReShade-like)
**Features:** CAS (sharpening), FXAA, SMAA, color grading
**Config:** `~/.config/vkBasalt/vkBasalt.conf`
**Toggle:** Home key (default)

**Enable for games:**
```bash
ENABLE_VKBASALT=1 %command%  # Steam
ENABLE_VKBASALT=1 ./game     # Direct
```

### Mod Managers ✨

**r2modman:** For Unity games (Risk of Rain 2, Valheim) — installed via Flatpak

---

## Performance Optimization

### Performance Launcher (~/launch-game.sh)

The script creates a rewritten performance launcher that handles:

1. **CPU governor** — Saves current governor, switches to performance, restores on exit
2. **GameMode** — Validates `libgamemodeauto.so.0` via `ldconfig -p` before enabling (prevents multilib errors)
3. **MangoHud** — Activates via `MANGOHUD=1` environment variable (Vulkan implicit layer) instead of LD_PRELOAD (prevents 32-bit/64-bit conflicts)
4. **Steam-specific** — Skips `gamemoderun` wrapping for Steam; advises per-game Launch Options

```bash
~/launch-game.sh steam
~/launch-game.sh lutris
~/launch-game.sh wine /path/to/game.exe
```

### System Optimizations (Applied by --optimize)

**File watchers:** `fs.inotify.max_user_watches=524288`
**Memory mapping:** `vm.max_map_count=2147483642`
**CPU governor:** Performance mode systemd service

---

## Rollback System

The rollback engine automatically tracks every reversible operation.

### 7 Action Types

| Action Type | What's Tracked | Reversal |
|-------------|---------------|----------|
| `apt_install` | APT package installs | `apt-get remove` |
| `flatpak_install` | Flatpak app installs | `flatpak uninstall` |
| `repo_add` | Repository additions | Remove repo files + `apt-get update` |
| `file_create` | Files created by script | `rm` |
| `file_modify` | Files modified (with backup) | Restore from backup |
| `sysctl_write` | sysctl config changes | `rm` config + `sysctl --system` |
| `ge_proton_install` | GE-Proton extraction | `rm -rf` extracted directory |

### Using Rollback

```bash
sudo python3 debian_gaming_setup.py --rollback
```

The engine will:
1. Load the rollback manifest from `~/gaming_setup_logs/rollback_manifest.json`
2. Display a grouped summary of what will be reversed
3. Ask for confirmation
4. Offer a dry-run preview showing exact commands
5. Process actions in reverse order (LIFO)
6. Archive the manifest after completion (not deleted — audit trail preserved)

### Auto-Recording

APT and Flatpak installs are auto-recorded by a hook in `run_command()`. File creates, repo adds, sysctl writes, and GE-Proton installs are recorded by dedicated methods. No manual tracking needed.

### Manifest Persistence

Saved atomically (temp file + `os.replace()`) after every action — survives crashes and restarts.

---

## Update Mode

```bash
sudo python3 debian_gaming_setup.py --update
```

Reads `installation_state.json` to identify previously installed components:

1. **APT packages** — Checks each tracked package for available upgrades
2. **Flatpak apps** — Runs `flatpak update -y`
3. **GE-Proton** — Queries GitHub API for newer releases, offers install if available
4. Updates the state file timestamp

---

## Self-Update

```bash
sudo python3 debian_gaming_setup.py --self-update
```

1. Queries the GitHub API for the latest release tag
2. Compares using semantic version parsing (handles v-prefix, hyphens, varying parts)
3. Downloads the script asset if newer
4. Validates syntax via `py_compile` before replacing
5. Backs up current version as `.v{version}.backup`
6. Replaces atomically via `os.replace()`

---

## System Requirements Check

```bash
sudo python3 debian_gaming_setup.py --check-requirements
```

Also runs automatically at the start of every installation.

| Check | Minimum | Warning |
|-------|---------|---------|
| Disk space | 5 GB free | < 10 GB free |
| RAM | 2 GB | — |
| Architecture | x86_64/amd64 | i386/i686 (limited support) |
| dpkg lock | Not locked | — |
| Python version | 3.7+ | — |

If any requirement fails, you're prompted to continue or cancel.

---

## Advanced Configuration

### Per-Game Proton Versions

1. Right-click game in Steam
2. Properties → Compatibility
3. Check "Force the use of a specific compatibility tool"
4. Select version (GE-Proton recommended for many games)

### Steam Launch Options Examples

```bash
# MangoHud + GameMode
gamemoderun mangohud %command%

# vkBasalt + MangoHud
ENABLE_VKBASALT=1 mangohud %command%

# Force Proton
PROTON_USE_WINED3D=1 %command%

# Enable logging
PROTON_LOG=1 %command%

# Everything combined
gamemoderun ENABLE_VKBASALT=1 mangohud %command%
```

### Wine Prefixes

```bash
# Create separate prefix
WINEPREFIX=~/.wine-game1 winecfg

# Install dependencies
WINEPREFIX=~/.wine-game1 winetricks directx9

# Run game
WINEPREFIX=~/.wine-game1 wine game.exe
```

---

## File Locations & Logs

| File | Path | Description |
|------|------|-------------|
| Operation logs | `~/gaming_setup_logs/gaming_setup_YYYYMMDD_HHMMSS.log` | Detailed log per execution |
| Installation state | `~/gaming_setup_logs/installation_state.json` | Tracks installed components and packages |
| Rollback manifest | `~/gaming_setup_logs/rollback_manifest.json` | Action history for rollback |
| Backups | `~/gaming_setup_backups/` | File backups taken before modifications |
| Performance launcher | `~/launch-game.sh` | Game launcher with perf enhancements |
| MangoHud config | `~/.config/MangoHud/MangoHud.conf` | HUD overlay configuration |

---

## Troubleshooting

### Script Issues

**"Must be run with sudo"**
```bash
sudo python3 debian_gaming_setup.py
```

**"dpkg is locked"**
```bash
sudo lsof /var/lib/dpkg/lock-frontend  # Check what's using it
# If safe, clear stale locks:
sudo rm /var/lib/dpkg/lock-frontend /var/lib/dpkg/lock
sudo dpkg --configure -a
```

**Package installation fails**
```bash
sudo apt-get update && sudo apt-get upgrade
# Then rerun script
```

### Driver Issues

**NVIDIA not loading**
```bash
lsmod | grep nvidia  # Check if loaded
sudo apt-get install --reinstall nvidia-driver-*
sudo update-initramfs -u
sudo reboot
```

**AMD no Vulkan**
```bash
sudo apt-get install mesa-vulkan-drivers mesa-vulkan-drivers:i386
vulkaninfo  # Test
```

### Game Issues

**Won't start**
- Check ProtonDB for known issues
- Try different Proton version
- Check game logs: `~/.steam/steam/logs/`

**Poor performance**
- Verify GPU drivers: `nvidia-smi` or `glxinfo`
- Use performance launcher: `~/launch-game.sh steam`
- Enable GameMode in game settings
- Check MangoHud overlay

**GameMode "cannot open shared object" errors**
```bash
sudo apt install libgamemode0 libgamemode0:i386
```

**MangoHud not showing**
1. Verify installation: `mangohud --version`
2. Check config: `~/.config/MangoHud/MangoHud.conf`
3. Vulkan games: `MANGOHUD=1` activates automatically
4. OpenGL games: launch with `mangohud glxgears`

### Check Logs

```bash
# View latest log
cat ~/gaming_setup_logs/gaming_setup_*.log | tail -100

# Search for errors
grep ERROR ~/gaming_setup_logs/gaming_setup_*.log

# View all logs
ls -lh ~/gaming_setup_logs/
```

---

## Best Practices

### Regular Maintenance

```bash
# Weekly
sudo apt-get update && sudo apt-get upgrade
flatpak update

# Monthly
sudo apt-get autoremove
sudo apt-get autoclean

# Or use the built-in updater
sudo python3 debian_gaming_setup.py --update
```

### Backup Game Saves

**Steam Cloud:** Enabled by default
**Manual backup:**
```bash
tar -czf steam-saves.tar.gz ~/.steam/steam/userdata/
```

### Monitor Performance

- Enable MangoHud for new games
- Check ProtonDB before buying
- Keep logs for troubleshooting

---

## FAQ

**Q: Do I need to reboot?**
A: Yes, after driver installation. Other components may work without reboot.

**Q: Can I run multiple times?**
A: Yes, the script checks versions and offers to update/reinstall.

**Q: Will this work on [distro]?**
A: Works on any Debian-based distro. Codenames are resolved dynamically.

**Q: Can I uninstall components?**
A: Yes, use `--rollback` to undo the entire installation, or manually:
```bash
sudo apt-get remove package-name
flatpak uninstall app.id
```

**Q: What are the system requirements?**
A: 5 GB disk, 2 GB RAM, x86_64 architecture, Python 3.7+. Run `--check-requirements` to validate.

**Q: Does it require internet?**
A: Yes, for package downloads. The script checks connectivity before remote operations.

**Q: Are there any external Python dependencies?**
A: No. The script uses only the Python standard library.

---

**For more help:** See [README.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/README.md) and [Quick_Start.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/Quick_Start.md)

**Version:** 2.5.0 | Updated: February 2026
