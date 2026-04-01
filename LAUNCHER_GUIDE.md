# Gaming Performance Launcher Guide

## `~/launch-game.sh` — Comprehensive Usage Documentation

**Version:** 3.5.0 | **Created by:** Debian Gaming Setup Script
**Location:** `~/launch-game.sh` (created during installation)

---

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [How It Works](#how-it-works)
- [Supported Launchers](#supported-launchers)
- [Steam Per-Game Configuration](#steam-per-game-configuration)
- [Automatic Enhancements](#automatic-enhancements)
- [Flatpak Resolution](#flatpak-resolution)
- [Environment Variables](#environment-variables)
- [Command Reference](#command-reference)
- [Troubleshooting](#troubleshooting)
- [Technical Details](#technical-details)

---

## Overview

The Gaming Performance Launcher (`launch-game.sh`) is a wrapper script that automatically applies performance optimizations when launching games. It handles CPU governor management, GameMode integration, MangoHud overlay activation, and Flatpak application resolution — all while avoiding the multilib LD_PRELOAD conflicts that commonly plague Linux gaming setups.

The script is created automatically by the Debian Gaming Setup Script during installation and placed in your home directory at `~/launch-game.sh`.

### What It Does

When you launch a game through this script, it automatically:

1. **Sets CPU governor to "performance"** — Prevents CPU frequency scaling during gameplay, ensuring maximum clock speeds. Restored to the original governor when the game exits.

2. **Enables GameMode** (if installed) — Activates Feral Interactive's GameMode via `gamemoderun`, which applies real-time process priority, I/O priority, and CPU governor optimizations. Library presence is validated before enabling to prevent missing-library errors.

3. **Activates MangoHud** (if installed) — Enables the MangoHud performance overlay using the `MANGOHUD=1` environment variable. This uses the Vulkan implicit layer rather than LD_PRELOAD, which avoids the 32-bit/64-bit library conflicts that the `mangohud` wrapper command can cause.

4. **Resolves Flatpak applications** — When you type `launch-game.sh lutris`, it automatically detects whether Lutris is installed as a native package or Flatpak and launches accordingly.

5. **Cleans up on exit** — Restores CPU governor, reports session end.

### What It Does NOT Do

The launcher does **not** modify game files, change system settings permanently, or require root access for normal operation (CPU governor changes may request `sudo` if `cpupower` is available).

---

## Quick Start

```bash
# Launch Steam with all optimizations
~/launch-game.sh steam

# Launch Lutris (auto-resolves Flatpak if needed)
~/launch-game.sh lutris

# Launch Heroic Games Launcher
~/launch-game.sh heroic

# Launch a native Linux game
~/launch-game.sh /path/to/game

# Launch a Windows game via Wine
~/launch-game.sh wine /path/to/game.exe

# Show help
~/launch-game.sh --help
```

---

## How It Works

### Startup Sequence

When you run `~/launch-game.sh <command>`, the script executes in this order:

1. **Argument parsing** — Validates input, checks for `--help`
2. **Command resolution** — Resolves known app names (lutris, heroic, discord) to their Flatpak equivalents if native binaries aren't found
3. **CPU governor** — Saves current governor, sets to "performance"
4. **GameMode check** — Verifies `gamemoderun` binary AND `libgamemodeauto.so.0` in `ldconfig` cache
5. **MangoHud check** — Enables via `MANGOHUD=1` if MangoHud binary or Vulkan layer file exists
6. **Steam detection** — If launching Steam, skips `gamemoderun` wrapping (shows per-game Launch Options instead)
7. **Launch** — Executes the game via `exec` (replaces the shell process)
8. **Cleanup** — On exit (normal or interrupt), restores CPU governor

### Why `MANGOHUD=1` Instead of `mangohud` Wrapper

The `mangohud` command sets `LD_PRELOAD=/usr/$LIB/mangohud/libMangoHud.so`. This causes three problems:

- `$LIB` doesn't expand correctly in all shell contexts
- 64-bit preload library gets passed to 32-bit child processes (Steam, Wine32), causing `wrong ELF class: ELFCLASS64` errors
- MangoHud config path may not be found when loaded via LD_PRELOAD

Setting `MANGOHUD=1` instead activates MangoHud through its Vulkan implicit layer (`/usr/share/vulkan/implicit_layer.d/MangoHud.x86_64.json`), which the Vulkan loader handles correctly for both 32-bit and 64-bit applications.

### Why Steam Gets Special Treatment

Steam launches many child processes: the Steam client itself (64-bit), game processes (may be 32-bit), the Steam runtime, and Proton/Wine containers. Wrapping the entire Steam client with `gamemoderun` causes:

- `libgamemodeauto.so.0` (64-bit) gets preloaded into 32-bit child processes
- This produces `wrong ELF class: ELFCLASS64` errors for every 32-bit subprocess

The solution: launch Steam without `gamemoderun`, and configure GameMode/MangoHud per-game through Steam's Launch Options instead.

---

## Supported Launchers

### Steam

```bash
~/launch-game.sh steam
```

**What happens:** Steam launches with `MANGOHUD=1` set globally. CPU governor is set to performance. GameMode is NOT wrapped around Steam itself (see [Steam Per-Game Configuration](#steam-per-game-configuration)).

**Post-launch:** Configure MangoHud and GameMode per-game through Steam's Launch Options.

### Lutris

```bash
~/launch-game.sh lutris
```

**What happens:** The resolver checks if `lutris` exists as a native binary. If not, it checks for Flatpak `net.lutris.Lutris` and launches via `flatpak run`. CPU governor, GameMode, and MangoHud are all applied.

**Note:** Lutris manages its own Wine/DXVK versions. MangoHud configured via this launcher applies to Lutris itself and any games it launches.

### Heroic Games Launcher

```bash
~/launch-game.sh heroic
```

**What happens:** Resolves to `flatpak run com.heroicgameslauncher.hgl` if installed as Flatpak (the typical installation method). All performance enhancements applied.

### Discord

```bash
~/launch-game.sh discord
```

**What happens:** Resolves to Flatpak `com.discordapp.Discord` if not available as a native binary. While not a game launcher, running Discord through this script ensures CPU performance mode is active during gaming sessions.

### Wine / Proton Games (Direct)

```bash
# Launch a Windows executable via Wine
~/launch-game.sh wine /path/to/game.exe

# With specific Wine prefix
WINEPREFIX=~/.wine-gaming ~/launch-game.sh wine /path/to/game.exe
```

**What happens:** Wine is wrapped with `gamemoderun` (if available). MangoHud is enabled via environment variable. The Wine executable receives all arguments.

### Native Linux Games

```bash
# Launch a native game binary
~/launch-game.sh /path/to/game

# With arguments
~/launch-game.sh /path/to/game --fullscreen --resolution=1920x1080
```

**What happens:** The game binary is wrapped with `gamemoderun` and launched with `MANGOHUD=1`. CPU governor is set to performance.

### Any Other Application

```bash
# The launcher works with any executable
~/launch-game.sh /usr/bin/some-application --arg1 --arg2
```

---

## Steam Per-Game Configuration

Since Steam cannot be wrapped with `gamemoderun` globally (see [Technical Details](#technical-details)), you should configure performance tools per-game through Steam's Launch Options.

### Setting Launch Options

1. Open Steam
2. Right-click the game in your library
3. Select **Properties**
4. In the **Launch Options** field, enter one of:

| Configuration | Launch Options |
|--------------|---------------|
| MangoHud + GameMode | `gamemoderun mangohud %command%` |
| MangoHud only | `mangohud %command%` |
| GameMode only | `gamemoderun %command%` |
| MangoHud + GameMode + Gamescope | `gamemoderun gamescope -f -- mangohud %command%` |

### Why This Works Per-Game but Not Globally

When Steam launches an individual game, that game process is a single architecture (either 32-bit or 64-bit). The `mangohud` and `gamemoderun` wrappers can correctly set LD_PRELOAD for that specific architecture. The problem only occurs when wrapping Steam itself, which spawns mixed-architecture children.

### MangoHud Toggle

Once configured, MangoHud can be toggled in-game:

- **Default keybind:** `Shift+F12` (configurable in `~/.config/MangoHud/MangoHud.conf`)
- **Display position:** Top-left by default
- **What's shown:** GPU/CPU stats, temperatures, RAM usage, FPS, frame timing

---

## Automatic Enhancements

### CPU Governor Management

| Feature | Details |
|---------|---------|
| **Trigger** | Always (if cpupower is available) |
| **Action** | Sets governor to "performance" on launch |
| **Restore** | Returns to original governor on exit (even on crash/SIGINT) |
| **Fallback** | Direct sysfs write if cpupower unavailable |
| **Requires** | `cpupower` command or write access to `/sys/devices/system/cpu/*/cpufreq/` |

### GameMode

| Feature | Details |
|---------|---------|
| **Trigger** | Binary `gamemoderun` found AND `libgamemodeauto.so.0` in `ldconfig -p` |
| **Action** | Wraps game command with `gamemoderun` |
| **Skipped for** | Steam (use per-game Launch Options instead) |
| **What it does** | Process priority boost, I/O scheduler tuning, CPU governor, GPU optimization |
| **Install if missing** | `sudo apt install gamemode libgamemode0 libgamemode0:i386` |

### MangoHud

| Feature | Details |
|---------|---------|
| **Trigger** | `mangohud` binary found OR Vulkan layer file exists |
| **Action** | Sets `MANGOHUD=1` and `MANGOHUD_DLSYM=1` environment variables |
| **Config file** | `~/.config/MangoHud/MangoHud.conf` |
| **Toggle** | `Shift+F12` in-game (default) |
| **Install if missing** | `sudo apt install mangohud mangohud:i386` |

---

## Flatpak Resolution

The launcher includes an intelligent command resolver that handles applications installed via Flatpak. This solves two common problems:

1. **"command not found"** — Flatpak apps don't create binaries in `$PATH` by default
2. **URI parsing errors** — Apps like Lutris interpret empty arguments as invalid URIs (`[''] is not a valid URI`)

### Resolution Logic

For each known application, the resolver follows this priority:

1. Check if a native binary exists in `$PATH` → use it
2. Check if Flatpak app is installed → use `flatpak run <app-id>`
3. Fall back to the original command (may fail if app not installed)

### Supported Flatpak Mappings

| Command | Native Binary | Flatpak ID |
|---------|--------------|------------|
| `lutris` | `/usr/bin/lutris` | `net.lutris.Lutris` |
| `heroic` | `/usr/bin/heroic` | `com.heroicgameslauncher.hgl` |
| `discord` | `/usr/bin/discord` | `com.discordapp.Discord` |

### How It Appears

When Flatpak resolution activates, you'll see:

```
  Resolved: lutris → flatpak run net.lutris.Lutris
```

---

## Environment Variables

The launcher sets or uses the following environment variables:

| Variable | Value | Purpose |
|----------|-------|---------|
| `MANGOHUD` | `1` | Activates MangoHud via Vulkan implicit layer |
| `MANGOHUD_DLSYM` | `1` | Enables MangoHud's dlsym interception for OpenGL |
| `ENABLE_VKBASALT` | `1` | Activates vkBasalt post-processing (if configured separately) |
| `WINEPREFIX` | User-defined | Wine prefix for Windows game (set before calling launcher) |
| `DXVK_HUD` | User-defined | Alternative HUD for DXVK games |

### Setting Additional Variables

You can set environment variables before calling the launcher:

```bash
# Use a specific Wine prefix
WINEPREFIX=~/.wine-gaming ~/launch-game.sh wine game.exe

# Enable vkBasalt effects
ENABLE_VKBASALT=1 ~/launch-game.sh /path/to/game

# Custom MangoHud config
MANGOHUD_CONFIG="fps,gpu_temp,cpu_temp" ~/launch-game.sh steam
```

---

## Command Reference

```
Usage: ~/launch-game.sh [OPTIONS] <game-command> [args...]

Options:
  --help, -h          Show help message and exit

Launcher Shortcuts:
  steam               Launch Steam client
  lutris              Launch Lutris (auto-resolves Flatpak)
  heroic              Launch Heroic Games Launcher (auto-resolves Flatpak)
  discord             Launch Discord (auto-resolves Flatpak)

Direct Launch:
  wine <path>         Launch Windows game via Wine
  /path/to/game       Launch native Linux game
  gamescope -- %cmd%  Launch via Gamescope compositor

Examples:
  ~/launch-game.sh steam
  ~/launch-game.sh lutris
  ~/launch-game.sh heroic
  ~/launch-game.sh wine ~/.wine/drive_c/Games/game.exe
  ~/launch-game.sh /opt/games/native-game --fullscreen
  WINEPREFIX=~/.wine-elden ~/launch-game.sh wine game.exe
```

---

## Troubleshooting

### MangoHud CPU Temperature Warning

```
[MANGOHUD] [error] [cpu.cpp:461] Could not find cpu temp sensor location
```

**Cause:** No hardware monitoring sensor exposed. Common in VMs or systems without `lm-sensors`.
**Impact:** Cosmetic only — MangoHud still works; CPU temp just won't display.
**Fix:** Install sensor support: `sudo apt install lm-sensors && sudo sensors-detect`

### Lutris URI Error

```
[''] is not a valid URI
```

**Cause:** Lutris interprets empty command-line arguments as an invalid URI. This occurred in pre-v2.6.0 versions of the launcher.
**Fix:** update to v3.5.0+ which includes the Flatpak resolver and empty-argument fix. Re-run the setup script or regenerate the launcher.

### "command not found" for Heroic/Lutris

**Cause:** App was installed via Flatpak, which doesn't create binaries in `$PATH`.
**Fix:** update to v3.5.0+ which includes automatic Flatpak resolution. Or launch directly: `flatpak run com.heroicgameslauncher.hgl`

### CPU Governor Permission Denied

```
sudo cpupower frequency-set -g performance
```

**Cause:** `cpupower` requires root privileges for governor changes.
**Fix:** Either run the launcher with a `cpupower` sudoers entry or ensure the `cpupower` package is installed: `sudo apt install linux-cpupower`

### GameMode "cannot open shared object"

```
libgamemodeauto.so.0: cannot open shared object file
```

**Cause:** GameMode library not installed or not in `ldconfig` cache.
**Fix:** Install both architectures: `sudo apt install libgamemode0 libgamemode0:i386 && sudo ldconfig`

### MangoHud Not Appearing In-Game

**Possible causes and fixes:**

1. **Vulkan layer not installed:** Check `/usr/share/vulkan/implicit_layer.d/MangoHud.x86_64.json` exists
2. **OpenGL game:** MangoHud's Vulkan layer only works with Vulkan/DXVK games. For OpenGL, use `mangohud` wrapper in Steam Launch Options
3. **Config toggle:** MangoHud may be loaded but hidden. Press `Shift+F12` to toggle
4. **32-bit game:** Install 32-bit MangoHud: `sudo apt install mangohud:i386`

### Script Not Found

```
bash: /home/user/launch-game.sh: No such file or directory
```

**Cause:** The launcher wasn't created during setup, or was deleted.
**Fix:** Re-run the setup script, or run just the launcher creation: `sudo python3 debian_gaming_setup.py --launcher-only` (if supported) or re-run the full setup.

---

## Technical Details

### Architecture

The launcher uses `exec` to replace the shell process with the game process. This means:

- No extra shell process lingering in the background
- Signal handling (Ctrl+C) goes directly to the game
- Exit code is the game's exit code
- Cleanup runs via `trap EXIT` before `exec`

### Multilib Safety

The fundamental challenge in Linux gaming is that Steam and Wine frequently launch 32-bit child processes from a 64-bit parent. When `LD_PRELOAD` is set with a 64-bit library path, those 32-bit children fail with `wrong ELF class: ELFCLASS64`.

The launcher avoids this by:

1. Using `MANGOHUD=1` (Vulkan layer) instead of `LD_PRELOAD` for MangoHud
2. Validating `libgamemodeauto.so.0` exists in `ldconfig` before enabling GameMode
3. Not wrapping Steam itself with `gamemoderun` — instead advising per-game Launch Options
4. Splitting resolved commands into proper arrays for `exec` (prevents word-splitting issues)

### File Locations

| File | Purpose |
|------|---------|
| `~/launch-game.sh` | The launcher script itself |
| `~/.config/MangoHud/MangoHud.conf` | MangoHud configuration |
| `~/.config/vkBasalt/vkBasalt.conf` | vkBasalt configuration |
| `/usr/share/vulkan/implicit_layer.d/` | Vulkan layer registration |

---

## Version History

| Version | Changes |
|---------|---------|
| v3.3.0 | Automated test coverage for launcher syntax validation (bash -n in CI/CD) |
| v3.0.0 | Eliminated eval in cleanup handler, replaced CLEANUP_TASKS with GOVERNOR_RESTORE_METHOD |
| v2.6.0 | Flatpak-aware command resolver, `--help` flag, empty-arg fix, LAUNCH_CMD array split |
| v2.5.0 | Rewritten: MANGOHUD=1 env var, ldconfig validation, Steam-specific handling, MangoHud config creation |
| v2.0.0 | Initial version with LD_PRELOAD (known multilib issues) |

---

*Part of the [Debian Gaming Setup Script](https://github.com/Sandler73/Debian-Gaming-Setup-Project) project.*
