# Usage Guide v2.1

**Complete reference for all features and command-line options**

This guide provides detailed documentation for every feature, option, and use case of the Debian-Based Gaming Setup Script.

---

## 📚 Table of Contents

- [Basic Usage](#basic-usage)
- [All Command-Line Options](#all-command-line-options)
- [Usage Examples by Scenario](#usage-examples-by-scenario)
- [Platform Details](#platform-details)
- [Utility Details](#utility-details)
- [Performance Optimization](#performance-optimization)
- [Advanced Configuration](#advanced-configuration)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

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
--nvidia                Install NVIDIA proprietary drivers
--amd                   Install AMD Mesa drivers
--intel                 Install Intel Mesa drivers
--vm-tools              Install VM guest tools (auto-detected type)
```

**NVIDIA:** Latest stable drivers via ubuntu-drivers, nvidia-settings, nvidia-prime  
**AMD:** mesa-vulkan-drivers, libvulkan1, vulkan-tools  
**Intel:** mesa-vulkan-drivers, intel-media-va-driver, i965-va-driver  
**VM:** Detects VMware/VirtualBox/KVM/Hyper-V and installs appropriate tools

### Gaming Platform Options

```
--steam                 Install Valve Steam
--lutris                Install Lutris (Epic, GOG, Battle.net)
--heroic                Install Heroic Games Launcher
--protonup              Install ProtonUp-Qt (Proton version manager)
--sober                 Install SOBER (Roblox on Linux) ✨
--waydroid              Install Waydroid (Android container) ✨
--all-platforms         Install all standard platforms (excludes specialized)
```

**--all-platforms includes:** Steam, Lutris, Heroic, ProtonUp-Qt  
**--all-platforms excludes:** SOBER, Waydroid (specialized use cases)

### Compatibility Layer Options

```
--wine                  Install Wine Staging (latest)
--winetricks            Install Winetricks (Wine configuration tool)
--ge-proton             Install GE-Proton automatically (latest from GitHub)
--dxvk                  Show DXVK installation information
--vkd3d                 Show VKD3D-Proton installation information
```

### Performance Tool Options

```
--gamemode              Install Feral GameMode
--mangohud              Install MangoHud performance overlay
--goverlay              Install Goverlay (MangoHud GUI)
--gwe                   Install GreenWithEnvy (NVIDIA GPU control) ✨
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
--mod-managers          Install mod management tools ✨
--controllers           Install controller support (Xbox, PlayStation)
--essential             Install essential gaming packages
--codecs                Install multimedia codecs
```

### System Optimization Options

```
--optimize              Apply gaming system optimizations
--launcher              Create performance launcher script
```

### Maintenance Options

```
--rollback              Rollback previous installation (framework)
--cleanup               Clean up installation files and logs
```

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
sudo python3 debian_gaming_setup.py -y \
    --nvidia --steam --obs --discord \
    --mangohud --gamemode --optimize
```

**10. Minimal Setup (Steam Only)**
```bash
sudo python3 debian_gaming_setup.py -y \
    --steam --gamemode --essential
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
ENABLE_VKBASALT=1 %command%     # Post-processing effects
```

### Lutris

**Installation:** Flatpak (net.lutris.Lutris)  
**Size:** ~200MB  
**Features:** Epic, GOG, Battle.net, Origin, Ubisoft, Emulators  

**Usage:**
1. Browse: https://lutris.net/games
2. Click Install on game page
3. Follow on-screen instructions

**Supports:** Wine games, emulators, native Linux games

### Heroic Games Launcher

**Installation:** Flatpak (com.heroicgameslauncher.hgl)  
**Size:** ~150MB  
**Features:** Epic Games Store, GOG, Amazon Prime Gaming  

**Usage:**
- Login with Epic/GOG accounts
- Download and install games
- Integrated Wine/Proton support

### SOBER (Roblox) ✨

**Installation:** Flatpak (org.vinegarhq.Sober)  
**Size:** ~100MB  
**Features:** Full Roblox client for Linux  

**Launch:** `flatpak run org.vinegarhq.Sober`  
**Performance:** Comparable to Windows  
**Limitations:** Some games may have anti-cheat issues  

### Waydroid (Android) ✨

**Installation:** APT package + repository  
**Size:** ~300MB  
**Features:** Full Android system (not emulation!)  

**Requirements:**
- Wayland session (best performance)
- Compatible kernel modules

**Post-Install:**
```bash
sudo waydroid init
waydroid session start
waydroid show-full-ui
```

**Use Cases:** Mobile games, Android apps  
**Limitations:** Best on Wayland, limited on X11, some games blocked by SafetyNet

---

## Utility Details

### GameMode

**What:** CPU/IO optimization daemon by Feral Interactive  
**Features:** Automatic performance mode, I/O priority, GPU performance  
**Usage:** Automatic in Lutris, manual with `gamemoderun`  

### MangoHud

**What:** Performance monitoring overlay  
**Features:** FPS, frame time, CPU/GPU usage, temperatures  
**Config:** `~/.config/MangoHud/MangoHud.conf`  
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
**Features:** Fan curves, overclocking, power limits, monitoring  
**Launch:** `flatpak run com.leinardi.gwe`  
**Sudo:** Required for overclocking features  

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

**Effects available:**
- CAS - Contrast Adaptive Sharpening
- FXAA - Fast anti-aliasing
- SMAA - Subpixel morphological AA
- LumaSharpen - Intelligent sharpening
- Vibrance - Color enhancement

### Mod Managers ✨

**Mod Organizer 2:** For Bethesda games (Skyrim, Fallout)  
**Vortex:** Official Nexus Mods manager  
**r2modman:** For Unity games (Risk of Rain 2, Valheim)  

**Installation:** Interactive prompts guide setup

---

## Performance Optimization

### CPU Optimization

**Manual:**
```bash
# Check current governor
cpupower frequency-info

# Set performance mode
sudo cpupower frequency-set -g performance

# Revert to powersave
sudo cpupower frequency-set -g powersave
```

**Automatic (via performance launcher):**
```bash
~/launch-game.sh steam  # Handles CPU governor automatically
```

### GPU Optimization

**NVIDIA (via GWE):**
- Monitor temperatures
- Create fan curves
- Adjust power limits
- Overclock (carefully!)

**AMD:**
```bash
# Check performance level
cat /sys/class/drm/card0/device/power_dpm_force_performance_level

# Set to high
echo "high" | sudo tee /sys/class/drm/card0/device/power_dpm_force_performance_level
```

### System Optimizations (Applied by --optimize)

**File watchers:** `fs.inotify.max_user_watches=524288`  
**Memory mapping:** `vm.max_map_count=2147483642`  
**CPU governor:** Performance mode systemd service  

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

## Troubleshooting

### Script Issues

**"Must be run with sudo"**
```bash
sudo python3 debian_gaming_setup.py
```

**Package installation fails**
```bash
sudo apt-get update
sudo apt-get upgrade
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
- Use performance launcher
- Enable GameMode
- Check MangoHud overlay

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
A: Yes, script checks versions and offers to update/reinstall.

**Q: Will this work on [distro]?**  
A: Works on any Debian-based distro (Ubuntu, Mint, Debian, Pop!_OS, etc.)

**Q: Can I uninstall components?**  
A: Yes, use standard package managers:
```bash
sudo apt-get remove package-name
flatpak uninstall app.id
```

---

**For more help:** See [README.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/README.md) and [Quick_Start.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/Quick_Start.md)

**Version:** 2.1.0 | Updated: January 2026
