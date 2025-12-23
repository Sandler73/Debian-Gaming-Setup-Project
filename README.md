# Ubuntu-Gaming-Setup-Script

A comprehensive Python script to speed up and automated configuring an Ubuntu system for gaming purposes.

## Features

### GPU Driver Support
- **NVIDIA**: Automatic installation of proprietary drivers using `ubuntu-drivers`
- **AMD**: Mesa and Vulkan driver installation
- **Intel**: Integrated graphics support with VA-API

### Gaming Platforms
- **Steam**: Valve's gaming platform with Proton compatibility
- **Lutris**: Unified launcher for GOG, Epic Games, and more
- **Heroic Games Launcher**: Epic Games Store and GOG Galaxy alternative
- **ProtonUp-Qt**: Manage multiple Proton versions (including Proton-GE)

### Compatibility Layers
- **Wine**: Windows application compatibility (staging branch)
- **Winetricks**: Wine configuration and dependency management
- **Proton**: Steam's compatibility tool for Windows games

### System Optimizations
- 32-bit architecture support (required for many games)
- Increased inotify file watchers (for games like Star Citizen)
- Increased memory map count
- CPU performance governor option
- GameMode support for automatic performance optimization

### Additional Tools
- **Discord**: Voice chat and community
- **OBS Studio**: Streaming and recording
- **Controller support**: Xbox and generic gamepad support
- **Multimedia codecs**: Complete codec pack for video playback
- **Performance launcher script**: Automatically applies optimizations when launching games

## Prerequisites

- Ubuntu 24.04.3 LTS (works on other versions but tested on 24.04.3)
- Sudo/root privileges
- Active internet connection
- Minimum 20 GB free disk space recommended

## Installation

### Download and Run

```bash
# Download the script
wget https://github.com/Sandler73/Ubuntu-Gaming-Setup-Script/ubuntu_gaming_setup.py

# Make it executable
chmod +x ubuntu_gaming_setup.py

# Run with sudo
sudo python3 ubuntu_gaming_setup.py
```

### What the Script Does

1. **System Updates**: Updates all packages to latest versions
2. **GPU Detection**: Automatically detects your GPU type
3. **Driver Installation**: Installs appropriate drivers for your GPU
4. **32-bit Support**: Enables i386 architecture for game compatibility
5. **Gaming Platforms**: Installs Steam, Lutris, and other launchers (with prompts)
6. **Wine/Proton**: Sets up Windows game compatibility
7. **Optimizations**: Applies kernel parameters and performance tweaks
8. **Creates Tools**: Generates a performance launcher script

### Interactive Prompts

The script will ask for confirmation before:
- Installing each major component
- Applying system optimizations
- Installing optional software (Discord, OBS)
- Rebooting the system

## Post-Installation

### 1. Reboot (REQUIRED)
```bash
sudo reboot
```
GPU drivers and kernel parameters require a reboot to take effect.

### 2. Verify GPU Drivers

**NVIDIA:**
```bash
nvidia-smi
```
Should display your GPU information and driver version.

**AMD/Intel:**
```bash
vulkaninfo | head -20
glxinfo | grep "OpenGL renderer"
```

### 3. Configure Steam

1. Launch Steam
2. Go to **Settings** → **Steam Play**
3. Enable "Enable Steam Play for all other titles"
4. Select **Proton Experimental** or latest Proton version
5. Restart Steam

### 4. Install Proton-GE (Recommended)

Proton-GE offers better compatibility for many games:

1. Launch ProtonUp-Qt (if installed)
2. Install latest Proton-GE version
3. Select it in Steam for specific games that need it

### 5. Test Your Setup

Launch a game or run benchmark:
```bash
# Using the performance launcher
~/launch-game.sh steam steam://rungameid/APPID

# Or directly through Steam
steam
```

## Performance Launcher Usage

The script creates `~/launch-game.sh` which automatically:
- Enables GameMode (if available)
- Sets CPU governor to performance
- Runs game with higher process priority
- Restores settings after game exits

**Example usage:**
```bash
~/launch-game.sh /path/to/game
~/launch-game.sh steam steam://rungameid/570
```

## Troubleshooting

### NVIDIA Driver Issues

If NVIDIA drivers don't load:
```bash
# Check secure boot status (should be disabled)
mokutil --sb-state

# Reinstall drivers
sudo ubuntu-drivers autoinstall
sudo reboot
```

### Steam Not Launching

```bash
# Remove and reinstall
sudo apt remove --purge steam-installer
sudo apt autoremove
sudo apt install steam-installer
```

### Wine Applications Won't Run

```bash
# Verify 32-bit support
dpkg --print-foreign-architectures
# Should show: i386

# Reinstall Wine
sudo apt install --reinstall winehq-staging
```

### Performance Issues

1. **Check CPU governor:**
```bash
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```
Should show "performance" while gaming.

2. **Enable GameMode:**
```bash
# Check if running
gamemoded -s

# Test with a game
gamemoderun ./game
```

3. **Monitor GPU usage:**
```bash
# NVIDIA
nvidia-smi -l 1

# AMD/Intel
radeontop  # or intel_gpu_top
```

### Audio Issues

```bash
# Restart PulseAudio
systemctl --user restart pulseaudio

# Check audio devices
pactl list sinks
```

## Recommended Settings

### For NVIDIA GPUs
- Enable "Force Full Composition Pipeline" in NVIDIA Settings for tear-free gaming
- Use latest proprietary drivers for best performance

### For AMD GPUs
- Mesa drivers update with system updates - keep system updated
- Use RADV Vulkan driver (default)

### For Steam Play/Proton
- Use Proton Experimental for newest games
- Use Proton-GE for better compatibility
- Check ProtonDB (www.protondb.com) for game-specific tweaks

### Lutris Tips
- Install runners as needed (Wine, DXVK, etc.)
- Use game-specific install scripts from Lutris.net
- Enable Feral GameMode in Lutris settings

## Logs and Debugging

All installation steps are logged to:
```
~/gaming_setup_logs/gaming_setup_YYYYMMDD_HHMMSS.log
```

Check this file if something goes wrong during installation.

## What Gets Installed

### Core Packages
- Ubuntu restricted extras (codecs)
- Mesa Vulkan drivers
- 32-bit graphics libraries
- Build tools and libraries

### Gaming Software
- Steam
- Lutris
- Heroic Games Launcher (via Flatpak)
- Wine (staging branch)
- Winetricks
- ProtonUp-Qt (via Flatpak)
- GameMode

### Optional Software
- Discord (via Flatpak)
- OBS Studio
- Controller utilities (xboxdrv, antimicrox)

### System Optimizations
- Increased file watchers (fs.inotify.max_user_watches=524288)
- Increased memory maps (vm.max_map_count=2147483642)
- CPU performance governor service (optional)

## Uninstalling

To remove gaming components:

```bash
# Remove Steam
sudo apt remove --purge steam-installer

# Remove Lutris
sudo apt remove --purge lutris
sudo add-apt-repository --remove ppa:lutris-team/lutris

# Remove Wine
sudo apt remove --purge winehq-staging

# Remove Flatpak apps
flatpak uninstall com.heroicgameslauncher.hgl
flatpak uninstall com.discordapp.Discord
flatpak uninstall net.davidotek.pupgui2

# Remove optimizations
sudo rm /etc/sysctl.d/99-gaming.conf
sudo systemctl disable cpu-performance.service
sudo rm /etc/systemd/system/cpu-performance.service
```

## Security Considerations

- Script requires sudo privileges
- Reviews package sources before installation
- Uses official repositories and PPAs
- Flatpak apps are sandboxed
- Creates detailed logs for audit purposes

## Contributing

Found a bug or have a suggestion? This script can be modified to suit your needs:
- Add/remove gaming platforms
- Adjust system optimizations
- Customize package selections

## License

This script is provided as-is for educational and personal use.

## Resources

- [ProtonDB](https://www.protondb.com/) - Game compatibility database
- [Lutris](https://lutris.net/) - Game install scripts
- [WineHQ](https://www.winehq.org/) - Wine documentation
- [Steam Proton](https://github.com/ValveSoftware/Proton) - Official Proton repo
- [Proton-GE](https://github.com/GloriousEggroll/proton-ge-custom) - GloriousEggroll's Proton

## Changelog

### Version 1.0
- Initial release
- Support for Ubuntu 24.04.3
- NVIDIA, AMD, and Intel GPU support
- Steam, Lutris, Heroic installation
- Wine and Proton setup
- System optimizations
- Performance launcher script
- Discord and OBS installation

---

**Happy Gaming! 🎮**
