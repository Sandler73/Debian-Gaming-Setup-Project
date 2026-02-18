# Quick Start Guide v2.5

**Get gaming on Linux in under 30 minutes**

This guide walks you through your first installation, from download to playing games.

---

## 📋 Before You Begin

### Prerequisites Checklist

- [ ] Debian-based Linux (Ubuntu 20.04+, Linux Mint 20+, Debian 11+, Pop!_OS, ElementaryOS, Zorin OS, Kali Linux)
- [ ] Sudo/root access
- [ ] Internet connection (stable)
- [ ] 10GB+ free disk space (5GB minimum)
- [ ] Terminal access (Ctrl+Alt+T)

### Know Your Hardware

**Check your GPU:**
```bash
lspci | grep -i vga
```

**Running in VM?** The script auto-detects VMware, VirtualBox, KVM, Hyper-V, Xen, and Parallels.

### Validate Your System ✨

Before installing, you can verify your system meets all requirements:
```bash
sudo python3 debian_gaming_setup.py --check-requirements
```

---

## 🚀 Five Installation Paths

### Path A: Interactive (Recommended for Beginners)
**Time:** 30-45 minutes | **Control:** Full | **Safety:** Highest

### Path B: Preset (Fastest Setup) ✨
**Time:** 15-20 minutes | **Control:** Curated bundles | **Safety:** High

### Path C: Automated (Experienced Users)
**Time:** 15-20 minutes | **Control:** Minimal | **Safety:** Test with dry-run first

### Path D: Test First (Cautious Users)
**Time:** 5 min test + 30 min install | **Control:** Full | **Safety:** Maximum

### Path E: Targeted (Specific Components)
**Time:** 5-15 minutes | **Control:** Precise | **Safety:** High

---

## 🎯 Path A: Interactive Installation

### Step 1: Download

```bash
cd ~/Downloads
wget https://raw.githubusercontent.com/Sandler73/Debian-Gaming-Setup-Project/main/debian_gaming_setup.py
```

### Step 2: Run

```bash
sudo python3 debian_gaming_setup.py
```

### Step 3: Follow Prompts

The script will:
1. **Validate system** — Checks disk space, RAM, architecture, dpkg lock ✨
2. **Detect your system** — Shows GPU, distribution, VM status
3. **Check network** — Verifies connectivity to package repositories ✨
4. **Update packages** — Updates system (5-10 minutes)
5. **Detect hardware** — Identifies GPU vendor dynamically ✨
6. **Ask about drivers** — Install NVIDIA/AMD/Intel/VM tools?
7. **Ask about platforms** — Install Steam, Lutris, etc?
8. **Ask about tools** — Discord, OBS, controllers?
9. **Run health check** — Verifies all installed components ✨
10. **Show summary** — Display what was installed
11. **Offer reboot** — Required for drivers

**Example prompts you'll see:**

```
✓ NVIDIA GPU detected (dynamically resolved)
Install NVIDIA drivers? (y/n): y

✓ Steam already installed (version: 1.0.0.78)
Update available: 1.0.0.78 → 1.0.0.79
Update Steam? (y/n): y

Install Lutris? (y/n): y
Install Heroic Games Launcher? (y/n): y
Install SOBER (Roblox on Linux)? (y/n): n
Install Waydroid (Android container)? (y/n): n
```

**What to answer:**
- **GPU Drivers:** `y` (if not in VM)
- **Steam:** `y` (essential for gaming)
- **Lutris:** `y` (for Epic, GOG, etc.)
- **GameMode:** `y` (performance boost)
- **MangoHud:** `y` (FPS counter)
- **SOBER:** `y` if you play Roblox
- **Waydroid:** `y` if you want Android apps
- **Optimizations:** `y` (desktop), `n` (laptop — CPU governor drains battery)

### Step 4: Reboot

```bash
sudo reboot
```

**Required for:** GPU drivers, kernel parameters, CPU governor

### Step 5: Verify

**Check GPU drivers:**
```bash
# NVIDIA
nvidia-smi

# AMD/Intel
glxinfo | grep "OpenGL renderer"
```

### Step 6: Configure Steam

1. Open Steam
2. Go to **Settings** → **Compatibility**
3. Enable **"Enable Steam Play for all other titles"**
4. Select **Proton Experimental**
5. Click **OK** and restart Steam

### Step 7: Play!

**Test games:**
- **Native:** Counter-Strike 2 (free), Portal 2
- **Proton:** Stardew Valley, Terraria, Hades

---

## ⚡ Path B: Preset Installation ✨

Presets are curated component bundles — the fastest way to a working gaming setup.

### Minimal (GPU + Steam Only)

```bash
wget https://raw.githubusercontent.com/Sandler73/Debian-Gaming-Setup-Project/main/debian_gaming_setup.py

sudo python3 debian_gaming_setup.py --preset minimal -y
sudo reboot
```

### Standard (Recommended for Most Users)

```bash
sudo python3 debian_gaming_setup.py --preset standard -y
sudo reboot
```

**Includes:** GPU drivers, Steam, Lutris, Heroic, ProtonUp-Qt, Wine, GameMode, MangoHud, codecs, system optimizations, performance launcher

### Complete (Everything)

```bash
sudo python3 debian_gaming_setup.py --preset complete -y
sudo reboot
```

**Includes:** All platforms (including SOBER, Waydroid), all tools, all communication apps, all performance tools, mod managers, controllers

### Streaming

```bash
sudo python3 debian_gaming_setup.py --preset streaming -y
sudo reboot
```

**Includes:** Standard + OBS Studio, Discord, Mumble

### Combine Presets with Flags

Presets are non-destructive overlays — you can add extra components:

```bash
# Standard preset plus Waydroid and vkBasalt
sudo python3 debian_gaming_setup.py --preset standard --waydroid --vkbasalt -y
```

---

## ⚡ Path C: Automated Installation

### NVIDIA Gaming PC (Complete)

```bash
wget https://raw.githubusercontent.com/Sandler73/Debian-Gaming-Setup-Project/main/debian_gaming_setup.py

sudo python3 debian_gaming_setup.py -y \
    --nvidia \
    --all-platforms \
    --wine \
    --ge-proton \
    --gamemode \
    --mangohud \
    --gwe \
    --vkbasalt \
    --discord \
    --obs \
    --controllers \
    --essential \
    --codecs \
    --optimize \
    --launcher

sudo reboot
```

### AMD Gaming PC

```bash
sudo python3 debian_gaming_setup.py -y \
    --amd \
    --all-platforms \
    --wine \
    --ge-proton \
    --gamemode \
    --mangohud \
    --vkbasalt \
    --discord \
    --essential \
    --codecs \
    --optimize

sudo reboot
```

### Intel Laptop (Battery-Friendly)

```bash
sudo python3 debian_gaming_setup.py -y \
    --intel \
    --steam \
    --lutris \
    --gamemode \
    --mangohud \
    --essential

sudo reboot
```

### Virtual Machine

```bash
sudo python3 debian_gaming_setup.py -y \
    --vm-tools \
    --steam \
    --lutris \
    --gamemode \
    --essential

# Don't forget to enable 3D acceleration in VM settings!
sudo reboot
```

### Specialized: Roblox Player

```bash
sudo python3 debian_gaming_setup.py -y \
    --sober \
    --essential \
    --controllers

# No reboot needed (Flatpak only)
```

### Specialized: Mobile Gaming

```bash
sudo python3 debian_gaming_setup.py -y \
    --waydroid \
    --controllers \
    --essential

# Requires Wayland session
sudo reboot
```

---

## 🧪 Path D: Test First (Dry-Run)

### Step 1: Test Installation

```bash
wget https://raw.githubusercontent.com/Sandler73/Debian-Gaming-Setup-Project/main/debian_gaming_setup.py

sudo python3 debian_gaming_setup.py --dry-run \
    --nvidia \
    --all-platforms \
    --optimize
```

**You'll see:**
```
═══════════════════════════════════════════
DRY RUN MODE - No changes will be made
═══════════════════════════════════════════

[DRY RUN] Would execute: apt-get update
[DRY RUN] Would execute: apt-get upgrade -y
[DRY RUN] Would install: nvidia-driver-*
[DRY RUN] Would install: steam-installer
...
```

### Step 2: Review Output

Look for:
- ✓ Components that would be installed
- ✓ Commands that would be executed
- ⚠ Any warnings or potential issues

### Step 3: Run For Real

```bash
# If everything looks good, run without --dry-run
sudo python3 debian_gaming_setup.py -y \
    --nvidia \
    --all-platforms \
    --optimize

sudo reboot
```

### Dry-Run with Presets ✨

```bash
# Preview what a preset would install
sudo python3 debian_gaming_setup.py --preset complete --dry-run
```

---

## 🎯 Path E: Targeted Installation

Install only specific components without any prompts:

```bash
# Just Steam and GameMode
sudo python3 debian_gaming_setup.py --steam --gamemode -y

# Just Wine ecosystem
sudo python3 debian_gaming_setup.py --wine --winetricks --dxvk --vkd3d -y

# Just performance tools
sudo python3 debian_gaming_setup.py --gamemode --mangohud --goverlay -y
```

---

## 🎮 After Installation

### 1. Essential Post-Install Steps

**Configure Steam (Required):**
1. Launch Steam
2. Settings → Compatibility
3. Enable Steam Play for all titles
4. Select Proton Experimental
5. Restart Steam

**Configure vkBasalt (Optional):**
```bash
# Already configured by script, but you can customize
nano ~/.config/vkBasalt/vkBasalt.conf
```

Enable for games:
```
# Steam launch options:
ENABLE_VKBASALT=1 %command%
```

**Configure MangoHud (Optional):**
The installer creates a default config at `~/.config/MangoHud/MangoHud.conf` ✨

```bash
# Customize if desired
nano ~/.config/MangoHud/MangoHud.conf
```

Example config:
```ini
fps
frame_timing=1
cpu_temp
gpu_temp
position=top-left
```

Enable for games:
```
# Steam launch options:
mangohud %command%

# Combined with GameMode:
gamemoderun mangohud %command%
```

### 2. Use Performance Launcher

The script creates `~/launch-game.sh` with intelligent performance management ✨:

```bash
~/launch-game.sh steam
~/launch-game.sh lutris
~/launch-game.sh wine /path/to/game.exe
```

**What it does:**
- ✓ Sets CPU governor to performance (restores on exit)
- ✓ Validates GameMode library before enabling (prevents multilib errors)
- ✓ Activates MangoHud via MANGOHUD=1 env var (avoids LD_PRELOAD issues)
- ✓ Steam-specific handling (skips wrapper, advises per-game Launch Options)
- ✓ Cleanup trap restores all settings on exit

**For Steam games**, configure per-game via Launch Options:
```
gamemoderun mangohud %command%
```

### 3. Install Your First Game

**Recommended first games:**

**Native Linux (Easy):**
- Counter-Strike 2 (free) - FPS
- Portal 2 - Puzzle
- Dota 2 (free) - MOBA
- Team Fortress 2 (free) - FPS

**Proton (Test Compatibility):**
- Stardew Valley - Low requirement, works great
- Terraria - 2D, excellent performance
- Hades - 3D but optimized
- Hollow Knight - 2D platformer

**How to install:**
1. Open Steam
2. Search for game
3. Click Install
4. Wait for download
5. Click Play!

### 4. Test Performance Overlay

```bash
# Launch game with MangoHud
# In Steam: Right-click game → Properties → Launch Options
mangohud %command%

# Or use performance launcher
~/launch-game.sh steam
```

**You should see:**
- FPS counter
- Frame time graph
- GPU usage
- CPU usage
- Temperatures

**Toggle on/off:** Shift+F12 (default)

---

## 🔄 Maintenance ✨

### Update Components

```bash
# Update all previously installed components
sudo python3 debian_gaming_setup.py --update
```

Reads your installation state and checks APT packages, Flatpak apps, and GE-Proton for updates.

### Rollback Installation

```bash
# Undo a previous installation
sudo python3 debian_gaming_setup.py --rollback
```

The rollback engine tracks 7 action types (APT, Flatpak, repos, files, sysctl, GE-Proton) and reverses them in LIFO order with a dry-run preview option.

### Check for Script Updates

```bash
# Check GitHub for newer version
sudo python3 debian_gaming_setup.py --self-update
```

Downloads, validates syntax, backs up current version, and replaces atomically.

---

## 🐛 Common First-Time Issues

### Issue: "Must be run with sudo"

**Solution:**
```bash
sudo python3 debian_gaming_setup.py
```
Always use `sudo`.

### Issue: "dpkg is locked" ✨

**Solution:**
```bash
sudo lsof /var/lib/dpkg/lock-frontend  # Check what's using it
# If safe, clear stale locks:
sudo rm /var/lib/dpkg/lock-frontend /var/lib/dpkg/lock
sudo dpkg --configure -a
```

The script's system pre-check detects this automatically and warns you.

### Issue: Steam won't launch

**Solutions:**
```bash
# Run from terminal to see errors
steam

# Clear cache
rm -rf ~/.steam/steam/appcache/

# Reinstall
sudo apt-get install --reinstall steam-installer
```

### Issue: No GPU detected

**Check:**
```bash
lspci | grep -i vga
```

**If NVIDIA:**
```bash
sudo python3 debian_gaming_setup.py --nvidia
```

**If AMD:**
```bash
sudo python3 debian_gaming_setup.py --amd
```

### Issue: Proton games won't start

**Solutions:**
1. Verify Proton is enabled in Steam settings
2. Try different Proton version (Properties → Compatibility)
3. Check ProtonDB: https://www.protondb.com
4. View logs: `~/.steam/steam/logs/`

### Issue: Low FPS / Poor Performance

**Checks:**
1. Verify GPU drivers loaded:
   ```bash
   nvidia-smi  # NVIDIA
   glxinfo | grep renderer  # AMD/Intel
   ```

2. Use performance launcher:
   ```bash
   ~/launch-game.sh steam
   ```

3. Enable GameMode in game settings

4. Check if running on integrated GPU (laptops):
   ```bash
   prime-select query  # NVIDIA laptops
   ```

### Issue: GameMode "cannot open shared object" ✨

```bash
sudo apt install libgamemode0 libgamemode0:i386
```

The performance launcher validates library presence via `ldconfig` before enabling GameMode.

### Issue: MangoHud not showing ✨

- The performance launcher uses `MANGOHUD=1` env var (Vulkan implicit layer)
- For Steam per-game: set Launch Options to `mangohud %command%`
- Check config: `~/.config/MangoHud/MangoHud.conf`

### Issue: Controller not detected

**Check:**
```bash
ls /dev/input/js*
jstest /dev/input/js0
```

**Fix:**
```bash
sudo python3 debian_gaming_setup.py --controllers
```

### Issue: Waydroid won't start

**Requirements:**
- Wayland session (check: `echo $XDG_SESSION_TYPE`)
- Kernel modules loaded

**Initialize:**
```bash
sudo waydroid init
waydroid session start
waydroid show-full-ui
```

---

## 📊 Verification Checklist

After installation, verify:

- [ ] System rebooted
- [ ] GPU drivers working (`nvidia-smi` or `glxinfo`)
- [ ] Steam launches
- [ ] Proton enabled in Steam settings
- [ ] At least one game installed
- [ ] Game launches and runs
- [ ] Performance overlay shows (if MangoHud installed)
- [ ] Post-install health check passed ✨
- [ ] Logs show no critical errors
- [ ] Performance launcher works

**Check logs:**
```bash
cat ~/gaming_setup_logs/gaming_setup_*.log | tail -100
grep ERROR ~/gaming_setup_logs/gaming_setup_*.log
```

---

## 🎯 Next Steps

### Learn More

1. **ProtonDB** - Check game compatibility
   - https://www.protondb.com
   - Community fixes and tips

2. **Lutris** - Install non-Steam games
   - https://lutris.net/games
   - One-click installers

3. **MangoHud Configuration**
   - https://github.com/flightlessmango/MangoHud
   - Customize overlay

4. **GE-Proton** - Custom Proton builds
   - Already installed by script (SHA512 verified) ✨
   - Select in game properties

### Ongoing Maintenance ✨

```bash
# Update all components
sudo python3 debian_gaming_setup.py --update

# Check for script updates
sudo python3 debian_gaming_setup.py --self-update

# System maintenance
sudo apt-get update && sudo apt-get upgrade
flatpak update
```

### Advanced Configuration

See [Usage_Guide.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/Usage_Guide.md) for:
- All 54 CLI options explained
- Configuration presets
- Rollback system details
- Update mode
- Per-game configurations
- Troubleshooting guide
- Virtual machine tips

---

## 🆘 Getting Help

### Self-Help Resources

1. **Check logs first:**
   ```bash
   cat ~/gaming_setup_logs/gaming_setup_*.log
   ```

2. **Run health check** ✨:
   The script runs a post-install health check automatically. Check the output for warnings.

3. **Search ProtonDB** for game-specific issues

4. **Review documentation:**
   - [README.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/README.md) - Overview
   - [Usage_Guide.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/Usage_Guide.md) - Complete reference
   - [CHANGELOG.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/CHANGELOG.md) - Recent changes

### Report Issues

If you encounter problems:
1. Note your Linux distribution and version
2. Note your GPU model
3. Save relevant log excerpts
4. Report on GitHub Issues

**Include:**
- Distribution: `lsb_release -a`
- GPU: `lspci | grep -i vga`
- Logs: `~/gaming_setup_logs/gaming_setup_*.log`

---

## 📝 Quick Command Reference

```bash
# Installation
sudo python3 debian_gaming_setup.py              # Interactive
sudo python3 debian_gaming_setup.py --dry-run    # Test
sudo python3 debian_gaming_setup.py -y [OPTIONS] # Automated
sudo python3 debian_gaming_setup.py --preset standard -y  # Preset ✨

# Maintenance ✨
sudo python3 debian_gaming_setup.py --update         # Update components
sudo python3 debian_gaming_setup.py --rollback        # Undo installation
sudo python3 debian_gaming_setup.py --self-update     # Update script
sudo python3 debian_gaming_setup.py --check-requirements  # Validate system

# Post-Installation
nvidia-smi                           # Check NVIDIA driver
glxinfo | grep "OpenGL renderer"     # Check AMD/Intel
~/launch-game.sh steam               # Launch with optimizations

# Configuration
nano ~/.config/MangoHud/MangoHud.conf    # MangoHud settings
nano ~/.config/vkBasalt/vkBasalt.conf    # vkBasalt settings

# Troubleshooting
cat ~/gaming_setup_logs/gaming_setup_*.log  # View logs
steam                                        # Run Steam from terminal
```

---

## ✅ Success!

**You're now ready to game on Linux!** 🎮

- Drivers installed and working
- Gaming platforms configured
- Performance tools enabled
- Rollback safety net in place ✨
- Ready to play

**Enjoy your games!**

---

**Questions?** See [Usage_Guide.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/Usage_Guide.md) for detailed help.

**Version:** 2.5.0 | Updated: February 2026
