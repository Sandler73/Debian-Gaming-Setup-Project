# Frequently Asked Questions (FAQ)

## Debian Gaming Setup Script — Comprehensive FAQ

**Version:** 2.6.0 | **Last Updated:** February 2026

---

## Table of Contents

- [General](#general)
- [Installation](#installation)
- [GPU & Drivers](#gpu--drivers)
- [Gaming Platforms](#gaming-platforms)
- [Performance Tools](#performance-tools)
- [Compatibility & Wine](#compatibility--wine)
- [Maintenance & Updates](#maintenance--updates)
- [Troubleshooting](#troubleshooting)
- [Waydroid & Android Gaming](#waydroid--android-gaming)
- [Advanced Topics](#advanced-topics)
- [Security & Privacy](#security--privacy)
- [Contributing](#contributing)

---

## General

### What is the Debian Gaming Setup Script?

It is a single-file Python utility that automates the installation and configuration of gaming platforms, GPU drivers, performance tools, and system optimizations across all Debian-based Linux distributions. It replaces what would otherwise be hours of manual package installation, PPA management, and configuration file editing.

### Which distributions are supported?

The script supports all Debian-based distributions, including Ubuntu (22.04, 24.04, 24.10), Linux Mint (21.x, 22.x), Debian (11, 12), Pop!_OS, Zorin OS, Elementary OS, and KDE neon. LMDE (Linux Mint Debian Edition) is also supported. Any distribution that uses `apt` as its package manager and is derived from Debian should work.

### What are the system requirements?

You need Python 3.7 or later (pre-installed on all modern Debian-based distros), root/sudo access for package installation, an active internet connection, and at least 2 GB of free disk space. 4+ GB RAM is recommended for a comfortable gaming experience.

### Does the script require any external Python dependencies?

No. The script uses only the Python standard library — no `pip install` required. This is a deliberate design choice to ensure the script runs on any fresh Debian-based installation without additional setup.

### Can I run the script multiple times?

Yes. The script includes pre-install detection for all components. On subsequent runs, it will detect already-installed software, show version information, and offer to reinstall or skip. Update mode (`--update`) is also available for refreshing existing installations.

### Does the script work in virtual machines?

Yes. The script detects VM environments (VMware, VirtualBox, KVM/QEMU, Hyper-V, Xen, Parallels) and installs appropriate guest tools. GPU performance will be limited by virtualization overhead, but the script configures the best available drivers for your virtual GPU.

### How long does a full installation take?

A complete interactive installation typically takes 30-45 minutes on a moderate internet connection. Automated mode with presets (`--preset complete -y`) can complete in 15-25 minutes. Dry-run mode (`--dry-run`) completes instantly and shows what would be installed without making any changes.

### Is there a GUI version?

Not yet. A Tkinter-based GUI frontend is planned for v3.0.0. Currently, the script operates entirely from the command line, with interactive prompts for each component.

---

## Installation

### How do I install the script?

```bash
# Download the script
wget https://github.com/Sandler73/Debian-Gaming-Setup-Project/raw/main/debian_gaming_setup.py

# Run interactively
sudo python3 debian_gaming_setup.py

# Or with a preset
sudo python3 debian_gaming_setup.py --preset standard -y
```

### What do the presets install?

| Preset | Components |
|--------|-----------|
| `minimal` | GPU drivers, Steam, GameMode |
| `standard` | Minimal + Wine, Lutris, GameMode, MangoHud |
| `complete` | Standard + Heroic, ProtonUp-Qt, GE-Proton, vkBasalt, controllers, Discord, Mumble |
| `streaming` | Complete + OBS Studio, streaming tools |

### Can I install only specific components?

Yes. Use targeted mode with specific flags:

```bash
# Just Steam and MangoHud
sudo python3 debian_gaming_setup.py --steam --mangohud

# Just GPU drivers
sudo python3 debian_gaming_setup.py --nvidia
# or
sudo python3 debian_gaming_setup.py --amd
```

### What happens if the installation is interrupted?

The script records installation state as it progresses. If interrupted (power loss, Ctrl+C, network failure), you can re-run it and it will detect what was already installed. The rollback system can also undo partial installations with `--rollback`.

### Can I preview what the script will do without making changes?

Yes. Use dry-run mode:

```bash
sudo python3 debian_gaming_setup.py --preset complete --dry-run
```

This shows every command that would be executed, every package that would be installed, and every file that would be created — without actually doing anything.

### Do I need to reboot after installation?

A reboot is recommended after GPU driver installation (especially NVIDIA proprietary drivers) and after kernel-level changes. The script will advise when a reboot is needed in its completion summary.

---

## GPU & Drivers

### How does the script detect my GPU?

The script uses a multi-method detection approach: `lspci` output for PCI device identification, existing kernel module checks (`lsmod`), and package availability queries. It identifies NVIDIA, AMD, and Intel GPUs, including hybrid configurations.

### My NVIDIA GPU isn't being detected. What should I do?

First, verify your GPU is visible to the system: `lspci | grep -i nvidia`. If it appears but the script doesn't detect it, try running with the `--nvidia` flag explicitly. If `lspci` shows nothing, your GPU may not be properly seated or may need a BIOS/UEFI configuration change.

### Should I use NVIDIA proprietary or open-source drivers?

For gaming, NVIDIA proprietary drivers are strongly recommended. They provide significantly better performance, Vulkan support, and compatibility with tools like GreenWithEnvy. The open-source Nouveau driver has limited gaming performance. The script installs proprietary drivers by default when `--nvidia` is specified.

### How do I switch between NVIDIA and AMD GPUs?

If you've physically changed your GPU, run the script again with the appropriate flag (`--nvidia` or `--amd`). The script will install the correct drivers. You may need to remove old drivers first — the script handles this for most cases, but a manual `sudo apt purge nvidia-*` may be needed for NVIDIA-to-AMD transitions.

### Does the script support hybrid GPU laptops (NVIDIA Optimus / AMD Switchable)?

The script installs the correct drivers for detected GPUs but does not currently configure GPU switching (PRIME profiles, optimus-manager). After installation, you can use `prime-select` for NVIDIA Optimus or `switcheroo-control` for AMD hybrid configurations.

### What about Intel Arc GPUs?

Intel Arc GPUs are supported through the Mesa driver stack. The script installs the latest available Mesa drivers for Intel hardware. Vulkan support for Intel Arc is handled through `intel-media-va-driver` and Mesa's ANV Vulkan driver.

### Do I need Vulkan for gaming?

For modern gaming through Proton/Wine/DXVK, Vulkan is essential. DXVK translates DirectX 9/10/11 calls to Vulkan, and VKD3D-Proton translates DirectX 12 to Vulkan. The script installs `vulkan-tools` and the appropriate Vulkan drivers for your GPU.

---

## Gaming Platforms

### How do I launch Steam after installation?

Steam can be launched from your application menu, from the terminal with `steam`, or through the performance launcher with `~/launch-game.sh steam` for CPU governor and MangoHud enhancements.

### Steam installed but won't start. What should I do?

Common fixes include: running `steam --reset` to clear configuration, checking that 32-bit libraries are installed (`sudo dpkg --add-architecture i386 && sudo apt update && sudo apt install libgl1-mesa-dri:i386`), and verifying your GPU drivers are installed correctly with `vulkaninfo`.

### What is Lutris and when should I use it?

Lutris is a game manager that handles installation and configuration of games from various sources (GOG, Epic, Humble Bundle, etc.) using different runners (Wine, DOSBox, emulators). Use Lutris when you want to run non-Steam Windows games or retro games. The script installs Lutris as a Flatpak.

### What is the Heroic Games Launcher?

Heroic is an open-source launcher for the Epic Games Store, GOG, and Amazon Prime Gaming. It provides a native Linux interface for managing and launching games from these platforms using Wine/Proton. Installed as a Flatpak.

### How do I play Roblox on Linux?

The script includes SOBER, a community-maintained Roblox client for Linux, installed as a Flatpak (`org.vinegarhq.Sober`). After installation, launch it from your application menu. Note that Roblox anti-cheat may occasionally block Linux clients.

### Can I run Android games on my Linux desktop?

Yes, through Waydroid, which runs a full Android container. The script can install and configure Waydroid, but it requires a Wayland session (not X11). After installation, initialize with `waydroid init` and access the Android interface through your Wayland compositor.

### What is ProtonUp-Qt?

ProtonUp-Qt is a GUI tool for managing Proton and Wine versions. It lets you install, update, and switch between different versions of GE-Proton, Wine-GE, and other compatibility layers without manually downloading and extracting files.

---

## Performance Tools

### What does MangoHud show?

MangoHud displays a customizable overlay with real-time performance metrics including: FPS, frame timing, GPU utilization and temperature, CPU utilization and temperature per-core, RAM usage, VRAM usage, and more. Toggle visibility with `Shift+F12` (default).

### How do I configure MangoHud?

Edit `~/.config/MangoHud/MangoHud.conf`. The script creates a default configuration during installation. You can also use Goverlay for a graphical configuration interface. Common settings include `position` (overlay location), `font_size`, and which metrics to display.

### What is GameMode and do I need it?

GameMode is a daemon by Feral Interactive that optimizes your system when a game is running. It temporarily sets CPU governor to performance, adjusts I/O scheduling priority, enables GPU performance modes, and tunes the process scheduler. It provides measurable FPS improvements in many games and is recommended for all setups.

### What is vkBasalt?

vkBasalt is a Vulkan post-processing layer that applies visual effects like sharpening (CAS), FXAA anti-aliasing, SMAA, and ReShade-compatible shaders. It can improve visual quality in games, particularly on lower-end hardware or older titles. Configure in `~/.config/vkBasalt/vkBasalt.conf`.

### What is GreenWithEnvy (GWE)?

GreenWithEnvy is an NVIDIA GPU management tool (similar to MSI Afterburner on Windows). It allows you to monitor GPU temperature, clock speeds, fan curves, and power consumption. It can also set custom fan profiles. Requires NVIDIA proprietary drivers.

### My MangoHud overlay isn't appearing. What should I check?

Check these in order: (1) MangoHud is installed: `mangohud --version`. (2) The Vulkan layer exists: `ls /usr/share/vulkan/implicit_layer.d/MangoHud*`. (3) The game uses Vulkan/DXVK (MangoHud doesn't work with native OpenGL unless using the `mangohud` wrapper). (4) Press `Shift+F12` — it may be loaded but toggled off. (5) For 32-bit games, install `mangohud:i386`.

---

## Compatibility & Wine

### What is Wine and how does it work?

Wine is a compatibility layer that translates Windows system calls to Linux system calls, allowing many Windows applications and games to run on Linux. It does not emulate Windows — it provides native-speed translation. The script installs Wine Staging, which includes the latest gaming-related patches.

### What is Proton?

Proton is Valve's version of Wine, integrated into Steam. It includes DXVK (DirectX-to-Vulkan translation), VKD3D-Proton (DirectX 12 translation), and additional patches for game compatibility. When you click "Play" on a Windows game in Steam, Proton handles the translation automatically.

### What is GE-Proton and why should I use it?

GE-Proton (Glorious Eggroll) is a community-maintained Proton build that includes additional patches, fixes, and features not yet in official Proton. It often provides better compatibility for problematic games. The script installs it from GitHub with SHA512 checksum verification.

### How do I check if my game works on Linux?

Visit [ProtonDB](https://www.protondb.com/) and search for your game. Ratings range from Platinum (works perfectly) through Gold, Silver, Bronze, to Borked (doesn't work). ProtonDB also shows which Proton version and settings other users found successful.

### Do anti-cheat games work on Linux?

It depends on the game. Easy Anti-Cheat (EAC) and BattlEye both have Linux support, but game developers must enable it. Some games with anti-cheat work on Linux (e.g., Elden Ring, Apex Legends), while others don't (e.g., Destiny 2, PUBG). Check ProtonDB for your specific game.

### How do I manage Wine prefixes?

A Wine prefix is a directory containing a virtual Windows installation. By default, it's `~/.wine`. For game-specific prefixes, set `WINEPREFIX` before launching: `WINEPREFIX=~/.wine-game1 wine game.exe`. Lutris automatically manages separate prefixes for each game.

---

## Maintenance & Updates

### How do I update all gaming packages?

```bash
sudo python3 debian_gaming_setup.py --update
```

This updates APT packages, Flatpak applications, and checks for new GE-Proton releases.

### How do I update the script itself?

```bash
sudo python3 debian_gaming_setup.py --self-update
```

This queries the GitHub repository for newer versions, validates the download, and replaces the current script with a backup preserved.

### How do I roll back changes?

```bash
# Preview what would be rolled back
sudo python3 debian_gaming_setup.py --rollback --dry-run

# Execute rollback
sudo python3 debian_gaming_setup.py --rollback
```

The rollback system reverses the last installation session's changes in LIFO (last-in-first-out) order: removes packages, restores config files, cleans up repositories.

### Where are the log files?

Installation logs are written to `~/gaming_setup.log`. State information is in `~/gaming_setup_state.json`. Rollback manifests are in `~/gaming_setup_rollback.json`. These files are owned by your user account, not root.

### How do I check the system health after installation?

The script runs an automatic post-install health check. To run it manually:

```bash
sudo python3 debian_gaming_setup.py --health-check
```

This verifies installed packages, checks binary availability, validates Flatpak installations, and tests GPU driver functionality.

---

## Troubleshooting

### "dpkg lock" or "Could not get lock" errors

Another package manager (apt, Software Center, unattended-upgrades) is running. Wait for it to finish, or check with `ps aux | grep -E 'apt|dpkg'`. The script includes dpkg lock detection and will warn you before proceeding.

### "E: Unable to locate package" errors

The package may not be available for your distribution or version. The script checks package availability before installation and provides fallback options. Try running `sudo apt update` first, then re-run the script.

### Steam games crash on launch

Common solutions: (1) Verify game files in Steam. (2) Try a different Proton version (right-click game → Properties → Compatibility). (3) Check ProtonDB for game-specific fixes. (4) Install missing 32-bit libraries: `sudo apt install libgl1-mesa-dri:i386 mesa-vulkan-drivers:i386`. (5) Check the game's log in `~/.steam/steam/steamapps/common/<game>/`.

### NVIDIA driver installation failed

Try these steps: (1) Ensure Secure Boot is disabled in BIOS (NVIDIA proprietary drivers aren't signed by default). (2) Remove existing NVIDIA packages: `sudo apt purge nvidia-* libnvidia-*`. (3) Re-run the script with `--nvidia`. (4) Check `dmesg | grep -i nvidia` for kernel-level errors.

### Wine/Proton games show black screen

This usually indicates a DirectX/Vulkan translation issue. Try: (1) Use GE-Proton instead of default Proton. (2) Add `PROTON_USE_WINED3D=1 %command%` to Steam Launch Options (uses OpenGL instead of Vulkan — slower but more compatible). (3) Install `vulkan-tools` and run `vulkaninfo` to verify Vulkan is working.

### Sound doesn't work in games

Check these: (1) PulseAudio/PipeWire is running: `pactl info`. (2) For Wine games, try `winetricks sound=pulse`. (3) For Steam, check Settings → Audio. (4) For Flatpak apps, verify PulseAudio permission: `flatpak permission-list`.

### "Wrong ELF class: ELFCLASS64" errors

This indicates a 64-bit library being loaded into a 32-bit process. The performance launcher (v2.5.0+) fixes this by using `MANGOHUD=1` instead of LD_PRELOAD. If using older scripts, update the launcher or configure MangoHud through Steam Launch Options instead.

### Games run but performance is poor

Checklist: (1) GPU driver is correct: `glxinfo | grep "OpenGL renderer"` should show your GPU, not "llvmpipe". (2) Vulkan is working: `vulkaninfo --summary`. (3) GameMode is active: `gamemoded --status`. (4) CPU governor is "performance": `cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor`. (5) Compositor is disabled during gaming (varies by desktop environment). (6) Use the performance launcher: `~/launch-game.sh <game>`.

---

## Waydroid & Android Gaming

### What is Waydroid?

Waydroid is a container-based approach to running a full Android system on Linux. Unlike emulators, it shares the Linux kernel, providing near-native performance for Android applications including games.

### Why does Waydroid require Wayland?

Waydroid uses the Wayland protocol for display output. It does not work under X11. If you're using an X11 session, you'll need to switch to a Wayland session (available in most modern desktops like GNOME on Wayland, KDE Plasma Wayland). Check your session type with `echo $XDG_SESSION_TYPE`.

### How do I install Google Play on Waydroid?

After Waydroid initialization, Google Play services can be added using community scripts. The setup script provides guidance during installation. Note that Google Play certification and SafetyNet may not pass, which affects some apps.

### Waydroid won't start. What should I check?

Verify: (1) You're in a Wayland session. (2) Kernel modules are loaded: `lsmod | grep binder`. (3) Waydroid is initialized: `waydroid status`. (4) Try re-initializing: `sudo waydroid init -f`. (5) Check logs: `waydroid log`.

---

## Advanced Topics

### Can I use custom Proton versions?

Yes. Install GE-Proton through the script or use ProtonUp-Qt to manage multiple versions. In Steam, right-click a game → Properties → Compatibility → "Force the use of a specific Steam Play compatibility tool" and select your preferred version.

### How do I use Gamescope?

Gamescope is a micro-compositor that provides features like resolution scaling, FPS limiting, and frame timing. Use it through Steam Launch Options: `gamescope -f -w 1920 -h 1080 -- %command%`. It's particularly useful for games with problematic windowing behavior.

### Can I stream games from my Linux PC?

Yes. The script can install OBS Studio (with the `streaming` preset) for local recording and streaming. For remote play, Steam Remote Play works natively. Sunshine/Moonlight is another option for NVIDIA GPU-accelerated streaming.

### How do I overclock my GPU on Linux?

For NVIDIA: Use GreenWithEnvy (installed by the script) for a GUI interface, or `nvidia-settings` for command-line control. For AMD: Use `corectrl` or modify sysfs parameters. Be cautious with overclocking — monitor temperatures closely.

### Can I use VR headsets on Linux?

VR support on Linux is improving but limited. SteamVR works with Valve Index and some other headsets. Monado provides an open-source OpenXR runtime. The script does not currently install VR-specific software, but GPU drivers and Vulkan support are prerequisites.

---

## Security & Privacy

### Why does the script need root access?

Package installation (`apt-get install`), repository management (`add-apt-repository`), driver installation, system configuration changes (sysctl, CPU governor), and file permission management all require root privileges. The script does not run as root for user-space operations like game launches.

### Does the script collect any data?

No. The script does not collect, transmit, or store any personal data, telemetry, or usage statistics. All operations are local. Network access is used only for downloading packages and checking for updates.

### What repositories does the script add?

Depending on your selections, the script may add: WineHQ repository (for latest Wine), Flathub (for Flatpak applications), and GPU-specific PPAs (NVIDIA, Mesa). All added repositories are official sources maintained by their respective projects. The script validates repository URLs before adding them.

### Is the script safe to use?

The script follows security best practices: no `shell=True` in subprocess calls (with documented exceptions), no `eval`/`exec` on user input, specific exception handling, input validation, SHA512 checksum verification for downloads, and syntax validation for self-updates. See [SECURITY.md](SECURITY.md) for full details.

---

## Contributing

### How do I report a bug?

Open an issue on [GitHub](https://github.com/Sandler73/Debian-Gaming-Setup-Project/issues) with: your distribution and version, the command you ran, the complete error message, and the contents of `~/gaming_setup.log`.

### How do I request a feature?

Open a feature request issue on GitHub describing what you'd like, why it would be useful, and any implementation ideas you have.

### Can I contribute code?

Yes! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. We welcome bug fixes, new platform support, distribution compatibility improvements, and documentation enhancements.

### How do I test changes locally?

Use dry-run mode to verify behavior without making system changes:

```bash
sudo python3 debian_gaming_setup.py --dry-run --preset complete
```

For development, the `--dry-run` flag combined with specific component flags lets you test individual installation paths.

---

*Part of the [Debian Gaming Setup Script](https://github.com/Sandler73/Debian-Gaming-Setup-Project) project.*
*For additional support, see the [Usage Guide](Usage_Guide.md), [Quick Start](Quick_Start.md), and [Launcher Guide](LAUNCHER_GUIDE.md).*
