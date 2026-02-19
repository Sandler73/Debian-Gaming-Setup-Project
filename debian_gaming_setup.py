#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
Debian-Based Comprehensive Gaming Setup Script v2.6.0
═══════════════════════════════════════════════════════════════════════════════

SYNOPSIS:
    Comprehensive automated gaming environment setup for Debian-based Linux
    distributions including Ubuntu, Linux Mint, Kali, Pop!_OS, and derivatives.

DESCRIPTION:
    Automates installation and configuration of a complete gaming environment
    including GPU drivers, gaming platforms, compatibility layers, performance
    tools, system optimizations, and communication utilities. Capabilities:

    Core Installation:
    • GPU/VM auto-detection with lspci and glxinfo cross-validation
    • Dynamic GPU driver selection (NVIDIA via ubuntu-drivers, AMD with Vulkan,
      Intel with Arc support, VM guest tools for 6 hypervisors)
    • Gaming platforms (Steam, Lutris, Heroic, ProtonUp-Qt, Sober, Waydroid)
    • Wine/Proton with WineHQ repository validation and codename resolution
    • GE-Proton with SHA512 checksum verification
    • Performance tools (GameMode, MangoHud, Goverlay, GreenWithEnvy, vkBasalt)
    • Communication tools (Discord, OBS, Mumble)
    • Mod management (r2modman)
    • System optimizations (sysctl tuning, performance launcher script)

    Intelligent Behavior:
    • Dynamic distribution codename resolution (no hardcoded codenames)
    • Distro-aware package name mapping (Ubuntu vs Debian vs derivatives)
    • Package availability pre-flight validation before install attempts
    • Smart install/update prompts showing current and available versions
    • Pre-flight network connectivity checking
    • System requirements validation (disk space, RAM, architecture, dpkg lock)

    State Management & Safety:
    • Action-based rollback engine with LIFO reversal and dry-run preview
    • Per-package state tracking with versioned JSON manifest
    • Auto-recording of apt/flatpak installs, repo additions, file writes
    • SIGTERM/SIGINT signal handlers for graceful cleanup
    • Post-install health check verifying installed components

    CLI Automation & UX:
    • 55+ CLI arguments for targeted or fully automated installs
    • Configuration presets (minimal, standard, complete, streaming)
    • --update mode for centralized component updating
    • --self-update to check GitHub for newer script versions
    • Dry-run mode for testing without system changes
    • Auto-yes mode for unattended installation

    Security:
    • No shell=True subprocess calls (command injection prevention)
    • Specific exception types (no bare except clauses)
    • Categorized timeout constants for all operations
    • Secure download-then-execute for external scripts (Waydroid)
    • Deduplicated Flatpak setup with session caching

SUPPORTED SYSTEMS:
    • Ubuntu (20.04+) - all editions
    • Linux Mint (20+) including LMDE
    • Debian (11+)
    • Pop!_OS (20.04+)
    • Kali Linux (2020+)
    • Elementary OS (6+)
    • Zorin OS (16+)
    • Any Debian/Ubuntu derivative

SUPPORTED HARDWARE:
    • NVIDIA GPUs (dynamic driver selection via ubuntu-drivers or apt-cache)
    • AMD GPUs (Mesa/AMDGPU with Vulkan, firmware-aware for Debian non-free)
    • Intel GPUs (Mesa/i915 with media acceleration, Arc GPU support)
    • VMware virtual machines (open-vm-tools)
    • VirtualBox virtual machines (guest additions)
    • KVM/QEMU virtual machines (guest agent)
    • Hyper-V, Xen, Parallels virtual machines

USAGE EXAMPLES:
    # Interactive installation (prompts for each component)
    sudo python3 debian_gaming_setup.py

    # Dry-run mode (test without changes)
    sudo python3 debian_gaming_setup.py --dry-run

    # Auto-yes with all gaming platforms
    sudo python3 debian_gaming_setup.py -y --all-platforms

    # Install specific components
    sudo python3 debian_gaming_setup.py --nvidia --steam --lutris

    # Use a preset configuration
    sudo python3 debian_gaming_setup.py --preset standard -y

    # Rollback previous installation
    sudo python3 debian_gaming_setup.py --rollback

    # Update all previously installed components
    sudo python3 debian_gaming_setup.py --update

    # Check for script updates
    sudo python3 debian_gaming_setup.py --self-update

    # Validate system requirements without installing
    sudo python3 debian_gaming_setup.py --check-requirements

NOTES:
    • Requires sudo/root privileges
    • Creates backups before system modifications
    • Logs all operations to ~/gaming_setup_logs/
    • Supports rollback via --rollback with manifest archiving
    • All codenames and driver versions are resolved dynamically
    • Rollback manifest persists across script restarts

VERSION:
    2.6.0

AUTHOR:
    Debian Gaming Setup Script
    https://github.com/Sandler73/Debian-Gaming-Setup-Project

LICENSE:
    MIT License

═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import subprocess
import platform
import logging
import json
import shutil
import signal
import hashlib
import argparse
import pwd
import grp
import re
import time
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS FOR USER CONTEXT
# ═══════════════════════════════════════════════════════════════════════════════

def get_real_user() -> str:
    """
    Get the actual user who invoked sudo

    Returns:
        Username of the actual user (not root)
    """
    sudo_user = os.environ.get('SUDO_USER')
    if sudo_user:
        return sudo_user
    return os.environ.get('USER', 'root')

def get_real_user_home() -> Path:
    """
    Get the home directory of the actual user

    Returns:
        Path object representing user's home directory
    """
    real_user = get_real_user()
    try:
        return Path(pwd.getpwnam(real_user).pw_dir)
    except KeyError:
        return Path.home()

def get_real_user_uid_gid() -> Tuple[int, int]:
    """
    Get UID and GID of the actual user

    Returns:
        Tuple of (uid, gid) for the actual user
    """
    real_user = get_real_user()
    try:
        pw_record = pwd.getpwnam(real_user)
        return pw_record.pw_uid, pw_record.pw_gid
    except KeyError:
        return os.getuid(), os.getgid()

# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL CONSTANTS AND PATHS
# ═══════════════════════════════════════════════════════════════════════════════

# User context
REAL_USER = get_real_user()
REAL_USER_HOME = get_real_user_home()

# Directory setup
LOG_DIR = REAL_USER_HOME / "gaming_setup_logs"
LOG_DIR.mkdir(exist_ok=True, parents=True)
LOG_FILE = LOG_DIR / f"gaming_setup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

BACKUP_DIR = REAL_USER_HOME / "gaming_setup_backups"
BACKUP_DIR.mkdir(exist_ok=True, parents=True)

STATE_FILE = LOG_DIR / "installation_state.json"
ROLLBACK_FILE = LOG_DIR / "rollback_manifest.json"

# Script version constant for self-update checks
SCRIPT_VERSION = "2.6.0"

# Rollback manifest schema version
ROLLBACK_SCHEMA_VERSION = "1.0"

# Categorized timeout constants in seconds
TIMEOUT_QUICK = 5        # Fast local operations (lspci, dpkg, dmesg)
TIMEOUT_NETWORK = 10     # Network connectivity probes
TIMEOUT_API = 15         # GitHub/remote API calls
TIMEOUT_DOWNLOAD = 120   # File downloads (wget, large fetches)
TIMEOUT_INSTALL = 300    # Package installations (apt-get install)
TIMEOUT_UPDATE = 600     # Full system updates (apt-get upgrade)

# Rollback manifest schema version
ROLLBACK_SCHEMA_VERSION = "1.0"

# GitHub repository for self-update checks
GITHUB_REPO_OWNER = "Sandler73"
GITHUB_REPO_NAME = "Debian-Gaming-Setup-Project"
GITHUB_API_BASE = "https://api.github.com/repos"

# System requirements thresholds
MIN_DISK_SPACE_GB = 5.0    # Minimum free disk space in GB
MIN_RAM_GB = 2.0            # Minimum RAM in GB
WARN_DISK_SPACE_GB = 10.0  # Warn if less than this available

# Set proper ownership for directories
try:
    uid, gid = get_real_user_uid_gid()
    os.chown(LOG_DIR, uid, gid)
    os.chown(BACKUP_DIR, uid, gid)
except (OSError, PermissionError):
    pass  # Non-fatal: ownership fix best-effort during early init

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# ═══════════════════════════════════════════════════════════════════════════════
# COLOR OUTPUT CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class Color:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def disable():
        """Disable colors for non-TTY or logging"""
        Color.HEADER = ''
        Color.BLUE = ''
        Color.CYAN = ''
        Color.GREEN = ''
        Color.YELLOW = ''
        Color.RED = ''
        Color.END = ''
        Color.BOLD = ''
        Color.UNDERLINE = ''

# ═══════════════════════════════════════════════════════════════════════════════
# ENUMERATIONS FOR TYPE SAFETY
# ═══════════════════════════════════════════════════════════════════════════════

class GPUVendor(Enum):
    """GPU vendor enumeration"""
    NVIDIA = "nvidia"
    AMD = "amd"
    INTEL = "intel"
    VIRTUAL = "virtual"
    UNKNOWN = "unknown"

class VMType(Enum):
    """Virtual machine type enumeration"""
    VMWARE = "vmware"
    VIRTUALBOX = "virtualbox"
    KVM = "kvm"
    QEMU = "qemu"
    HYPERV = "hyperv"
    XEN = "xen"
    PARALLELS = "parallels"
    NONE = "none"

class DistroFamily(Enum):
    """Distribution family enumeration"""
    DEBIAN = "debian"
    UBUNTU = "ubuntu"
    MINT = "mint"
    KALI = "kali"
    POPOS = "popos"
    ELEMENTARY = "elementary"
    ZORIN = "zorin"
    UNKNOWN = "unknown"

class InstallationPhase(Enum):
    """Installation phase tracking for state management"""
    INIT = "initialization"
    DETECTION = "detection"
    DRIVERS = "drivers"
    PLATFORMS = "platforms"
    COMPATIBILITY = "compatibility"
    PERFORMANCE = "performance"
    TOOLS = "tools"
    OPTIMIZATION = "optimization"
    FINALIZATION = "finalization"

# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES FOR STRUCTURED INFORMATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SystemInfo:
    """System information container"""
    distro_name: str = "Unknown"
    distro_version: str = "Unknown"
    distro_id: str = "Unknown"
    distro_family: DistroFamily = DistroFamily.UNKNOWN
    kernel_version: str = "Unknown"
    architecture: str = "Unknown"
    desktop_environment: str = "Unknown"
    is_wsl: bool = False

@dataclass
class HardwareInfo:
    """Hardware information container"""
    gpu_vendor: GPUVendor = GPUVendor.UNKNOWN
    gpu_model: str = "Unknown"
    gpu_pci_id: str = ""
    vm_type: VMType = VMType.NONE
    cpu_vendor: str = "Unknown"
    cpu_model: str = "Unknown"
    cpu_cores: int = 0
    total_memory_gb: float = 0.0
    has_vulkan: bool = False
    vulkan_version: str = ""

@dataclass
class BackupEntry:
    """Backup entry for rollback functionality (legacy, kept for compatibility)"""
    timestamp: str
    file_path: str
    backup_path: str
    operation: str
    checksum: str = ""
    package_name: str = ""

class ActionType(Enum):
    """
    Rollback action types for the state engine.


    so the rollback engine knows how to undo it.
    """
    APT_INSTALL = "apt_install"           # apt-get install package(s)
    FLATPAK_INSTALL = "flatpak_install"   # flatpak install app
    REPO_ADD = "repo_add"                 # Repository addition (PPA, .sources file)
    FILE_CREATE = "file_create"           # New file created by script
    FILE_MODIFY = "file_modify"           # Existing file modified (backup stored)
    SYSCTL_WRITE = "sysctl_write"         # sysctl config file written
    GE_PROTON_INSTALL = "ge_proton_install"  # GE-Proton extracted to compat dir

@dataclass
class RollbackAction:
    """
    A single reversible action recorded during installation.


    to fully reverse itself. Actions are processed LIFO during rollback.

    Attributes:
        action_type: Category of action (determines reversal strategy)
        timestamp: ISO format timestamp when action was performed
        description: Human-readable description of what was done
        packages: List of package names involved (apt or flatpak)
        files: List of file paths created or modified
        backup_files: Dict mapping original path → backup path (for FILE_MODIFY)
        reversal_commands: List of commands to execute for reversal
        metadata: Additional info (repo URL, flatpak remote, version, etc.)
        success: Whether the original action succeeded
    """
    action_type: str  # ActionType.value string for JSON serialization
    timestamp: str
    description: str
    packages: List[str] = field(default_factory=list)
    files: List[str] = field(default_factory=list)
    backup_files: Dict[str, str] = field(default_factory=dict)
    reversal_commands: List[List[str]] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)
    success: bool = True

@dataclass
class InstallationConfig:
    """
    Installation configuration from CLI arguments or interactive prompts
    This replaces the need for global flags while preserving all functionality
    """
    # GPU/VM options
    install_nvidia_drivers: bool = False
    install_amd_drivers: bool = False
    install_intel_drivers: bool = False
    install_vm_tools: bool = False

    # Gaming platforms
    install_steam: bool = False
    install_lutris: bool = False
    install_heroic: bool = False
    install_protonup: bool = False
    install_sober: bool = False
    install_waydroid: bool = False

    # Compatibility layers
    install_wine: bool = False
    install_winetricks: bool = False
    install_dxvk: bool = False
    install_vkd3d: bool = False
    install_ge_proton: bool = False

    # Performance tools
    install_gamemode: bool = False
    install_mangohud: bool = False
    install_goverlay: bool = False
    install_greenwithenv: bool = False

    # Graphics enhancement tools
    install_vkbasalt: bool = False
    install_reshade_setup: bool = False

    # Additional tools
    install_discord: bool = False
    install_obs: bool = False
    install_mumble: bool = False
    install_teamspeak: bool = False
    install_mod_managers: bool = False

    # Controller support
    install_controller_support: bool = False
    install_antimicrox: bool = False
    install_xboxdrv: bool = False

    # System optimizations
    apply_system_optimizations: bool = False
    install_custom_kernel: bool = False
    optimize_btrfs: bool = False
    create_performance_launcher: bool = False

    # Essential packages
    install_essential_packages: bool = False
    install_codecs: bool = False

    # Script behavior
    dry_run: bool = False
    auto_yes: bool = False
    skip_prompts: bool = False
    create_backup: bool = True
    enable_rollback: bool = True
    verbose: bool = False
    skip_update: bool = False

# ═══════════════════════════════════════════════════════════════════════════════
# ARGUMENT PARSER
# ═══════════════════════════════════════════════════════════════════════════════

def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments for automated installation

    Adds CLI automation while preserving the original interactive mode
    when no arguments are provided.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description='Comprehensive Debian-based gaming setup with full Ubuntu compatibility',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (original behavior)
  sudo python3 debian_gaming_setup.py

  # Test before installing
  sudo python3 debian_gaming_setup.py --dry-run --all-platforms

  # Automated NVIDIA gaming setup
  sudo python3 debian_gaming_setup.py -y --nvidia --all-platforms --optimize

  # AMD gaming setup
  sudo python3 debian_gaming_setup.py -y --amd --steam --lutris

  # Rollback previous installation
  sudo python3 debian_gaming_setup.py --rollback
        """
    )

    # General options
    general = parser.add_argument_group('General Options')
    general.add_argument('-y', '--yes', action='store_true',
                        help='Auto-answer yes to all prompts')
    general.add_argument('--dry-run', action='store_true',
                        help='Test mode - show what would be done without making changes')
    general.add_argument('--verbose', action='store_true',
                        help='Enable verbose debug output')
    general.add_argument('--no-backup', action='store_true',
                        help='Skip creating backups before modifications')

    # GPU/Driver options
    drivers = parser.add_argument_group('GPU/Driver Options')
    drivers.add_argument('--nvidia', action='store_true',
                        help='Install NVIDIA drivers')
    drivers.add_argument('--amd', action='store_true',
                        help='Install AMD drivers')
    drivers.add_argument('--intel', action='store_true',
                        help='Install Intel drivers')
    drivers.add_argument('--vm-tools', action='store_true',
                        help='Install VM guest tools')

    # Gaming platforms
    platforms = parser.add_argument_group('Gaming Platforms')
    platforms.add_argument('--steam', action='store_true',
                          help='Install Steam')
    platforms.add_argument('--lutris', action='store_true',
                          help='Install Lutris')
    platforms.add_argument('--heroic', action='store_true',
                          help='Install Heroic Games Launcher')
    platforms.add_argument('--protonup', action='store_true',
                          help='Install ProtonUp-Qt')
    platforms.add_argument('--sober', action='store_true',
                          help='Install Sober (Roblox on Linux)')
    platforms.add_argument('--waydroid', action='store_true',
                          help='Install Waydroid (Android container)')
    platforms.add_argument('--all-platforms', action='store_true',
                          help='Install all gaming platforms (excludes Sober/Waydroid)')

    # Compatibility layers
    compat = parser.add_argument_group('Compatibility Layers')
    compat.add_argument('--wine', action='store_true',
                       help='Install Wine Staging')
    compat.add_argument('--winetricks', action='store_true',
                       help='Install Winetricks')
    compat.add_argument('--dxvk', action='store_true',
                       help='Show DXVK installation information')
    compat.add_argument('--vkd3d', action='store_true',
                       help='Show VKD3D-Proton installation information')
    compat.add_argument('--ge-proton', action='store_true',
                       help='Install GE-Proton automatically')

    # Performance tools
    perf = parser.add_argument_group('Performance Tools')
    perf.add_argument('--gamemode', action='store_true',
                     help='Install GameMode')
    perf.add_argument('--mangohud', action='store_true',
                     help='Install MangoHud performance overlay')
    perf.add_argument('--goverlay', action='store_true',
                     help='Install Goverlay (MangoHud GUI)')
    perf.add_argument('--gwe', action='store_true',
                     help='Install GreenWithEnvy (NVIDIA GPU control)')

    # Graphics enhancement tools
    graphics = parser.add_argument_group('Graphics Enhancement')
    graphics.add_argument('--vkbasalt', action='store_true',
                         help='Install vkBasalt (Vulkan post-processing layer)')
    graphics.add_argument('--reshade', action='store_true',
                         help='Show ReShade setup information (via vkBasalt)')

    # Additional tools
    tools = parser.add_argument_group('Additional Tools')
    tools.add_argument('--discord', action='store_true',
                      help='Install Discord')
    tools.add_argument('--obs', action='store_true',
                      help='Install OBS Studio')
    tools.add_argument('--mumble', action='store_true',
                      help='Install Mumble')
    tools.add_argument('--teamspeak', action='store_true',
                      help='Show TeamSpeak installation information')
    tools.add_argument('--mod-managers', action='store_true',
                      help='Install mod management tools')
    tools.add_argument('--controllers', action='store_true',
                      help='Install controller support')
    tools.add_argument('--essential', action='store_true',
                      help='Install essential gaming packages')
    tools.add_argument('--codecs', action='store_true',
                      help='Install multimedia codecs')

    # System options
    system = parser.add_argument_group('System Options')
    system.add_argument('--optimize', action='store_true',
                       help='Apply system optimizations')
    system.add_argument('--custom-kernel', action='store_true',
                       help='Install custom gaming kernel (planned)')
    system.add_argument('--skip-update', action='store_true',
                       help='Skip system update')
    system.add_argument('--launcher', action='store_true',
                       help='Create performance launcher script')

    # Maintenance
    maint = parser.add_argument_group('Maintenance')
    maint.add_argument('--rollback', action='store_true',
                      help='Rollback previous installation')
    maint.add_argument('--cleanup', action='store_true',
                      help='Clean up installation files and logs')
    maint.add_argument('--update', action='store_true',
                      help='Update all previously installed components')
    maint.add_argument('--self-update', action='store_true',
                      help='Check GitHub for newer script version and update')
    maint.add_argument('--check-requirements', action='store_true',
                      help='Check system requirements without installing')

    # Configuration presets
    presets = parser.add_argument_group('Presets')
    presets.add_argument('--preset', type=str, choices=[
                         'minimal', 'standard', 'complete', 'streaming'],
                         help='Apply a named configuration preset '
                              '(minimal: drivers+steam, '
                              'standard: +wine+lutris+gamemode, '
                              'complete: all components, '
                              'streaming: +obs+discord)')

    return parser.parse_args()

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN GAMINGSETUP CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class GamingSetup:
    """
    Main class for comprehensive Debian-based gaming setup


    - All detection methods with lspci and glxinfo cross-validation
    - Package version checking and comparison
    - Smart installation prompts with version display
    - Flatpak app detection and version checking
    - Comprehensive installation summary
    - Repository cleanup
    - Error handling and logging
    - Progress indication
    - Performance launcher creation
    - CPU governor configuration

    - CLI argument support
    - Dry-run mode
    - State management
    - Rollback framework
    - Multi-distribution support
    - Enhanced error tracking
    - Dynamic codename resolution for all supported distributions
    - Dynamic driver detection for NVIDIA, AMD, Intel, and VM environments
    - Network connectivity checking before remote operations
    - Automatic interactive/targeted flow control based on CLI flags
    """

    def __init__(self, args: Optional[argparse.Namespace] = None):
        """
        Initialize the gaming setup system

        Args:
            args: Parsed command-line arguments (None for interactive mode)
        """
        # Store arguments (None if running in interactive mode)
        self.args = args if args else argparse.Namespace()

        # Initialize configuration from arguments or defaults
        self.config = self._init_config_from_args()

        # System and hardware information
        self.system_info = SystemInfo()
        self.hardware_info = HardwareInfo()

        # State tracking
        self.rollback_entries: List[BackupEntry] = []  # Legacy
        self.rollback_actions: List[RollbackAction] = []  # Action-based rollback
        self.installation_state: Dict[str, Any] = {}
        self.failed_operations: List[str] = []
        self.current_phase = InstallationPhase.INIT
        self._session_id = datetime.now().strftime('%Y%m%d_%H%M%S')  # Unique session

        self._setup_signal_handlers()

        # Verify prerequisites
        self.check_root()

        # Load previous state if exists
        self.load_installation_state()
        self.load_rollback_manifest()  # Load previous rollback data

    def _setup_signal_handlers(self):
        """
        Register signal handlers for graceful cleanup on SIGTERM/SIGINT.


        and a clean message is displayed when the script is killed via
        signal (e.g., kill command, system shutdown, Ctrl+C).
        """
        def _signal_handler(signum, frame):
            """Handle termination signals gracefully"""
            sig_name = signal.Signals(signum).name if hasattr(signal, 'Signals') else str(signum)
            print(f"\n{Color.YELLOW}Received {sig_name} — performing cleanup...{Color.END}")
            logging.warning(f"Signal received: {sig_name}")

            # Best-effort state save
            try:
                self.save_installation_state()
                self.save_rollback_manifest()
                logging.info("State saved during signal cleanup")
            except (IOError, OSError):
                pass

            print(f"{Color.CYAN}State saved. Check logs: {LOG_FILE}{Color.END}")
            sys.exit(128 + signum)

        signal.signal(signal.SIGTERM, _signal_handler)
        # SIGINT is also handled by KeyboardInterrupt in run(),
        # but this provides a fallback for non-interactive contexts
        signal.signal(signal.SIGINT, _signal_handler)

        logging.debug("Signal handlers registered (SIGTERM, SIGINT)")

    def _init_config_from_args(self) -> InstallationConfig:
        """
        Initialize installation configuration from CLI arguments

        Falls back to interactive mode if no arguments provided

        Returns:
            InstallationConfig object
        """
        config = InstallationConfig()

        # If no args object or no specific flags, return default (interactive mode)
        if not hasattr(self, 'args') or not self.args:
            return config

        # General options
        config.dry_run = getattr(self.args, 'dry_run', False)
        config.auto_yes = getattr(self.args, 'yes', False)
        config.verbose = getattr(self.args, 'verbose', False)
        config.create_backup = not getattr(self.args, 'no_backup', False)
        config.skip_update = getattr(self.args, 'skip_update', False)

        # GPU/Driver options
        config.install_nvidia_drivers = getattr(self.args, 'nvidia', False)
        config.install_amd_drivers = getattr(self.args, 'amd', False)
        config.install_intel_drivers = getattr(self.args, 'intel', False)
        config.install_vm_tools = getattr(self.args, 'vm_tools', False)

        # Gaming platforms
        if getattr(self.args, 'all_platforms', False):
            config.install_steam = True
            config.install_lutris = True
            config.install_heroic = True
            config.install_protonup = True
        else:
            config.install_steam = getattr(self.args, 'steam', False)
            config.install_lutris = getattr(self.args, 'lutris', False)
            config.install_heroic = getattr(self.args, 'heroic', False)
            config.install_protonup = getattr(self.args, 'protonup', False)

        # Specialized platforms (always from explicit flags)
        config.install_sober = getattr(self.args, 'sober', False)
        config.install_waydroid = getattr(self.args, 'waydroid', False)

        # Compatibility layers
        config.install_wine = getattr(self.args, 'wine', False)
        config.install_winetricks = getattr(self.args, 'winetricks', False)
        config.install_dxvk = getattr(self.args, 'dxvk', False)
        config.install_vkd3d = getattr(self.args, 'vkd3d', False)
        config.install_ge_proton = getattr(self.args, 'ge_proton', False)

        # Performance tools
        config.install_gamemode = getattr(self.args, 'gamemode', False)
        config.install_mangohud = getattr(self.args, 'mangohud', False)
        config.install_goverlay = getattr(self.args, 'goverlay', False)
        config.install_greenwithenv = getattr(self.args, 'gwe', False)

        # Graphics enhancement
        config.install_vkbasalt = getattr(self.args, 'vkbasalt', False)
        config.install_reshade_setup = getattr(self.args, 'reshade', False)

        # Additional tools
        config.install_discord = getattr(self.args, 'discord', False)
        config.install_obs = getattr(self.args, 'obs', False)
        config.install_mumble = getattr(self.args, 'mumble', False)
        config.install_teamspeak = getattr(self.args, 'teamspeak', False)
        config.install_mod_managers = getattr(self.args, 'mod_managers', False)
        config.install_controller_support = getattr(self.args, 'controllers', False)
        config.install_essential_packages = getattr(self.args, 'essential', False)
        config.install_codecs = getattr(self.args, 'codecs', False)

        # System optimizations
        config.apply_system_optimizations = getattr(self.args, 'optimize', False)
        config.create_performance_launcher = getattr(self.args, 'launcher', False)
        config.install_custom_kernel = getattr(self.args, 'custom_kernel', False)

        preset = getattr(self.args, 'preset', None)
        if preset:
            config = self._apply_preset(preset, config)

        return config

    # ═══════════════════════════════════════════════════════════════════════════
    # CONFIGURATION PRESETS
    # ═══════════════════════════════════════════════════════════════════════════

    def _apply_preset(self, preset_name: str,
                      config: InstallationConfig) -> InstallationConfig:
        """
        Apply a named configuration preset to the InstallationConfig.


        overriding anything the user explicitly set via CLI flags.

        Presets:
            minimal:   Drivers + Steam only
            standard:  + Wine, Lutris, Heroic, GameMode, MangoHud, essentials
            complete:  All components enabled
            streaming: Standard + OBS, Discord, Mumble

        Args:
            preset_name: Name of the preset to apply
            config: Current InstallationConfig (explicit flags already set)

        Returns:
            Updated InstallationConfig
        """
        logging.info(f"Applying preset: '{preset_name}'")
        print(f"{Color.CYAN}Applying preset: {preset_name}{Color.END}")

        presets = {
            'minimal': {
                'install_steam': True,
                'install_essential_packages': True,
            },
            'standard': {
                'install_steam': True,
                'install_lutris': True,
                'install_heroic': True,
                'install_protonup': True,
                'install_wine': True,
                'install_winetricks': True,
                'install_gamemode': True,
                'install_mangohud': True,
                'install_essential_packages': True,
                'install_codecs': True,
                'apply_system_optimizations': True,
                'create_performance_launcher': True,
            },
            'complete': {
                'install_steam': True,
                'install_lutris': True,
                'install_heroic': True,
                'install_protonup': True,
                'install_sober': True,
                'install_waydroid': True,
                'install_wine': True,
                'install_winetricks': True,
                'install_ge_proton': True,
                'install_gamemode': True,
                'install_mangohud': True,
                'install_goverlay': True,
                'install_vkbasalt': True,
                'install_discord': True,
                'install_obs': True,
                'install_mumble': True,
                'install_mod_managers': True,
                'install_controller_support': True,
                'install_essential_packages': True,
                'install_codecs': True,
                'apply_system_optimizations': True,
                'create_performance_launcher': True,
            },
            'streaming': {
                'install_steam': True,
                'install_lutris': True,
                'install_heroic': True,
                'install_protonup': True,
                'install_wine': True,
                'install_winetricks': True,
                'install_gamemode': True,
                'install_mangohud': True,
                'install_discord': True,
                'install_obs': True,
                'install_mumble': True,
                'install_essential_packages': True,
                'install_codecs': True,
                'apply_system_optimizations': True,
                'create_performance_launcher': True,
            },
        }

        if preset_name not in presets:
            logging.warning(f"Unknown preset: '{preset_name}'")
            print(f"{Color.YELLOW}⚠ Unknown preset '{preset_name}'. "
                  f"Valid: {', '.join(presets.keys())}{Color.END}")
            return config

        preset_flags = presets[preset_name]
        applied = []

        for flag, value in preset_flags.items():
            # Only set flags that weren't explicitly set by user CLI args
            current = getattr(config, flag, None)
            if current is False and value is True:
                setattr(config, flag, True)
                applied.append(flag.replace('install_', '').replace('_', '-'))

        if applied:
            print(f"  Components enabled: {', '.join(applied)}")

        logging.info(f"Preset '{preset_name}' applied: {len(applied)} flags set")
        return config

    # ═══════════════════════════════════════════════════════════════════════════
    # SYSTEM REQUIREMENTS PRE-CHECK — NEW
    # ═══════════════════════════════════════════════════════════════════════════

    def check_system_requirements(self) -> bool:
        """
        Validate system requirements before starting installation.


        architecture, and dpkg lock status.

        Returns:
            True if all requirements met (or user chose to continue)
        """
        self.banner("SYSTEM REQUIREMENTS CHECK")

        all_ok = True
        warnings = []
        errors = []

        # 1. Architecture check
        arch = platform.machine()
        if arch in ('x86_64', 'amd64'):
            print(f"  {Color.GREEN}✓{Color.END} Architecture: {arch}")
        elif arch in ('i386', 'i686'):
            warnings.append(f"32-bit architecture ({arch}) — some packages may be unavailable")
            print(f"  {Color.YELLOW}⚠{Color.END} Architecture: {arch} (32-bit — limited support)")
        else:
            errors.append(f"Unsupported architecture: {arch}")
            print(f"  {Color.RED}✗{Color.END} Architecture: {arch} (unsupported)")

        # 2. Disk space check
        try:
            stat = os.statvfs('/')
            free_gb = (stat.f_bavail * stat.f_frsize) / (1024 ** 3)

            if free_gb >= WARN_DISK_SPACE_GB:
                print(f"  {Color.GREEN}✓{Color.END} Disk space: {free_gb:.1f} GB free")
            elif free_gb >= MIN_DISK_SPACE_GB:
                warnings.append(f"Low disk space: {free_gb:.1f} GB free (recommended: ≥{WARN_DISK_SPACE_GB} GB)")
                print(f"  {Color.YELLOW}⚠{Color.END} Disk space: {free_gb:.1f} GB free (low)")
            else:
                errors.append(f"Insufficient disk space: {free_gb:.1f} GB free (minimum: {MIN_DISK_SPACE_GB} GB)")
                print(f"  {Color.RED}✗{Color.END} Disk space: {free_gb:.1f} GB free (insufficient)")
                all_ok = False
        except OSError as e:
            logging.warning(f"Could not check disk space: {e}")
            print(f"  {Color.YELLOW}⚠{Color.END} Disk space: could not determine")

        # 3. RAM check
        try:
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if line.startswith('MemTotal:'):
                        mem_kb = int(line.split()[1])
                        mem_gb = mem_kb / (1024 * 1024)
                        break
                else:
                    mem_gb = 0

            if mem_gb >= MIN_RAM_GB:
                print(f"  {Color.GREEN}✓{Color.END} RAM: {mem_gb:.1f} GB")
            else:
                warnings.append(f"Low RAM: {mem_gb:.1f} GB (recommended: ≥{MIN_RAM_GB} GB)")
                print(f"  {Color.YELLOW}⚠{Color.END} RAM: {mem_gb:.1f} GB (low)")
        except (OSError, ValueError) as e:
            logging.warning(f"Could not check RAM: {e}")
            print(f"  {Color.YELLOW}⚠{Color.END} RAM: could not determine")

        # 4. dpkg lock check
        dpkg_lock_files = ['/var/lib/dpkg/lock-frontend', '/var/lib/dpkg/lock']
        dpkg_locked = False

        for lock_file in dpkg_lock_files:
            try:
                fd = os.open(lock_file, os.O_RDONLY | os.O_CREAT)
                try:
                    import fcntl
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    fcntl.flock(fd, fcntl.LOCK_UN)
                except (IOError, OSError):
                    dpkg_locked = True
                finally:
                    os.close(fd)
            except (OSError, PermissionError):
                pass

        if dpkg_locked:
            errors.append("dpkg is locked — another package manager is running")
            print(f"  {Color.RED}✗{Color.END} dpkg: locked (another process is using it)")
            all_ok = False
        else:
            print(f"  {Color.GREEN}✓{Color.END} dpkg: available")

        # 5. Python version check
        py_version = sys.version_info
        if py_version >= (3, 7):
            print(f"  {Color.GREEN}✓{Color.END} Python: {py_version.major}.{py_version.minor}.{py_version.micro}")
        else:
            errors.append(f"Python {py_version.major}.{py_version.minor} too old (need ≥3.7)")
            print(f"  {Color.RED}✗{Color.END} Python: {py_version.major}.{py_version.minor} (need ≥3.7)")
            all_ok = False

        # Summary
        print()
        if errors:
            for err in errors:
                print(f"  {Color.RED}ERROR: {err}{Color.END}")
        if warnings:
            for warn in warnings:
                print(f"  {Color.YELLOW}WARNING: {warn}{Color.END}")

        if all_ok and not errors:
            print(f"\n{Color.GREEN}✓ All system requirements met{Color.END}")
            logging.info("System requirements check: PASSED")
        elif errors:
            print(f"\n{Color.RED}✗ System requirements not met{Color.END}")
            logging.error(f"System requirements check: FAILED ({len(errors)} errors)")

            if not self.confirm("Continue anyway? (installation may fail)"):
                print("Installation cancelled due to unmet requirements.")
                sys.exit(1)

        return all_ok

    # ═══════════════════════════════════════════════════════════════════════════
    # PACKAGE PRE-FLIGHT VALIDATION — NEW
    # ═══════════════════════════════════════════════════════════════════════════

    def _preflight_packages(self, packages: List[str],
                            description: str = "") -> Tuple[List[str], List[str]]:
        """
        Validate package availability before attempting batch install.


        a package list into available and unavailable before calling apt.

        Args:
            packages: List of package names to validate
            description: Optional description for logging

        Returns:
            Tuple of (available_packages, unavailable_packages)
        """
        if not packages:
            return [], []

        available = []
        unavailable = []

        for pkg in packages:
            if not pkg or pkg.startswith('-'):
                continue
            if self._check_package_available(pkg):
                available.append(pkg)
            else:
                unavailable.append(pkg)

        if unavailable:
            logging.info(
                f"Pre-flight ({description}): {len(unavailable)} packages unavailable: "
                f"{', '.join(unavailable[:10])}"
            )
            if self.config.verbose:
                print(f"{Color.YELLOW}  Pre-flight: unavailable packages skipped: "
                      f"{', '.join(unavailable)}{Color.END}")

        logging.debug(
            f"Pre-flight ({description}): "
            f"{len(available)} available, {len(unavailable)} unavailable"
        )

        return available, unavailable

    # ═══════════════════════════════════════════════════════════════════════════
    # UPDATE MODE
    # ═══════════════════════════════════════════════════════════════════════════

    def perform_update(self):
        """
        Update all previously installed components.


        what was installed, then checks for and applies available updates.
        """
        self.banner("UPDATE MODE")

        # Load previous installation state
        if not self.installation_state:
            self.load_installation_state()

        if not self.installation_state:
            print(f"{Color.YELLOW}No previous installation state found{Color.END}")
            print(f"{Color.CYAN}  Run the installer first, then use --update{Color.END}")
            return

        last_run = self.installation_state.get('last_updated', 'unknown')
        session = self.installation_state.get('session_id', 'unknown')
        print(f"  Last installation: {last_run}")
        print(f"  Session: {session}")
        print()

        installed = self.installation_state.get('installed_packages', {})
        apt_packages = installed.get('apt', [])
        flatpak_apps = installed.get('flatpak', [])

        if not apt_packages and not flatpak_apps:
            print(f"{Color.YELLOW}No tracked packages to update{Color.END}")
            print(f"{Color.CYAN}  The state file may be from a pre-tracking version{Color.END}")
            return

        print(f"{Color.BOLD}Tracked Components:{Color.END}")
        print(f"  APT packages:    {len(apt_packages)}")
        print(f"  Flatpak apps:    {len(flatpak_apps)}")
        print()

        # Phase 1: System update
        if not self.config.skip_update:
            print(f"{Color.CYAN}Updating system package lists...{Color.END}")
            self.run_command(["apt-get", "update"], "Updating package lists")

        # Phase 2: APT package updates
        if apt_packages:
            print(f"\n{Color.BOLD}Checking APT package updates...{Color.END}")

            updates_available = []
            for pkg in apt_packages:
                has_update, installed_ver, available_ver = self.check_updates_available(pkg)
                if has_update:
                    updates_available.append((pkg, installed_ver, available_ver))
                    print(f"  {Color.CYAN}↑{Color.END} {pkg}: {installed_ver} → {available_ver}")

            if updates_available:
                print(f"\n  {len(updates_available)} updates available")
                if self.confirm(f"Apply {len(updates_available)} APT updates?"):
                    pkgs_to_update = [u[0] for u in updates_available]
                    self.run_command(
                        ["apt-get", "install", "-y", "--only-upgrade"] + pkgs_to_update,
                        f"Updating {len(pkgs_to_update)} APT packages"
                    )
                    print(f"{Color.GREEN}✓ APT updates applied{Color.END}")
            else:
                print(f"  {Color.GREEN}✓ All APT packages are up to date{Color.END}")

        # Phase 3: Flatpak updates
        if flatpak_apps:
            print(f"\n{Color.BOLD}Checking Flatpak updates...{Color.END}")

            success, stdout, _ = self.run_command(
                ["flatpak", "update", "-y"],
                "Updating Flatpak applications",
                check=False
            )
            if success:
                print(f"{Color.GREEN}✓ Flatpak applications updated{Color.END}")
            else:
                print(f"{Color.YELLOW}⚠ Flatpak update encountered issues{Color.END}")

        # Phase 4: GE-Proton version check
        ge_proton_dir = REAL_USER_HOME / ".steam" / "root" / "compatibilitytools.d"
        if ge_proton_dir.exists():
            existing_versions = [
                d.name for d in ge_proton_dir.iterdir()
                if d.is_dir() and 'GE-Proton' in d.name
            ]
            if existing_versions:
                print(f"\n{Color.BOLD}GE-Proton:{Color.END}")
                for v in sorted(existing_versions):
                    print(f"  Installed: {v}")

                if self.confirm("Check for newer GE-Proton version?"):
                    try:
                        api_url = (
                            "https://api.github.com/repos/"
                            "GloriousEggroll/proton-ge-custom/releases/latest"
                        )
                        req = urllib.request.Request(api_url)
                        req.add_header('User-Agent', 'debian-gaming-setup')
                        with urllib.request.urlopen(req, timeout=TIMEOUT_API) as response:
                            data = json.loads(response.read())
                        latest_tag = data.get('tag_name', '')

                        if latest_tag and latest_tag not in existing_versions:
                            print(f"  {Color.CYAN}↑ Newer version available: {latest_tag}{Color.END}")
                            if self.confirm(f"Install {latest_tag}?"):
                                self._install_ge_proton()
                        else:
                            print(f"  {Color.GREEN}✓ Latest GE-Proton already installed{Color.END}")
                    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
                        logging.warning(f"Could not check GE-Proton updates: {e}")
                        print(f"  {Color.YELLOW}⚠ Could not check for updates{Color.END}")

        # Update the state file with current timestamp
        self.installation_state['last_updated'] = datetime.now().isoformat()
        self.installation_state['last_update_mode'] = True
        self.save_installation_state()

        print(f"\n{Color.GREEN}✓ Update check complete{Color.END}")

    # ═══════════════════════════════════════════════════════════════════════════
    # SELF-UPDATE MECHANISM — NEW
    # ═══════════════════════════════════════════════════════════════════════════

    def check_self_update(self):
        """
        Check GitHub for a newer version of this script and offer to download it.


        release tag and compares against SCRIPT_VERSION. If newer, downloads
        the updated script to the current location.
        """
        self.banner("SELF-UPDATE CHECK")

        print(f"  Current version: {SCRIPT_VERSION}")
        print(f"  Repository: {GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}")
        print()

        api_url = f"{GITHUB_API_BASE}/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/releases/latest"

        try:
            req = urllib.request.Request(api_url)
            req.add_header('User-Agent', 'debian-gaming-setup')

            with urllib.request.urlopen(req, timeout=TIMEOUT_API) as response:
                data = json.loads(response.read())

            remote_tag = data.get('tag_name', '').lstrip('v')
            release_name = data.get('name', remote_tag)
            published_at = data.get('published_at', 'unknown')
            html_url = data.get('html_url', '')

            if not remote_tag:
                print(f"{Color.YELLOW}⚠ Could not determine latest version{Color.END}")
                return

            print(f"  Latest release: {release_name} (tag: {remote_tag})")
            print(f"  Published: {published_at}")

            # Version comparison (semantic version: major.minor.patch)
            local_parts = self._parse_version(SCRIPT_VERSION)
            remote_parts = self._parse_version(remote_tag)

            if remote_parts <= local_parts:
                print(f"\n{Color.GREEN}✓ You are running the latest version{Color.END}")
                logging.info(f"Self-update: current ({SCRIPT_VERSION}) is up to date")
                return

            print(f"\n{Color.CYAN}↑ Newer version available: {remote_tag}{Color.END}")

            # Find the script asset in release
            script_url = None
            for asset in data.get('assets', []):
                name = asset.get('name', '')
                if name == 'debian_gaming_setup.py' or name.endswith('_gaming_setup.py'):
                    script_url = asset.get('browser_download_url', '')
                    break

            if not script_url:
                # Fallback: point to the release page
                print(f"  {Color.CYAN}Download: {html_url}{Color.END}")
                print(f"  {Color.YELLOW}No direct download found in release assets{Color.END}")
                logging.info(f"Self-update: no script asset in release {remote_tag}")
                return

            if not self.confirm(f"Download and replace current script with v{remote_tag}?"):
                return

            # Download new version
            current_script = os.path.abspath(sys.argv[0])
            backup_script = f"{current_script}.v{SCRIPT_VERSION}.backup"

            # Backup current version
            if os.path.exists(current_script):
                shutil.copy2(current_script, backup_script)
                print(f"  Backed up current version to: {backup_script}")

            # Download new version
            download_path = f"{current_script}.new"
            success, _, _ = self.run_command(
                ["wget", "-O", download_path, script_url],
                f"Downloading v{remote_tag}"
            )

            if success and os.path.exists(download_path):
                # Verify it's valid Python
                try:
                    import py_compile
                    py_compile.compile(download_path, doraise=True)
                except py_compile.PyCompileError as e:
                    print(f"{Color.RED}✗ Downloaded file has syntax errors: {e}{Color.END}")
                    os.remove(download_path)
                    return

                # Replace current script
                os.replace(download_path, current_script)
                os.chmod(current_script, 0o755)

                print(f"\n{Color.GREEN}✓ Updated to v{remote_tag}{Color.END}")
                print(f"  {Color.CYAN}Please re-run the script to use the new version{Color.END}")
                logging.info(f"Self-update: updated from {SCRIPT_VERSION} to {remote_tag}")
            else:
                print(f"{Color.YELLOW}⚠ Download failed{Color.END}")
                if os.path.exists(download_path):
                    os.remove(download_path)

        except (urllib.error.URLError, urllib.error.HTTPError) as e:
            logging.warning(f"Self-update check failed: {e}")
            print(f"{Color.YELLOW}⚠ Could not reach GitHub: {e}{Color.END}")
            print(f"  {Color.CYAN}Check manually: "
                  f"https://github.com/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/releases{Color.END}")
        except (json.JSONDecodeError, OSError) as e:
            logging.error(f"Self-update parsing error: {e}")
            print(f"{Color.YELLOW}⚠ Update check failed: {e}{Color.END}")

    @staticmethod
    def _parse_version(version_str: str) -> Tuple[int, ...]:
        """
        Parse a semantic version string into a comparable tuple.



        Args:
            version_str: Version string like '2.4.0', 'v2.3.0', '2.4.0-beta'

        Returns:
            Tuple of integers (major, minor, patch)
        """
        clean = version_str.lstrip('v').split('-')[0]
        parts = []
        for part in clean.split('.'):
            try:
                parts.append(int(part))
            except ValueError:
                parts.append(0)
        # Pad to at least 3 parts
        while len(parts) < 3:
            parts.append(0)
        return tuple(parts[:3])

    # ═══════════════════════════════════════════════════════════════════════════
    # PREREQUISITE CHECKS
    # ═══════════════════════════════════════════════════════════════════════════

    def check_root(self):
        """
        Verify script is running with root privileges

        Exact same check
        """
        if os.geteuid() != 0:
            print(f"{Color.RED}This script must be run with sudo/root privileges{Color.END}")
            print(f"{Color.CYAN}Usage: sudo python3 {sys.argv[0]}{Color.END}")
            sys.exit(1)

    def check_debian_based(self):
        """
        Verify system is Debian-based

        with distro-aware detection
        """
        try:
            with open('/etc/os-release', 'r') as f:
                os_info = f.read().lower()

            debian_indicators = ['debian', 'ubuntu', 'mint', 'pop', 'elementary',
                               'zorin', 'kali', 'mx ', 'antiX', 'devuan', 'deepin']

            if not any(indicator in os_info for indicator in debian_indicators):
                if 'id_like' in os_info and ('debian' in os_info or 'ubuntu' in os_info):
                    logging.info("Detected Debian/Ubuntu derivative via ID_LIKE")
                else:
                    print(f"{Color.RED}This script is designed for Debian-based distributions{Color.END}")
                    if not self.confirm("Continue anyway?"):
                        sys.exit(0)
            else:
                # Just log the detected distro, don't enforce version
                distro_name = "Unknown"
                for line in os_info.split('\n'):
                    if line.startswith('pretty_name='):
                        distro_name = line.split('=')[1].strip('"')
                        break
                logging.info(f"Detected Debian-based distribution: {distro_name}")
        except (IOError, OSError, ValueError) as e:
            logging.error(f"Could not verify OS version: {e}")

    # ═══════════════════════════════════════════════════════════════════════════
    # USER INTERACTION
    # ═══════════════════════════════════════════════════════════════════════════

    def confirm(self, question: str) -> bool:
        """
        Ask user for confirmation

        Identical loop and validation
        Added auto-yes and dry-run support

        Args:
            question: Question to ask

        Returns:
            Boolean confirmation result
        """
        if self.config.auto_yes:
            print(f"{Color.CYAN}{question} [auto-yes]{Color.END}")
            return True

        if self.config.dry_run:
            print(f"{Color.YELLOW}[DRY RUN] {question} [would prompt]{Color.END}")
            return True

        while True:
            try:
                response = input(f"{Color.YELLOW}{question} (y/n): {Color.END}").lower()
                if response in ['y', 'yes']:
                    return True
                elif response in ['n', 'no']:
                    return False
                print("Please answer 'y' or 'n'")
            except (EOFError, KeyboardInterrupt):
                print()
                return False

    def banner(self, text: str):
        """
        Display section banner

        Identical formatting
        """
        print(f"\n{Color.BOLD}{Color.HEADER}{'='*60}{Color.END}")
        print(f"{Color.BOLD}{Color.HEADER}{text.center(60)}{Color.END}")
        print(f"{Color.BOLD}{Color.HEADER}{'='*60}{Color.END}\n")

    # ═══════════════════════════════════════════════════════════════════════════
    # COMMAND EXECUTION
    # ═══════════════════════════════════════════════════════════════════════════

    def run_command(self, cmd, description="", check=True, shell=False,
                   env=None, timeout=TIMEOUT_INSTALL) -> Tuple[bool, str, str]:
        """
        Execute shell command with logging and error handling

        All error handling, logging, timeout functionality
        Added dry-run mode, return values, better error tracking

        Args:
            cmd: Command to execute (list or string)
            description: Human-readable description
            check: Raise exception on error
            shell: Execute in shell
            env: Environment variables
            timeout: Command timeout in seconds

        Returns:
            Tuple of (success: bool, stdout: str, stderr: str)
        """
        if description:
            logging.info(description)
            if not self.config.dry_run:
                print(f"{Color.CYAN}>>> {description}{Color.END}")

        # DRY RUN MODE
        if self.config.dry_run:
            cmd_str = cmd if isinstance(cmd, str) else ' '.join(str(c) for c in cmd)
            print(f"{Color.YELLOW}[DRY RUN] Would execute: {cmd_str}{Color.END}")
            logging.info(f"[DRY RUN] Would execute: {cmd_str}")
            return True, "", ""

        try:
            # Set default environment with DEBIAN_FRONTEND=noninteractive
            if env is None:
                env = os.environ.copy()
                env['DEBIAN_FRONTEND'] = 'noninteractive'

            result = subprocess.run(
                cmd, capture_output=True, text=True,
                shell=shell, env=env, timeout=timeout
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                logging.warning(f"Command returned {result.returncode}: {error_msg}")

                if check:
                    self.failed_operations.append(description or str(cmd))

                return False, result.stdout, result.stderr

            self._auto_record_from_command(cmd, description, True)

            return True, result.stdout, result.stderr

        except subprocess.TimeoutExpired:
            logging.error(f"Command timed out after {timeout}s: {cmd}")
            self.failed_operations.append(f"TIMEOUT: {description or str(cmd)}")
            return False, "", f"Command timed out after {timeout} seconds"
        except FileNotFoundError as e:
            logging.error(f"Command not found: {e}")
            return False, "", str(e)
        except (OSError, subprocess.SubprocessError) as e:
            logging.error(f"Command execution failed: {e}")
            if check:
                self.failed_operations.append(description or str(cmd))
            return False, "", str(e)

    # ═══════════════════════════════════════════════════════════════════════════
    # REPOSITORY MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════

    def clean_broken_repos(self):
        """
        Clean up broken repository configurations

        Exact same logic for cleaning broken PPAs
        Added MangoHud PPA cleanup for Ubuntu 24.04
        """
        print(f"{Color.YELLOW}Checking for broken repositories...{Color.END}")

        result, stdout, stderr = self.run_command(
            ["apt-get", "update"],
            "Testing repository configuration",
            check=False
        )

        if not result:
            print(f"{Color.YELLOW}Found broken repositories, attempting cleanup...{Color.END}")

            ppa_dir = "/etc/apt/sources.list.d/"
            if os.path.exists(ppa_dir):
                for file in os.listdir(ppa_dir):
                    if any(broken in file.lower() for broken in ["lutris", "mangohud"]):
                        file_path = os.path.join(ppa_dir, file)
                        try:
                            if not self.config.dry_run:
                                backup_path = f"{file_path}.broken"
                                if os.path.exists(file_path):
                                    shutil.copy2(file_path, backup_path)
                                os.remove(file_path)
                            print(f"{Color.GREEN}Removed broken repository: {file}{Color.END}")
                        except (OSError, PermissionError) as e:
                            logging.error(f"Could not remove {file}: {e}")

            self.run_command(
                ["apt-get", "update"],
                "Updating after repository cleanup",
                check=False
            )

    # ═══════════════════════════════════════════════════════════════════════════
    # PACKAGE MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════

    def is_package_installed(self, package_name: str) -> bool:
        """
        Check if a package is installed

        Exact same dpkg check
        """
        try:
            result = subprocess.run(
                ["dpkg", "-s", package_name],
                capture_output=True, text=True, timeout=TIMEOUT_QUICK
            )
            return result.returncode == 0 and 'Status: install ok installed' in result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def get_package_version(self, package_name: str) -> Optional[str]:
        """
        Get installed package version

        Exact same dpkg-query parsing
        """
        try:
            result = subprocess.run(
                ["dpkg-query", "-W", "-f=${Version}", package_name],
                capture_output=True, text=True, timeout=TIMEOUT_QUICK
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return None

    def get_available_version(self, package_name: str) -> Optional[str]:
        """
        Get available package version from repos

        Exact same apt-cache parsing
        """
        try:
            result = subprocess.run(
                ["apt-cache", "policy", package_name],
                capture_output=True, text=True, timeout=TIMEOUT_NETWORK
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Candidate:' in line:
                        version = line.split(':')[1].strip()
                        if version != '(none)':
                            return version
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return None

    def is_flatpak_installed(self, app_id: str) -> bool:
        """
        Check if a Flatpak app is installed

        Exact same flatpak list check
        """
        try:
            result = subprocess.run(
                ["flatpak", "list", "--app"],
                capture_output=True, text=True, timeout=TIMEOUT_QUICK
            )
            return app_id in result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def get_flatpak_version(self, app_id: str) -> Optional[str]:
        """
        Get installed Flatpak version

        Exact same flatpak info parsing
        """
        try:
            result = subprocess.run(
                ["flatpak", "info", app_id],
                capture_output=True, text=True, timeout=TIMEOUT_QUICK
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Version:' in line:
                        return line.split(':')[1].strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return None

    def check_updates_available(self, package_name: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Check if updates are available for a package

        Exact same version comparison logic
        """
        installed = self.get_package_version(package_name)
        available = self.get_available_version(package_name)

        if installed and available and installed != available:
            return True, installed, available
        return False, installed, available

    # ═══════════════════════════════════════════════════════════════════════════
    # SMART INSTALLATION PROMPTS
    # ═══════════════════════════════════════════════════════════════════════════

    def prompt_install_or_update(self, software_name: str,
                                 package_name: Optional[str] = None,
                                 flatpak_id: Optional[str] = None) -> bool:
        """
        Smart prompt that checks installation status and offers update

        Core intelligent prompting system

        Args:
            software_name: Human-readable software name
            package_name: APT package name (optional)
            flatpak_id: Flatpak application ID (optional)

        Returns:
            True if user wants to install/update, False otherwise
        """
        if self.config.auto_yes:
            print(f"{Color.CYAN}Auto-installing {software_name}...{Color.END}")
            return True

        is_installed = False
        current_version = None
        available_version = None
        update_available = False

        if package_name:
            is_installed = self.is_package_installed(package_name)
            if is_installed:
                current_version = self.get_package_version(package_name)
                available_version = self.get_available_version(package_name)
                update_available = current_version != available_version

        if flatpak_id and not is_installed:
            is_installed = self.is_flatpak_installed(flatpak_id)
            if is_installed:
                current_version = self.get_flatpak_version(flatpak_id)

        if is_installed:
            if current_version:
                print(f"{Color.GREEN}✓ {software_name} is already installed (version: {current_version}){Color.END}")
            else:
                print(f"{Color.GREEN}✓ {software_name} is already installed{Color.END}")

            if update_available and available_version:
                print(f"{Color.CYAN}  Update available: {current_version} → {available_version}{Color.END}")
                return self.confirm(f"Update {software_name}?")
            else:
                return self.confirm(f"Reinstall {software_name}?")
        else:
            return self.confirm(f"Install {software_name}?")

    # ═══════════════════════════════════════════════════════════════════════════
    # SYSTEM DETECTION
    # ═══════════════════════════════════════════════════════════════════════════

    def detect_system(self):
        """
        Comprehensive system detection

        All OS detection logic
        Better distro family detection, desktop environment detection
        """
        self.banner("SYSTEM DETECTION")
        self.current_phase = InstallationPhase.DETECTION

        try:
            os_release = {}
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        os_release[key] = value.strip('"')

            self.system_info.distro_name = os_release.get('NAME', 'Unknown')
            self.system_info.distro_version = os_release.get('VERSION_ID', 'Unknown')
            self.system_info.distro_id = os_release.get('ID', 'unknown')
            self.system_info.distro_family = self._detect_distro_family(os_release)
            self.system_info.kernel_version = platform.release()
            self.system_info.architecture = platform.machine()
            self.system_info.desktop_environment = self._detect_desktop_environment()
            self.system_info.is_wsl = os.path.exists('/proc/sys/fs/binfmt_misc/WSLInterop')

            print(f"{Color.BOLD}System Information:{Color.END}")
            print(f"  Distribution:     {Color.CYAN}{self.system_info.distro_name} {self.system_info.distro_version}{Color.END}")
            print(f"  Family:           {Color.CYAN}{self.system_info.distro_family.value}{Color.END}")
            print(f"  Kernel:           {Color.CYAN}{self.system_info.kernel_version}{Color.END}")
            print(f"  Architecture:     {Color.CYAN}{self.system_info.architecture}{Color.END}")
            print(f"  Desktop:          {Color.CYAN}{self.system_info.desktop_environment}{Color.END}")
            if self.system_info.is_wsl:
                print(f"  Environment:      {Color.YELLOW}WSL (Windows Subsystem for Linux){Color.END}")
            print(f"  User:             {Color.CYAN}{REAL_USER}{Color.END}")
            print()

            logging.info(f"System detection complete: {self.system_info.distro_name} "
                        f"{self.system_info.distro_version}")

        except (IOError, OSError, ValueError) as e:
            logging.error(f"System detection failed: {e}")
            raise

    def _detect_distro_family(self, os_release: Dict[str, str]) -> DistroFamily:
        """
        Detect distribution family from OS release info
        """
        distro_id = os_release.get('ID', '').lower()
        id_like = os_release.get('ID_LIKE', '').lower()

        family_map = {
            'ubuntu': DistroFamily.UBUNTU,
            'debian': DistroFamily.DEBIAN,
            'linuxmint': DistroFamily.MINT,
            'kali': DistroFamily.KALI,
            'pop': DistroFamily.POPOS,
            'elementary': DistroFamily.ELEMENTARY,
            'zorin': DistroFamily.ZORIN,
        }

        if distro_id in family_map:
            return family_map[distro_id]

        for key, family in family_map.items():
            if key in id_like:
                return family

        return DistroFamily.UNKNOWN

    def _detect_desktop_environment(self) -> str:
        """Detect current desktop environment"""
        de = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
        session = os.environ.get('DESKTOP_SESSION', '').lower()

        combined = f"{de} {session}"

        if 'gnome' in combined:
            return 'GNOME'
        elif 'kde' in combined or 'plasma' in combined:
            return 'KDE Plasma'
        elif 'xfce' in combined:
            return 'XFCE'
        elif 'cinnamon' in combined:
            return 'Cinnamon'
        elif 'mate' in combined:
            return 'MATE'
        elif 'pantheon' in combined:
            return 'Pantheon'
        elif 'lxde' in combined or 'lxqt' in combined:
            return 'LXDE/LXQt'
        elif 'i3' in combined or 'sway' in combined:
            return 'Tiling WM'

        return 'Unknown'

    # ═══════════════════════════════════════════════════════════════════════════
    # DISTRIBUTION RESOLUTION SYSTEM
    # Provides dynamic codename mapping for all Debian-based distributions
    # ═══════════════════════════════════════════════════════════════════════════

    def _get_os_release_field(self, field_name: str) -> str:
        """
        Read a specific field from /etc/os-release safely.



        Args:
            field_name: The os-release field to read (e.g., 'VERSION_CODENAME')

        Returns:
            The field value as a string, or empty string if not found
        """
        try:
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(f'{field_name}='):
                        value = line.split('=', 1)[1].strip('"').strip("'")
                        return value
        except (FileNotFoundError, PermissionError, IOError) as e:
            logging.warning(f"Could not read /etc/os-release field '{field_name}': {e}")
        return ""

    def _get_ubuntu_codename(self) -> str:
        """
        Resolve the effective Ubuntu codename for this system.


        derivatives (Mint, Pop!_OS, Elementary, Zorin, etc.), and
        Debian systems by mapping to the nearest Ubuntu equivalent.

        Returns:
            Ubuntu codename string (e.g., 'noble', 'jammy', 'focal')
            or empty string if resolution fails entirely
        """
        # Step 1: Check UBUNTU_CODENAME (most direct)
        ubuntu_codename = self._get_os_release_field('UBUNTU_CODENAME')
        if ubuntu_codename:
            logging.info(f"Distro resolver: UBUNTU_CODENAME = '{ubuntu_codename}'")
            return ubuntu_codename

        # Step 2: Read VERSION_CODENAME and distro ID
        version_codename = self._get_os_release_field('VERSION_CODENAME')
        distro_id = self._get_os_release_field('ID').lower()
        distro_id_like = self._get_os_release_field('ID_LIKE').lower()
        version_id = self._get_os_release_field('VERSION_ID')

        logging.info(
            f"Distro resolver: ID='{distro_id}', ID_LIKE='{distro_id_like}', "
            f"VERSION_CODENAME='{version_codename}', VERSION_ID='{version_id}'"
        )

        # Step 3: If this IS Ubuntu, the VERSION_CODENAME is the answer
        if distro_id == 'ubuntu':
            if version_codename:
                return version_codename
            return self._ubuntu_version_to_codename(version_id)

        # Step 4: Derivative codename → Ubuntu codename mapping
        derivative_to_ubuntu = {
            # Linux Mint 22.x (Ubuntu 24.04 Noble)
            "wilma": "noble", "xia": "noble",
            # Linux Mint 21.x (Ubuntu 22.04 Jammy)
            "virginia": "jammy", "victoria": "jammy",
            "vera": "jammy", "vanessa": "jammy",
            # Linux Mint 20.x (Ubuntu 20.04 Focal)
            "una": "focal", "uma": "focal",
            "ulyssa": "focal", "ulyana": "focal",
            # LMDE (Debian-based, not Ubuntu)
            "faye": "bookworm", "elsie": "bullseye",
            # Pop!_OS (follows Ubuntu codenames)
            "jammy": "jammy", "noble": "noble",
            # Elementary OS
            "horus": "noble", "hera": "focal",
            "odin": "focal", "jolnir": "jammy",
            # Kali Linux
            "kali-rolling": "bookworm",
        }

        if version_codename and version_codename in derivative_to_ubuntu:
            resolved = derivative_to_ubuntu[version_codename]
            logging.info(f"Distro resolver: Mapped derivative '{version_codename}' → '{resolved}'")
            return resolved

        # Step 5: Distro-specific VERSION_ID resolution
        if distro_id == 'zorin':
            zorin_map = {"17": "jammy", "16": "focal"}
            major_version = version_id.split('.')[0] if version_id else ""
            if major_version in zorin_map:
                resolved = zorin_map[major_version]
                logging.info(f"Distro resolver: Zorin {major_version} → '{resolved}'")
                return resolved

        if distro_id == 'elementary':
            elementary_map = {"8": "noble", "7.1": "jammy", "7": "jammy", "6.1": "focal", "6": "focal"}
            if version_id in elementary_map:
                resolved = elementary_map[version_id]
                logging.info(f"Distro resolver: Elementary {version_id} → '{resolved}'")
                return resolved

        # Step 6: Debian codename → nearest Ubuntu equivalent
        debian_to_ubuntu = {
            "trixie": "noble", "bookworm": "jammy", "bullseye": "focal",
            "buster": "bionic", "sid": "noble",
        }

        if distro_id == 'debian' or 'debian' in distro_id_like:
            if version_codename and version_codename in debian_to_ubuntu:
                resolved = debian_to_ubuntu[version_codename]
                logging.info(f"Distro resolver: Debian '{version_codename}' → '{resolved}'")
                return resolved

        # Step 7: ID_LIKE fallback
        if 'ubuntu' in distro_id_like and version_codename:
            logging.info(f"Distro resolver: Unknown Ubuntu derivative, trying '{version_codename}'")
            return version_codename

        # Step 8: Cannot determine
        logging.warning(
            f"Distro resolver: Could not determine Ubuntu codename for "
            f"ID='{distro_id}', VERSION_CODENAME='{version_codename}'"
        )
        return ""

    def _ubuntu_version_to_codename(self, version_id: str) -> str:
        """Map Ubuntu VERSION_ID to codename"""
        ubuntu_versions = {
            "25.04": "plucky", "24.10": "oracular", "24.04": "noble",
            "23.10": "mantic", "23.04": "lunar", "22.10": "kinetic",
            "22.04": "jammy", "21.10": "impish", "21.04": "hirsute",
            "20.10": "groovy", "20.04": "focal", "18.04": "bionic",
        }
        codename = ubuntu_versions.get(version_id, "")
        if codename:
            logging.info(f"Distro resolver: Ubuntu {version_id} → '{codename}'")
        else:
            logging.warning(f"Distro resolver: Unknown Ubuntu version '{version_id}'")
        return codename

    def get_wine_codename(self) -> str:
        """
        Resolve the correct WineHQ repository codename for this system.


        """
        distro_id = self._get_os_release_field('ID').lower()

        winehq_debian_codenames = {"trixie", "bookworm", "bullseye", "buster"}
        winehq_ubuntu_codenames = {
            "plucky", "oracular", "noble", "mantic", "lunar",
            "kinetic", "jammy", "focal", "bionic"
        }

        # Pure Debian: use Debian codename directly
        version_codename = self._get_os_release_field('VERSION_CODENAME')
        if distro_id == 'debian' and version_codename in winehq_debian_codenames:
            logging.info(f"Wine resolver: Using Debian codename '{version_codename}' directly")
            return version_codename

        # Ubuntu and all derivatives: resolve to Ubuntu codename
        ubuntu_codename = self._get_ubuntu_codename()

        if ubuntu_codename in winehq_ubuntu_codenames:
            logging.info(f"Wine resolver: Using Ubuntu codename '{ubuntu_codename}'")
            return ubuntu_codename

        # Fallback to newest supported
        if ubuntu_codename:
            logging.warning(f"Wine resolver: '{ubuntu_codename}' not in WineHQ list, using newest")
            return "plucky"

        logging.error("Wine resolver: Could not determine any codename for WineHQ")
        return ""

    def get_wine_repo_base_url(self) -> str:
        """Determine correct WineHQ repository base URL (Debian vs Ubuntu path)"""
        distro_id = self._get_os_release_field('ID').lower()
        distro_id_like = self._get_os_release_field('ID_LIKE').lower()

        if distro_id == 'debian' and 'ubuntu' not in distro_id_like:
            return "https://dl.winehq.org/wine-builds/debian"
        return "https://dl.winehq.org/wine-builds/ubuntu"

    def get_waydroid_codename(self) -> str:
        """
        Resolve the correct codename for Waydroid repository setup.


        """
        version_codename = self._get_os_release_field('VERSION_CODENAME')
        if version_codename:
            logging.info(f"Waydroid resolver: Using system codename '{version_codename}'")
            return version_codename

        ubuntu_codename = self._get_ubuntu_codename()
        if ubuntu_codename:
            logging.info(f"Waydroid resolver: Fallback to Ubuntu codename '{ubuntu_codename}'")
            return ubuntu_codename

        logging.warning("Waydroid resolver: Could not determine system codename")
        return ""

    # ═══════════════════════════════════════════════════════════════════════════
    # DISTRO-AWARE PACKAGE RESOLUTION — NEW
    # ═══════════════════════════════════════════════════════════════════════════

    def _resolve_package_name(self, generic_name: str) -> str:
        """
        Resolve a generic package name to the correct distro-specific name.


        """
        distro_id = self._get_os_release_field('ID').lower()
        distro_id_like = self._get_os_release_field('ID_LIKE').lower()
        version_id = self._get_os_release_field('VERSION_ID')

        is_ubuntu_family = (
            distro_id == 'ubuntu' or
            distro_id in ('pop', 'zorin', 'elementary', 'linuxmint') or
            'ubuntu' in distro_id_like
        )
        is_debian_native = distro_id == 'debian' and 'ubuntu' not in distro_id_like

        major_version = ""
        try:
            major_version = version_id.split('.')[0] if version_id else ""
        except (AttributeError, IndexError):
            pass

        mappings = {
            "ubuntu-drivers-common": {
                "debian_native": None,
                "ubuntu_family": "ubuntu-drivers-common",
            },
            "linux-cpupower": {
                "ubuntu_24+": "linux-tools-generic",
                "ubuntu_family": "linux-cpupower",
                "debian_native": "linux-cpupower",
            },
            "steam-installer": {
                "debian_native": "steam",
                "ubuntu_family": "steam-installer",
            },
        }

        if generic_name not in mappings:
            return generic_name

        pkg_map = mappings[generic_name]

        if is_ubuntu_family and major_version:
            try:
                if int(major_version) >= 24 and "ubuntu_24+" in pkg_map:
                    return pkg_map["ubuntu_24+"]
            except ValueError:
                pass

        if is_ubuntu_family and "ubuntu_family" in pkg_map:
            resolved = pkg_map["ubuntu_family"]
            return resolved if resolved is not None else ""

        if is_debian_native and "debian_native" in pkg_map:
            resolved = pkg_map["debian_native"]
            return resolved if resolved is not None else ""

        return generic_name

    def _check_package_available(self, package_name: str) -> bool:
        """
        Check if a package exists in the currently configured repositories.


        """
        if not package_name:
            return False
        try:
            result = subprocess.run(
                ["apt-cache", "show", package_name],
                capture_output=True, text=True, timeout=TIMEOUT_NETWORK
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            logging.debug(f"Package availability check failed for '{package_name}': {e}")
            return False

    # ═══════════════════════════════════════════════════════════════════════════
    # NETWORK CONNECTIVITY CHECK
    # ═══════════════════════════════════════════════════════════════════════════

    def check_network_connectivity(self) -> bool:
        """
        Verify internet connectivity before starting download operations.



        Returns:
            True if at least one connectivity test succeeds
        """
        self.banner("NETWORK CONNECTIVITY CHECK")
        print(f"{Color.CYAN}Verifying internet connectivity...{Color.END}")

        distro_id = self._get_os_release_field('ID').lower()

        test_endpoints = []
        if distro_id == 'debian':
            test_endpoints.append(("Debian Repositories", "https://deb.debian.org"))
        else:
            test_endpoints.append(("Ubuntu Repositories", "https://archive.ubuntu.com"))
        test_endpoints.append(("GitHub", "https://github.com"))
        test_endpoints.append(("Flathub", "https://flathub.org"))

        any_success = False
        results = []

        for name, url in test_endpoints:
            try:
                req = urllib.request.Request(url, method='HEAD')
                with urllib.request.urlopen(req, timeout=TIMEOUT_NETWORK) as response:
                    results.append((name, True, ""))
                    any_success = True
            except urllib.error.URLError as e:
                results.append((name, False, str(e.reason)))
            except urllib.error.HTTPError as e:
                results.append((name, True, f"HTTP {e.code}"))
                any_success = True
            except OSError as e:
                results.append((name, False, str(e)))

        for name, success, detail in results:
            if success:
                print(f"  {Color.GREEN}✓{Color.END} {name}")
            else:
                print(f"  {Color.RED}✗{Color.END} {name} ({detail})")

        if any_success:
            print(f"\n{Color.GREEN}✓ Network connectivity verified{Color.END}")
            logging.info("Network connectivity check passed")
        else:
            print(f"\n{Color.RED}✗ No internet connectivity detected{Color.END}")
            print(f"{Color.YELLOW}  The script requires internet to download packages.{Color.END}")
            logging.error("Network connectivity check FAILED")

            if not self.confirm("Continue anyway? (downloads will likely fail)"):
                print("Installation cancelled due to network issues.")
                sys.exit(1)

        return any_success


    # ═══════════════════════════════════════════════════════════════════════════
    # ROLLBACK ACTION RECORDING
    # Records every reversible action so rollback can undo the installation.
    # ═══════════════════════════════════════════════════════════════════════════

    def record_action(self, action_type: ActionType, description: str,
                      packages: List[str] = None, files: List[str] = None,
                      backup_files: Dict[str, str] = None,
                      reversal_commands: List[List[str]] = None,
                      metadata: Dict[str, str] = None,
                      success: bool = True):
        """
        Record a reversible action in the rollback manifest.


        install operations. Each action stores enough info to reverse itself.

        Args:
            action_type: ActionType enum member
            description: Human-readable description
            packages: List of package names involved
            files: List of file paths created or modified
            backup_files: Dict of original_path -> backup_path
            reversal_commands: Commands to execute for reversal
            metadata: Additional context (URLs, versions, etc.)
            success: Whether the action succeeded
        """
        if self.config.dry_run:
            logging.info(f"[DRY RUN] Would record action: {action_type.value} -- {description}")
            return

        action = RollbackAction(
            action_type=action_type.value,
            timestamp=datetime.now().isoformat(),
            description=description,
            packages=packages or [],
            files=files or [],
            backup_files=backup_files or {},
            reversal_commands=reversal_commands or [],
            metadata=metadata or {},
            success=success,
        )

        self.rollback_actions.append(action)
        logging.info(f"Rollback recorded: [{action_type.value}] {description}")

        # Auto-persist after each action so we survive crashes
        self.save_rollback_manifest()

    def _record_package_install(self, packages: List[str], description: str,
                                success: bool = True):
        """
        Convenience: record an apt package installation.


        """
        self.record_action(
            action_type=ActionType.APT_INSTALL,
            description=description,
            packages=packages,
            reversal_commands=[["apt-get", "remove", "-y"] + packages],
            success=success,
        )

    def _record_flatpak_install(self, app_id: str, description: str,
                                success: bool = True):
        """
        Convenience: record a Flatpak application installation.


        """
        self.record_action(
            action_type=ActionType.FLATPAK_INSTALL,
            description=description,
            packages=[app_id],
            reversal_commands=[["flatpak", "uninstall", "-y", app_id]],
            success=success,
        )

    def _record_repo_add(self, repo_identifier: str, files_added: List[str],
                         description: str, success: bool = True):
        """
        Convenience: record a repository addition (PPA or .sources file).


        """
        reversal = []
        for f in files_added:
            reversal.append(["rm", "-f", f])
        reversal.append(["apt-get", "update"])

        self.record_action(
            action_type=ActionType.REPO_ADD,
            description=description,
            files=files_added,
            reversal_commands=reversal,
            metadata={"repo_identifier": repo_identifier},
            success=success,
        )

    def _record_file_create(self, file_path: str, description: str,
                            success: bool = True):
        """
        Convenience: record a file created by the script.


        """
        self.record_action(
            action_type=ActionType.FILE_CREATE,
            description=description,
            files=[file_path],
            reversal_commands=[["rm", "-f", file_path]],
            success=success,
        )

    def _record_file_modify(self, original_path: str, backup_path: str,
                            description: str, success: bool = True):
        """
        Convenience: record modification of an existing file.


        """
        self.record_action(
            action_type=ActionType.FILE_MODIFY,
            description=description,
            files=[original_path],
            backup_files={original_path: backup_path},
            reversal_commands=[["cp", "-f", backup_path, original_path]],
            success=success,
        )

    def _auto_record_from_command(self, cmd, description: str,
                                  success: bool):
        """
        Auto-detect and record apt/flatpak installs from run_command calls.


        methods gain rollback tracking without individual modification.

        Args:
            cmd: The command that was executed (list or string)
            description: Human-readable description
            success: Whether the command succeeded
        """
        if self.config.dry_run or not success:
            return

        # Normalize command to list form for inspection
        if isinstance(cmd, str):
            cmd_parts = cmd.split()
        else:
            cmd_parts = [str(c) for c in cmd]

        if len(cmd_parts) < 3:
            return

        # Detect apt-get install commands
        if (cmd_parts[0] == 'apt-get' and 'install' in cmd_parts and
                '-y' in cmd_parts):
            # Extract package names (everything after 'install' that isn't a flag)
            install_idx = cmd_parts.index('install')
            packages = [
                p for p in cmd_parts[install_idx + 1:]
                if not p.startswith('-') and p != '-y'
            ]
            if packages:
                self._record_package_install(packages, description, success)
            return

        # Detect flatpak install commands
        if (cmd_parts[0] == 'flatpak' and 'install' in cmd_parts and
                '-y' in cmd_parts):
            # Last argument is typically the app ID
            app_id = cmd_parts[-1]
            if '.' in app_id and not app_id.startswith('-'):
                self._record_flatpak_install(app_id, description, success)
            return

    # ═══════════════════════════════════════════════════════════════════════════
    # ROLLBACK MANIFEST PERSISTENCE
    # ═══════════════════════════════════════════════════════════════════════════

    def save_rollback_manifest(self):
        """
        Persist the rollback manifest to disk as versioned JSON.


        Manifest survives script crashes and can be loaded for later rollback.
        """
        if self.config.dry_run:
            return

        manifest = {
            "schema_version": ROLLBACK_SCHEMA_VERSION,
            "session_id": self._session_id,
            "script_version": SCRIPT_VERSION,
            "started_at": self.rollback_actions[0].timestamp if self.rollback_actions else "",
            "last_updated": datetime.now().isoformat(),
            "distro_info": {
                "name": self.system_info.distro_name,
                "version": self.system_info.distro_version,
                "id": self.system_info.distro_id,
            },
            "action_count": len(self.rollback_actions),
            "actions": [],
        }

        for action in self.rollback_actions:
            manifest["actions"].append({
                "action_type": action.action_type,
                "timestamp": action.timestamp,
                "description": action.description,
                "packages": action.packages,
                "files": action.files,
                "backup_files": action.backup_files,
                "reversal_commands": action.reversal_commands,
                "metadata": action.metadata,
                "success": action.success,
            })

        try:
            # Write atomically: write to temp file then rename
            tmp_path = str(ROLLBACK_FILE) + ".tmp"
            with open(tmp_path, 'w') as f:
                json.dump(manifest, f, indent=2)

            os.replace(tmp_path, str(ROLLBACK_FILE))

            uid, gid = get_real_user_uid_gid()
            os.chown(ROLLBACK_FILE, uid, gid)

            logging.debug(f"Rollback manifest saved: {len(self.rollback_actions)} actions")
        except (IOError, OSError) as e:
            logging.error(f"Could not save rollback manifest: {e}")

    def load_rollback_manifest(self) -> bool:
        """
        Load a previous rollback manifest from disk.



        Returns:
            True if manifest was loaded successfully
        """
        if not ROLLBACK_FILE.exists():
            logging.debug("No rollback manifest found")
            return False

        try:
            with open(ROLLBACK_FILE, 'r') as f:
                manifest = json.load(f)

            schema = manifest.get("schema_version", "0")
            if schema != ROLLBACK_SCHEMA_VERSION:
                logging.warning(
                    f"Rollback manifest schema mismatch: "
                    f"found v{schema}, expected v{ROLLBACK_SCHEMA_VERSION}"
                )

            # Only load actions from previous sessions if we are in rollback mode
            # During normal runs, we start fresh and append
            if hasattr(self, 'args') and getattr(self.args, 'rollback', False):
                self.rollback_actions = []
                for entry in manifest.get("actions", []):
                    action = RollbackAction(
                        action_type=entry.get("action_type", ""),
                        timestamp=entry.get("timestamp", ""),
                        description=entry.get("description", ""),
                        packages=entry.get("packages", []),
                        files=entry.get("files", []),
                        backup_files=entry.get("backup_files", {}),
                        reversal_commands=entry.get("reversal_commands", []),
                        metadata=entry.get("metadata", {}),
                        success=entry.get("success", True),
                    )
                    self.rollback_actions.append(action)

                logging.info(
                    f"Loaded rollback manifest: {len(self.rollback_actions)} actions "
                    f"from session {manifest.get('session_id', 'unknown')}"
                )
            else:
                logging.info(
                    f"Previous rollback manifest exists with "
                    f"{manifest.get('action_count', 0)} actions "
                    f"(session {manifest.get('session_id', 'unknown')})"
                )

            return True

        except (json.JSONDecodeError, KeyError, IOError) as e:
            logging.error(f"Could not load rollback manifest: {e}")
            return False

    # ═══════════════════════════════════════════════════════════════════════════
    # GPU DETECTION
    # ═══════════════════════════════════════════════════════════════════════════

    def detect_gpu(self):
        """
        Detect GPU type

        All lspci parsing and glxinfo cross-validation
        Better false-positive prevention, more VM types
        """
        self.banner("GPU DETECTION")

        # First check if running in a VM
        vm_type = self.detect_virtualization()
        if vm_type:
            print(f"{Color.YELLOW}⚠ Virtual Machine Detected: {vm_type}{Color.END}")
            print(f"{Color.CYAN}Virtual GPU drivers will be handled by VM guest tools{Color.END}")
            logging.info(f"Running in {vm_type} VM")
            self.hardware_info.vm_type = self._vm_type_str_to_enum(vm_type)
            self.hardware_info.gpu_vendor = GPUVendor.VIRTUAL
            return vm_type.lower()

        try:
            result = subprocess.run(['lspci'], capture_output=True, text=True, timeout=TIMEOUT_QUICK)
            lspci_output = result.stdout.lower()

            gpu_lines = []
            for line in lspci_output.split('\n'):
                if any(keyword in line for keyword in ['vga', '3d', 'display']):
                    gpu_lines.append(line)

            gpu_info = ' '.join(gpu_lines).lower()

            gl_info = ""
            try:
                gl_result = subprocess.run(['glxinfo'], capture_output=True,
                                          text=True, timeout=TIMEOUT_QUICK)
                if gl_result.returncode == 0:
                    for line in gl_result.stdout.split('\n'):
                        if 'OpenGL renderer' in line:
                            gl_info = line.lower()
                            break
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass

            logging.info(f"GPU detection - lspci VGA: {gpu_info}")
            logging.info(f"GPU detection - GL renderer: {gl_info}")

            # Check for virtual/emulated GPUs first
            if any(vm_indicator in gpu_info or vm_indicator in gl_info
                   for vm_indicator in ['vmware', 'virtualbox', 'qxl', 'virtio', 'svga3d']):
                print(f"{Color.YELLOW}⚠ Virtual GPU detected{Color.END}")
                logging.info("Virtual GPU detected in hardware scan")
                self.hardware_info.gpu_vendor = GPUVendor.VIRTUAL
                return 'generic'

            # Check for NVIDIA
            if 'nvidia' in gpu_info or 'nvidia' in gl_info:
                print(f"{Color.GREEN}✓ NVIDIA GPU detected{Color.END}")
                logging.info("NVIDIA GPU detected")
                self.hardware_info.gpu_vendor = GPUVendor.NVIDIA
                for line in gpu_lines:
                    if 'nvidia' in line:
                        self.hardware_info.gpu_model = self._extract_gpu_model(line)
                        break
                return 'nvidia'

            # Check for AMD/Radeon
            if any(amd_indicator in gpu_info or amd_indicator in gl_info
                   for amd_indicator in ['amd', 'radeon', 'ati']):
                print(f"{Color.GREEN}✓ AMD GPU detected{Color.END}")
                logging.info("AMD GPU detected")
                self.hardware_info.gpu_vendor = GPUVendor.AMD
                for line in gpu_lines:
                    if any(amd in line for amd in ['amd', 'radeon', 'ati']):
                        self.hardware_info.gpu_model = self._extract_gpu_model(line)
                        break
                return 'amd'

            # Check for Intel
            if ('intel' in gpu_info and any(gpu_term in gpu_info
                for gpu_term in ['graphics', 'hd', 'iris', 'uhd', 'arc'])):
                print(f"{Color.GREEN}✓ Intel GPU detected{Color.END}")
                logging.info("Intel GPU detected")
                self.hardware_info.gpu_vendor = GPUVendor.INTEL
                for line in gpu_lines:
                    if 'intel' in line:
                        self.hardware_info.gpu_model = self._extract_gpu_model(line)
                        break
                return 'intel'

            if gpu_lines:
                print(f"{Color.YELLOW}! Generic/Unknown GPU detected{Color.END}")
                print(f"{Color.CYAN}  GPU info: {gpu_lines[0] if gpu_lines else 'unknown'}{Color.END}")
                logging.info(f"Unknown GPU type: {gpu_lines}")
                self.hardware_info.gpu_vendor = GPUVendor.UNKNOWN
                return 'generic'

            print(f"{Color.YELLOW}! No GPU detected{Color.END}")
            self.hardware_info.gpu_vendor = GPUVendor.UNKNOWN
            return 'unknown'

        except (OSError, subprocess.SubprocessError, ValueError) as e:
            logging.error(f"GPU detection failed: {e}")
            self.hardware_info.gpu_vendor = GPUVendor.UNKNOWN
            return 'unknown'

    def _extract_gpu_model(self, lspci_line: str) -> str:
        """Extract GPU model from lspci line"""
        parts = lspci_line.split(':')
        if len(parts) >= 3:
            model = ':'.join(parts[2:]).strip()
            model = model.replace('vga compatible controller:', '').strip()
            model = model.replace('3d controller:', '').strip()
            model = model.replace('display controller:', '').strip()
            return model[:80]
        return "Unknown Model"

    def _vm_type_str_to_enum(self, vm_str: str) -> VMType:
        """Convert VM type string to enum"""
        vm_lower = vm_str.lower()
        if 'vmware' in vm_lower:
            return VMType.VMWARE
        elif 'virtualbox' in vm_lower or 'oracle' in vm_lower:
            return VMType.VIRTUALBOX
        elif 'kvm' in vm_lower:
            return VMType.KVM
        elif 'qemu' in vm_lower:
            return VMType.QEMU
        elif 'hyper-v' in vm_lower or 'microsoft' in vm_lower:
            return VMType.HYPERV
        elif 'xen' in vm_lower:
            return VMType.XEN
        elif 'parallels' in vm_lower:
            return VMType.PARALLELS
        return VMType.NONE

    def detect_virtualization(self):
        """
        Detect if running in a virtual machine and which type

        All three detection methods
        More VM types, better error handling
        """
        try:
            result = subprocess.run(['systemd-detect-virt'],
                                  capture_output=True, text=True, timeout=TIMEOUT_QUICK)
            virt_type = result.stdout.strip()

            if virt_type and virt_type != 'none':
                virt_map = {
                    'vmware': 'VMware', 'kvm': 'KVM', 'qemu': 'QEMU',
                    'virtualbox': 'VirtualBox', 'oracle': 'VirtualBox',
                    'microsoft': 'Hyper-V', 'xen': 'Xen', 'bochs': 'Bochs',
                    'parallels': 'Parallels'
                }
                return virt_map.get(virt_type.lower(), virt_type)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        try:
            result = subprocess.run(['dmesg'], capture_output=True, text=True, timeout=TIMEOUT_QUICK)
            dmesg = result.stdout.lower()

            if 'vmware' in dmesg:
                return 'VMware'
            elif 'virtualbox' in dmesg:
                return 'VirtualBox'
            elif 'hypervisor detected' in dmesg:
                return 'VM'
        except (FileNotFoundError, subprocess.TimeoutExpired, PermissionError):
            pass

        try:
            result = subprocess.run(['lspci'], capture_output=True, text=True, timeout=TIMEOUT_QUICK)
            lspci = result.stdout.lower()

            if 'vmware' in lspci:
                return 'VMware'
            elif 'virtualbox' in lspci:
                return 'VirtualBox'
            elif 'qxl' in lspci or 'virtio' in lspci:
                return 'KVM/QEMU'
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        return None

    # ═══════════════════════════════════════════════════════════════════════════
    # DYNAMIC NVIDIA DRIVER DETECTION
    # ═══════════════════════════════════════════════════════════════════════════

    def _detect_installed_nvidia_driver(self) -> Optional[str]:
        """
        Dynamically detect any installed NVIDIA driver package.


        """
        try:
            result = subprocess.run(
                ["dpkg", "-l"], capture_output=True, text=True, timeout=TIMEOUT_API
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    match = re.match(r'^ii\s+(nvidia-driver-\d+)\s+', line)
                    if match:
                        package_name = match.group(1)
                        logging.info(f"Dynamic NVIDIA detection: Found installed '{package_name}'")
                        return package_name
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            logging.warning(f"Dynamic NVIDIA detection via dpkg failed: {e}")
        return None

    def _get_recommended_nvidia_driver(self) -> Optional[str]:
        """
        Get the system-recommended NVIDIA driver using distro-native tools.


        """
        distro_id = self._get_os_release_field('ID').lower()
        distro_id_like = self._get_os_release_field('ID_LIKE').lower()
        is_ubuntu_family = (
            distro_id == 'ubuntu' or
            distro_id in ('pop', 'zorin', 'elementary', 'linuxmint') or
            'ubuntu' in distro_id_like
        )

        # Method 1: ubuntu-drivers (Ubuntu and derivatives)
        if is_ubuntu_family:
            drivers_pkg = self._resolve_package_name("ubuntu-drivers-common")
            if drivers_pkg and self._check_package_available(drivers_pkg):
                if not self.is_package_installed(drivers_pkg):
                    self.run_command(
                        ["apt-get", "install", "-y", drivers_pkg],
                        f"Installing {drivers_pkg} for driver detection",
                        check=False
                    )

                try:
                    result = subprocess.run(
                        ["ubuntu-drivers", "devices"],
                        capture_output=True, text=True, timeout=TIMEOUT_API
                    )
                    if result.returncode == 0:
                        recommended = None
                        for line in result.stdout.split('\n'):
                            if 'recommended' in line.lower():
                                match = re.search(r'(nvidia-driver-\d+)', line)
                                if match:
                                    return match.group(1)
                            elif 'nvidia-driver-' in line and recommended is None:
                                match = re.search(r'(nvidia-driver-\d+)', line)
                                if match:
                                    recommended = match.group(1)
                        if recommended:
                            return recommended
                except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
                    logging.warning(f"ubuntu-drivers detection failed: {e}")

        # Method 2: apt-cache search (Debian and fallback)
        try:
            result = subprocess.run(
                ["apt-cache", "search", "^nvidia-driver-[0-9]"],
                capture_output=True, text=True, timeout=TIMEOUT_API
            )
            if result.returncode == 0 and result.stdout.strip():
                available_drivers = []
                for line in result.stdout.strip().split('\n'):
                    match = re.match(r'^(nvidia-driver-(\d+))\s', line)
                    if match:
                        available_drivers.append((int(match.group(2)), match.group(1)))

                if available_drivers:
                    available_drivers.sort(reverse=True)
                    best = available_drivers[0][1]
                    logging.info(f"apt-cache NVIDIA: best = '{best}' (from {len(available_drivers)} options)")
                    return best
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            logging.warning(f"apt-cache NVIDIA search failed: {e}")

        # Method 3: meta-package fallback
        if self._check_package_available("nvidia-driver"):
            return "nvidia-driver"

        return None

    # ═══════════════════════════════════════════════════════════════════════════
    # NVIDIA DRIVER INSTALLATION — DYNAMIC
    # ═══════════════════════════════════════════════════════════════════════════

    def install_nvidia_drivers(self):
        """
        Install NVIDIA proprietary drivers with fully dynamic detection.

        Dynamic version detection, no hardcoded versions.
        Handles prompting, nvidia-smi display, and reinstall/upgrade flow.
        """
        self.banner("NVIDIA DRIVER INSTALLATION")

        installed_driver = self._detect_installed_nvidia_driver()

        if installed_driver:
            try:
                result = subprocess.run(
                    ["nvidia-smi"], capture_output=True, text=True, timeout=TIMEOUT_NETWORK
                )
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'Driver Version:' in line:
                            version = line.split('Driver Version:')[1].split()[0]
                            print(f"{Color.GREEN}✓ NVIDIA drivers already installed "
                                  f"(version: {version}, package: {installed_driver}){Color.END}")
                            break
                    else:
                        print(f"{Color.GREEN}✓ NVIDIA drivers already installed "
                              f"(package: {installed_driver}){Color.END}")

                    if not self.confirm("Reinstall/update NVIDIA drivers?"):
                        return
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                print(f"{Color.YELLOW}⚠ NVIDIA driver package '{installed_driver}' "
                      f"found but driver not loaded{Color.END}")
                if not self.confirm("Reinstall NVIDIA drivers?"):
                    return

        recommended = self._get_recommended_nvidia_driver()

        if not recommended:
            print(f"{Color.RED}✗ Could not determine appropriate NVIDIA driver{Color.END}")
            print(f"{Color.CYAN}  Try: sudo apt-get install nvidia-driver{Color.END}")
            logging.error("NVIDIA install: could not determine recommended driver")
            return

        print(f"{Color.CYAN}Recommended NVIDIA driver: {recommended}{Color.END}")
        logging.info(f"NVIDIA install: selected driver = '{recommended}'")

        distro_id = self._get_os_release_field('ID').lower()
        distro_id_like = self._get_os_release_field('ID_LIKE').lower()
        is_ubuntu_family = (
            distro_id == 'ubuntu' or
            distro_id in ('pop', 'zorin', 'elementary', 'linuxmint') or
            'ubuntu' in distro_id_like
        )

        if is_ubuntu_family and self.is_package_installed("ubuntu-drivers-common"):
            print(f"{Color.CYAN}Using ubuntu-drivers for optimal installation...{Color.END}")
            success, _, _ = self.run_command(
                ["ubuntu-drivers", "autoinstall"],
                "Installing NVIDIA drivers via ubuntu-drivers",
                check=False
            )
            if not success:
                print(f"{Color.YELLOW}⚠ ubuntu-drivers failed, trying direct install...{Color.END}")
                self.run_command(
                    ["apt-get", "install", "-y", recommended],
                    f"Installing {recommended} via apt"
                )
        else:
            self.run_command(
                ["apt-get", "install", "-y", recommended],
                f"Installing {recommended}"
            )

        companion_packages = []
        if self._check_package_available("nvidia-settings"):
            companion_packages.append("nvidia-settings")
        if is_ubuntu_family and self._check_package_available("nvidia-prime"):
            companion_packages.append("nvidia-prime")

        if companion_packages:
            self.run_command(
                ["apt-get", "install", "-y"] + companion_packages,
                f"Installing NVIDIA companion tools ({', '.join(companion_packages)})",
                check=False
            )

        print(f"{Color.GREEN}✓ NVIDIA drivers installed{Color.END}")
        logging.info("NVIDIA driver installation complete")

    # ═══════════════════════════════════════════════════════════════════════════
    # AMD DRIVER INSTALLATION — DISTRO-AWARE
    # ═══════════════════════════════════════════════════════════════════════════

    def install_amd_drivers(self):
        """
        Install AMD Mesa/AMDGPU drivers with distro-aware package selection.

        Availability checking, Debian firmware awareness.
        Installs core Mesa/Vulkan packages for AMD GPU support.
        """
        self.banner("AMD DRIVER INSTALLATION")

        print(f"{Color.CYAN}Installing AMD Mesa and Vulkan drivers...{Color.END}")

        distro_id = self._get_os_release_field('ID').lower()
        distro_id_like = self._get_os_release_field('ID_LIKE').lower()
        is_debian_native = distro_id == 'debian' and 'ubuntu' not in distro_id_like

        core_packages = [
            "mesa-vulkan-drivers", "mesa-vulkan-drivers:i386",
            "libvulkan1", "libvulkan1:i386", "vulkan-tools", "mesa-utils",
        ]

        if is_debian_native:
            if self._check_package_available("firmware-amd-graphics"):
                core_packages.append("firmware-amd-graphics")
            else:
                print(f"{Color.YELLOW}⚠ firmware-amd-graphics not available. "
                      f"Ensure 'non-free' is enabled in sources.list{Color.END}")

        optional_packages = ["libdrm-amdgpu1", "xserver-xorg-video-amdgpu", "radeontop"]
        available_optional = [pkg for pkg in optional_packages if self._check_package_available(pkg)]

        self.run_command(
            ["apt-get", "install", "-y"] + core_packages,
            "Installing AMD Mesa and Vulkan core drivers"
        )

        if available_optional:
            self.run_command(
                ["apt-get", "install", "-y"] + available_optional,
                f"Installing AMD optional packages ({', '.join(available_optional)})",
                check=False
            )

        print(f"{Color.GREEN}✓ AMD drivers installed{Color.END}")

    # ═══════════════════════════════════════════════════════════════════════════
    # INTEL DRIVER INSTALLATION — DISTRO-AWARE
    # ═══════════════════════════════════════════════════════════════════════════

    def install_intel_drivers(self):
        """
        Install Intel graphics drivers with distro-aware package selection.

        Availability checking, Arc GPU support, Debian firmware.
        Installs core Mesa/Intel packages with media acceleration support.
        """
        self.banner("INTEL DRIVER INSTALLATION")

        print(f"{Color.CYAN}Installing Intel graphics drivers...{Color.END}")

        distro_id = self._get_os_release_field('ID').lower()
        distro_id_like = self._get_os_release_field('ID_LIKE').lower()
        is_debian_native = distro_id == 'debian' and 'ubuntu' not in distro_id_like

        core_packages = [
            "mesa-vulkan-drivers", "mesa-vulkan-drivers:i386",
            "libvulkan1", "libvulkan1:i386", "mesa-utils",
        ]

        for pkg in ["intel-media-va-driver", "i965-va-driver"]:
            if self._check_package_available(pkg):
                core_packages.append(pkg)

        if is_debian_native:
            for fw_pkg in ["firmware-misc-nonfree", "intel-microcode"]:
                if self._check_package_available(fw_pkg):
                    core_packages.append(fw_pkg)

        gpu_model = self.hardware_info.gpu_model.lower()
        if 'arc' in gpu_model or 'a770' in gpu_model or 'a750' in gpu_model:
            print(f"{Color.CYAN}  Intel Arc GPU detected — ensuring latest Mesa support{Color.END}")
            if self._check_package_available("intel-opencl-icd"):
                core_packages.append("intel-opencl-icd")

        self.run_command(
            ["apt-get", "install", "-y"] + core_packages,
            "Installing Intel graphics drivers"
        )

        print(f"{Color.GREEN}✓ Intel drivers installed{Color.END}")

    # ═══════════════════════════════════════════════════════════════════════════
    # VM TOOLS — DISTRO-AWARE
    # ═══════════════════════════════════════════════════════════════════════════

    def install_vm_tools(self, vm_type):
        """
        Install VM guest tools with distro-aware package availability checking.

        Pre-install detection checks for existing guest tools before prompting.
        Package availability verification before install.
        Supports VMware, VirtualBox, KVM/QEMU, Hyper-V, Xen, and Parallels.
        """
        self.banner("VM GUEST TOOLS INSTALLATION")

        # --- Pre-install detection: check if VM tools are already present ---
        vm_lower = vm_type.lower()
        existing_version = None
        existing_tool = None

        if 'vmware' in vm_lower:
            if shutil.which("vmware-toolbox-cmd"):
                success, stdout, _ = self.run_command(
                    ["vmware-toolbox-cmd", "-v"],
                    "Checking VMware Tools version", check=False
                )
                if success and stdout.strip():
                    existing_version = stdout.strip()
                    existing_tool = "VMware Tools"
            elif self.is_package_installed("open-vm-tools"):
                existing_version = self.get_package_version("open-vm-tools")
                existing_tool = "open-vm-tools"

        elif 'virtualbox' in vm_lower:
            if self.is_package_installed("virtualbox-guest-utils"):
                existing_version = self.get_package_version("virtualbox-guest-utils")
                existing_tool = "VirtualBox Guest Utils"
            elif shutil.which("VBoxClient"):
                existing_tool = "VirtualBox Guest Additions"

        elif 'kvm' in vm_lower or 'qemu' in vm_lower:
            if self.is_package_installed("qemu-guest-agent"):
                existing_version = self.get_package_version("qemu-guest-agent")
                existing_tool = "QEMU Guest Agent"

        elif 'hyper-v' in vm_lower or 'microsoft' in vm_lower:
            if self.is_package_installed("hyperv-daemons"):
                existing_version = self.get_package_version("hyperv-daemons")
                existing_tool = "Hyper-V Daemons"

        elif 'xen' in vm_lower:
            if self.is_package_installed("xe-guest-utilities"):
                existing_version = self.get_package_version("xe-guest-utilities")
                existing_tool = "Xen Guest Utilities"

        # Report existing installation and offer reinstall
        if existing_tool:
            if existing_version:
                print(f"{Color.GREEN}✓ {existing_tool} already installed "
                      f"(v{existing_version}){Color.END}")
            else:
                print(f"{Color.GREEN}✓ {existing_tool} already installed{Color.END}")
            if not self.confirm(f"Reinstall {vm_type} guest tools?"):
                return
        else:
            print(f"{Color.CYAN}Detected {vm_type} — Installing guest tools...{Color.END}")

        if 'vmware' in vm_lower:
            self._install_vm_packages("VMware",
                ["open-vm-tools", "open-vm-tools-desktop"],
                optional=["mesa-utils"])
        elif 'virtualbox' in vm_lower:
            self._install_vm_packages("VirtualBox",
                ["virtualbox-guest-utils", "virtualbox-guest-x11"],
                optional=["virtualbox-guest-dkms", "mesa-utils"])
        elif 'kvm' in vm_lower or 'qemu' in vm_lower:
            self._install_vm_packages("KVM/QEMU",
                ["qemu-guest-agent", "spice-vdagent"],
                optional=["xserver-xorg-video-qxl", "mesa-utils"])
        elif 'hyper-v' in vm_lower or 'microsoft' in vm_lower:
            self._install_vm_packages("Hyper-V",
                ["hyperv-daemons"],
                optional=["linux-tools-virtual", "linux-cloud-tools-virtual"])
        elif 'xen' in vm_lower:
            self._install_vm_packages("Xen", [],
                optional=["xe-guest-utilities"])
        elif 'parallels' in vm_lower:
            print(f"{Color.CYAN}Parallels Tools should be installed from the "
                  f"Parallels Desktop menu: Actions → Install Parallels Tools{Color.END}")
        else:
            self.install_generic_vm_graphics()

        print(f"{Color.GREEN}✓ {vm_type} guest tools installation complete{Color.END}")

    def _install_vm_packages(self, vm_name: str, required: list, optional: list = None):
        """
        Install VM packages with availability checking.


        """
        optional = optional or []

        available_required = [pkg for pkg in required if self._check_package_available(pkg)]
        missing_required = [pkg for pkg in required if not self._check_package_available(pkg)]

        if missing_required:
            print(f"{Color.YELLOW}⚠ Some {vm_name} packages not available: "
                  f"{', '.join(missing_required)}{Color.END}")

        if available_required:
            self.run_command(
                ["apt-get", "install", "-y"] + available_required,
                f"Installing {vm_name} guest tools"
            )

        available_optional = [pkg for pkg in optional if self._check_package_available(pkg)]
        if available_optional:
            self.run_command(
                ["apt-get", "install", "-y"] + available_optional,
                f"Installing {vm_name} optional packages",
                check=False
            )

    def install_generic_vm_graphics(self):
        """Install generic VM graphics support - """
        packages = [
            "mesa-utils", "mesa-utils-extra", "libgl1-mesa-dri",
            "libgl1-mesa-dri:i386", "mesa-vulkan-drivers", "mesa-vulkan-drivers:i386"
        ]
        self.run_command(
            ["apt-get", "install", "-y"] + packages,
            "Installing generic VM graphics drivers"
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # SYSTEM UPDATE
    # ═══════════════════════════════════════════════════════════════════════════

    def update_system(self):
        """Update system packages - """
        if self.config.skip_update:
            print(f"{Color.YELLOW}Skipping system update as requested{Color.END}")
            return

        self.banner("SYSTEM UPDATE")

        commands = [
            (["apt-get", "update"], "Updating package lists"),
            (["apt-get", "upgrade", "-y"], "Upgrading installed packages"),
            (["apt-get", "autoremove", "-y"], "Removing unnecessary packages"),
            (["apt-get", "autoclean"], "Cleaning package cache")
        ]

        for cmd, desc in commands:
            self.run_command(cmd, desc)

    def enable_32bit_support(self):
        """Enable 32-bit architecture support - """
        self.banner("32-BIT SUPPORT")

        result = subprocess.run(["dpkg", "--print-foreign-architectures"],
                              capture_output=True, text=True, timeout=TIMEOUT_QUICK)

        if 'i386' in result.stdout:
            print(f"{Color.GREEN}✓ 32-bit support already enabled{Color.END}")
            return

        self.run_command(["dpkg", "--add-architecture", "i386"],
                        "Adding i386 architecture")
        self.run_command(["apt-get", "update"], "Updating package lists")

    # ═══════════════════════════════════════════════════════════════════════════
    # ESSENTIAL PACKAGES
    # ═══════════════════════════════════════════════════════════════════════════

    def install_essential_packages(self):
        """
        Install essential gaming packages.

        Same package list and fallback logic.
        Pre-flight validation via _preflight_packages()
        to skip unavailable packages cleanly instead of letting apt fail.
        """
        self.banner("ESSENTIAL PACKAGES")

        # Resolve distro-specific package names
        cpupower_pkg = self._resolve_package_name("linux-cpupower")

        packages = [
            "curl", "wget",
            "libgl1-mesa-dri:i386", "mesa-vulkan-drivers", "mesa-vulkan-drivers:i386",
            "pulseaudio", "pavucontrol",
            "joystick", "jstest-gtk",
            "fonts-liberation", "fonts-wine",
            cpupower_pkg,
            "xboxdrv", "antimicrox"
        ]

        # Filter out empty package names
        packages = [p for p in packages if p]

        available, unavailable = self._preflight_packages(packages, "essential packages")

        if unavailable:
            print(f"{Color.YELLOW}  Skipping {len(unavailable)} unavailable packages: "
                  f"{', '.join(unavailable)}{Color.END}")

        if available:
            self.run_command(
                ["apt-get", "install", "-y"] + available,
                f"Installing {len(available)} essential packages",
                check=False
            )
        else:
            print(f"{Color.YELLOW}⚠ No essential packages available for install{Color.END}")

    def install_codecs(self):
        """
        Install multimedia codecs.

        Same codecs and EULA pre-acceptance.
        Eliminated shell=True. Uses subprocess
        pipe for debconf-set-selections and list-form for apt install.
        """
        self.banner("MULTIMEDIA CODECS")

        if self.confirm("Install multimedia codecs?"):
            print(f"{Color.CYAN}Pre-accepting license agreements...{Color.END}")

            # Pipe the EULA acceptance into debconf-set-selections safely
            if not self.config.dry_run:
                try:
                    eula_value = (
                        "ttf-mscorefonts-installer "
                        "msttcorefonts/accepted-mscorefonts-eula select true"
                    )
                    result = subprocess.run(
                        ["debconf-set-selections"],
                        input=eula_value,
                        capture_output=True, text=True,
                        timeout=TIMEOUT_QUICK
                    )
                    if result.returncode == 0:
                        logging.info("Pre-accepted Microsoft fonts EULA")
                    else:
                        logging.warning(f"debconf-set-selections returned {result.returncode}")
                except (FileNotFoundError, subprocess.TimeoutExpired) as e:
                    logging.warning(f"Could not pre-accept EULA: {e}")
            else:
                print(f"{Color.YELLOW}[DRY RUN] Would pre-accept Microsoft fonts EULA{Color.END}")

            # is already set in run_command's default env)
            codecs_pkg = self._resolve_package_name("ubuntu-restricted-extras")
            if codecs_pkg:
                self.run_command(
                    ["apt-get", "install", "-y", codecs_pkg],
                    "Installing restricted extras (codecs)",
                    check=False,
                    timeout=TIMEOUT_INSTALL
                )

    # ═══════════════════════════════════════════════════════════════════════════
    # FLATPAK SETUP — DEDUPLICATED
    # ═══════════════════════════════════════════════════════════════════════════

    def ensure_flatpak_ready(self) -> bool:
        """
        Ensure Flatpak is installed and Flathub remote is configured.


        'flatpak remote-add --if-not-exists flathub' calls throughout the
        codebase. Checks once per session and caches the result.

        Returns:
            True if Flatpak is ready for installs, False otherwise
        """
        # Cache check: only verify once per session
        if hasattr(self, '_flatpak_ready'):
            return self._flatpak_ready

        self._flatpak_ready = False

        # Ensure flatpak is installed
        if not shutil.which('flatpak'):
            print(f"{Color.CYAN}Installing Flatpak...{Color.END}")
            success, _, _ = self.run_command(
                ["apt-get", "install", "-y", "flatpak"],
                "Installing Flatpak",
                check=False
            )
            if not success:
                print(f"{Color.YELLOW}⚠ Could not install Flatpak{Color.END}")
                return False

        # Ensure Flathub remote is configured
        success, _, _ = self.run_command(
            ["flatpak", "remote-add", "--if-not-exists", "flathub",
             "https://dl.flathub.org/repo/flathub.flatpakrepo"],
            "Configuring Flathub repository",
            check=False
        )

        if success:
            self._flatpak_ready = True
            logging.info("Flatpak ready: Flathub configured")
        else:
            logging.warning("Flatpak: could not configure Flathub remote")

        return self._flatpak_ready

    # ═══════════════════════════════════════════════════════════════════════════
    # GAMING PLATFORMS
    # ═══════════════════════════════════════════════════════════════════════════

    def install_gaming_platforms(self):
        """Install Steam, Lutris, Heroic, ProtonUp-Qt - """
        self.current_phase = InstallationPhase.PLATFORMS

        # Steam - with smart prompts
        steam_pkg = self._resolve_package_name("steam-installer")
        if steam_pkg:
            should_install = self.config.install_steam or \
                            self.prompt_install_or_update("Steam", package_name=steam_pkg)
            if should_install:
                self.banner("STEAM INSTALLATION")
                self.run_command(
                    ["apt-get", "install", "-y", steam_pkg],
                    "Installing Steam"
                )

        # Lutris via Flatpak -
        should_install = self.config.install_lutris or \
                        self.prompt_install_or_update("Lutris", flatpak_id="net.lutris.Lutris")
        if should_install:
            self.banner("LUTRIS INSTALLATION")
            if not self.ensure_flatpak_ready():
                return
            self.run_command(
                ["flatpak", "install", "-y", "flathub", "net.lutris.Lutris"],
                "Installing Lutris"
            )

        # Heroic Games Launcher -
        should_install = self.config.install_heroic or \
                        self.prompt_install_or_update("Heroic Games Launcher",
                                                     flatpak_id="com.heroicgameslauncher.hgl")
        if should_install:
            self.banner("HEROIC GAMES LAUNCHER")
            if not self.ensure_flatpak_ready():
                return
            self.run_command(
                ["flatpak", "install", "-y", "flathub", "com.heroicgameslauncher.hgl"],
                "Installing Heroic Games Launcher"
            )

        # ProtonUp-Qt -
        should_install = self.config.install_protonup or \
                        self.prompt_install_or_update("ProtonUp-Qt",
                                                     flatpak_id="net.davidotek.pupgui2")
        if should_install:
            self.banner("PROTONUP-QT INSTALLATION")
            if not self.ensure_flatpak_ready():
                return
            self.run_command(
                ["flatpak", "install", "-y", "flathub", "net.davidotek.pupgui2"],
                "Installing ProtonUp-Qt"
            )

    # ═══════════════════════════════════════════════════════════════════════════
    # WINE & PROTON — DYNAMIC CODENAME
    # ═══════════════════════════════════════════════════════════════════════════

    def install_wine_proton(self):
        """
        Install Wine, Winetricks, and related compatibility layers.

        Dynamic WineHQ codename resolution.
        Handles Wine, Winetricks, DXVK, VKD3D, and GE-Proton installation.
        """
        self.current_phase = InstallationPhase.COMPATIBILITY

        # Wine - with dynamic codename
        should_install = self.config.install_wine or \
                        self.prompt_install_or_update("Wine Staging", package_name="winehq-staging")
        if should_install:
            self._install_wine_dynamic()

        # Winetricks -
        should_install = self.config.install_winetricks or \
                        self.prompt_install_or_update("Winetricks", package_name="winetricks")
        if should_install:
            self.banner("WINETRICKS INSTALLATION")
            self.run_command(
                ["apt-get", "install", "-y", "winetricks"],
                "Installing Winetricks"
            )

        # GE-Proton -
        if self.config.install_ge_proton or self.confirm("Install GE-Proton (enhanced Proton)?"):
            self._install_ge_proton()

    def _install_wine_dynamic(self):
        """
        Install Wine with dynamically resolved repository codename.


        """
        self.banner("WINE INSTALLATION")

        wine_codename = self.get_wine_codename()
        if not wine_codename:
            print(f"{Color.RED}✗ Could not determine WineHQ repository codename{Color.END}")
            print(f"{Color.CYAN}  Falling back to system packages: apt-get install wine wine64{Color.END}")
            self.run_command(
                ["apt-get", "install", "-y", "wine", "wine64"],
                "Installing Wine from distribution repositories",
                check=False
            )
            return

        repo_base = self.get_wine_repo_base_url()

        print(f"{Color.CYAN}  Detected codename: {wine_codename}{Color.END}")
        print(f"{Color.CYAN}  Repository: {repo_base}{Color.END}")
        logging.info(f"Wine install: codename='{wine_codename}', repo='{repo_base}'")

        sources_url = f"{repo_base}/dists/{wine_codename}/winehq-{wine_codename}.sources"

        # Verify repo URL is accessible
        print(f"{Color.CYAN}  Verifying WineHQ repository availability...{Color.END}")
        repo_accessible = False
        try:
            req = urllib.request.Request(sources_url, method='HEAD')
            with urllib.request.urlopen(req, timeout=TIMEOUT_NETWORK) as response:
                repo_accessible = response.status == 200
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            logging.warning(f"Wine repo check failed for '{sources_url}': {e}")

        if not repo_accessible:
            print(f"{Color.YELLOW}⚠ WineHQ repository not available for '{wine_codename}'{Color.END}")
            print(f"{Color.CYAN}  Falling back to distribution packages...{Color.END}")
            self.run_command(
                ["apt-get", "install", "-y", "wine", "wine64"],
                "Installing Wine from distribution repositories",
                check=False
            )
            return

        commands = [
            (["mkdir", "-pm755", "/etc/apt/keyrings"],
             "Creating keyring directory"),
            (["wget", "-O", "/etc/apt/keyrings/winehq-archive.key",
              "https://dl.winehq.org/wine-builds/winehq.key"],
             "Downloading WineHQ signing key"),
            (["wget", "-NP", "/etc/apt/sources.list.d/", sources_url],
             f"Adding WineHQ repository ({wine_codename})"),
            (["apt-get", "update"],
             "Updating package lists"),
            (["apt-get", "install", "-y", "--install-recommends", "winehq-staging"],
             "Installing Wine Staging"),
        ]

        for cmd, desc in commands:
            success, _, _ = self.run_command(cmd, desc, check=False)
            if not success and 'install' in desc.lower() and 'wine' in desc.lower():
                print(f"{Color.YELLOW}⚠ Wine Staging not available, trying Stable...{Color.END}")
                self.run_command(
                    ["apt-get", "install", "-y", "--install-recommends", "winehq-stable"],
                    "Installing Wine Stable (fallback)",
                    check=False
                )

        sources_filename = sources_url.rsplit('/', 1)[-1] if '/' in sources_url else ""
        repo_files = ["/etc/apt/keyrings/winehq-archive.key"]
        if sources_filename:
            repo_files.append(f"/etc/apt/sources.list.d/{sources_filename}")
        self._record_repo_add(
            f"WineHQ ({wine_codename})", repo_files,
            f"WineHQ repository added for {wine_codename}"
        )

    def _install_ge_proton(self):
        """
        Install GE-Proton from GitHub with SHA512 checksum verification.

        Pre-install detection scans compatibilitytools.d for existing versions.
        Downloads and verifies sha512sum.
        Records rollback action.
        Downloads latest release, verifies SHA512 checksum, and extracts.
        """
        self.banner("GE-PROTON INSTALLATION")

        # --- Pre-install detection: check for existing GE-Proton versions ---
        compat_dir = REAL_USER_HOME / ".steam" / "root" / "compatibilitytools.d"
        existing_versions = []
        if compat_dir.exists():
            existing_versions = sorted(
                [d.name for d in compat_dir.iterdir()
                 if d.is_dir() and 'GE-Proton' in d.name],
                reverse=True
            )
        if existing_versions:
            print(f"{Color.GREEN}✓ GE-Proton already installed:{Color.END}")
            for ver in existing_versions[:5]:
                print(f"  • {ver}")
            if len(existing_versions) > 5:
                print(f"  ... and {len(existing_versions) - 5} more")

        print(f"{Color.CYAN}Fetching latest GE-Proton release...{Color.END}")

        try:
            api_url = "https://api.github.com/repos/GloriousEggroll/proton-ge-custom/releases/latest"
            req = urllib.request.Request(api_url)
            req.add_header('User-Agent', 'debian-gaming-setup')

            with urllib.request.urlopen(req, timeout=TIMEOUT_API) as response:
                data = json.loads(response.read())

            tag_name = data.get('tag_name', '')
            print(f"{Color.CYAN}Latest GE-Proton: {tag_name}{Color.END}")

            # Compare with installed versions — skip if already up to date
            if existing_versions and tag_name and tag_name in existing_versions:
                print(f"{Color.GREEN}✓ {tag_name} is already installed{Color.END}")
                if not self.confirm("Download and reinstall anyway?"):
                    return

            # Find tar.gz and sha512sum assets
            download_url = None
            checksum_url = None
            tarball_name = None

            for asset in data.get('assets', []):
                name = asset.get('name', '')
                url = asset.get('browser_download_url', '')
                if name.endswith('.tar.gz') and 'GE-Proton' in name:
                    download_url = url
                    tarball_name = name
                elif name.endswith('.sha512sum') and 'GE-Proton' in name:
                    checksum_url = url

            if not download_url:
                print(f"{Color.YELLOW}⚠ Could not find GE-Proton download{Color.END}")
                return

            # Download and extract
            compat_dir = REAL_USER_HOME / ".steam" / "root" / "compatibilitytools.d"
            compat_dir.mkdir(parents=True, exist_ok=True)

            download_path = f"/tmp/{tag_name}.tar.gz"

            self.run_command(
                ["wget", "-O", download_path, download_url],
                f"Downloading {tag_name}"
            )

            if checksum_url:
                print(f"{Color.CYAN}  Verifying SHA512 checksum...{Color.END}")
                checksum_verified = self._verify_ge_proton_checksum(
                    download_path, checksum_url, tarball_name
                )
                if not checksum_verified:
                    print(f"{Color.RED}✗ Checksum verification FAILED!{Color.END}")
                    print(f"{Color.YELLOW}  The download may be corrupt or tampered.{Color.END}")
                    if not self.confirm("Install anyway? (NOT recommended)"):
                        if os.path.exists(download_path):
                            os.remove(download_path)
                        return
                else:
                    print(f"{Color.GREEN}  ✓ Checksum verified{Color.END}")
            else:
                print(f"{Color.YELLOW}  ⚠ No checksum file found, skipping verification{Color.END}")
                logging.warning(f"GE-Proton: No .sha512sum asset for {tag_name}")

            self.run_command(
                ["tar", "-xzf", download_path, "-C", str(compat_dir)],
                f"Extracting {tag_name}"
            )

            # Set proper ownership -
            uid, gid = get_real_user_uid_gid()
            if not self.config.dry_run:
                for root, dirs, files in os.walk(str(compat_dir)):
                    os.chown(root, uid, gid)
                    for d in dirs:
                        os.chown(os.path.join(root, d), uid, gid)
                    for f_item in files:
                        os.chown(os.path.join(root, f_item), uid, gid)

            # Determine the extracted directory name (typically matches tag)
            extracted_dir = str(compat_dir / tag_name)
            self.record_action(
                action_type=ActionType.GE_PROTON_INSTALL,
                description=f"GE-Proton {tag_name} installed",
                files=[extracted_dir],
                reversal_commands=[["rm", "-rf", extracted_dir]],
                metadata={"tag_name": tag_name, "download_url": download_url},
            )

            # Cleanup download
            if os.path.exists(download_path):
                os.remove(download_path)

            print(f"{Color.GREEN}✓ {tag_name} installed to {compat_dir}{Color.END}")

        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            logging.error(f"GE-Proton installation failed: {e}")
            print(f"{Color.YELLOW}⚠ GE-Proton installation failed: {e}{Color.END}")
            print(f"{Color.CYAN}  Manual: https://github.com/GloriousEggroll/proton-ge-custom{Color.END}")
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logging.error(f"GE-Proton installation failed (unexpected): {e}")
            print(f"{Color.YELLOW}⚠ GE-Proton installation failed: {e}{Color.END}")
            print(f"{Color.CYAN}  Manual: https://github.com/GloriousEggroll/proton-ge-custom{Color.END}")

    def _verify_ge_proton_checksum(self, local_file: str, checksum_url: str,
                                    expected_filename: str) -> bool:
        """
        Verify GE-Proton download against the SHA512 checksum from GitHub.


        release assets, extracts the expected hash, and compares it against
        the locally computed hash of the downloaded tarball.

        Args:
            local_file: Path to the downloaded tar.gz file
            checksum_url: URL of the .sha512sum asset
            expected_filename: The tarball filename to match in checksum file

        Returns:
            True if checksum matches, False otherwise
        """
        try:
            # Download the checksum file
            req = urllib.request.Request(checksum_url)
            req.add_header('User-Agent', 'debian-gaming-setup')

            with urllib.request.urlopen(req, timeout=TIMEOUT_API) as response:
                checksum_content = response.read().decode('utf-8').strip()

            # Parse checksum file (format: "hash  filename" or "hash *filename")
            expected_hash = None
            for line in checksum_content.split('\n'):
                line = line.strip()
                if not line:
                    continue
                parts = line.split(None, 1)
                if len(parts) == 2:
                    file_hash, file_name = parts
                    # Strip leading * from binary mode indicator
                    file_name = file_name.lstrip('*').strip()
                    if expected_filename in file_name or file_name in expected_filename:
                        expected_hash = file_hash.lower()
                        break

            if not expected_hash:
                # Try using the first line if only one hash is present
                first_parts = checksum_content.split(None, 1)
                if first_parts and len(first_parts[0]) == 128:  # SHA512 is 128 hex chars
                    expected_hash = first_parts[0].lower()
                else:
                    logging.warning(f"GE-Proton checksum: could not parse hash from file")
                    return False

            # Compute local SHA512
            sha512 = hashlib.sha512()
            with open(local_file, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    sha512.update(chunk)
            local_hash = sha512.hexdigest().lower()

            if local_hash == expected_hash:
                logging.info(f"GE-Proton checksum verified: {local_hash[:16]}...")
                return True
            else:
                logging.error(
                    f"GE-Proton checksum MISMATCH: "
                    f"expected={expected_hash[:16]}... "
                    f"actual={local_hash[:16]}..."
                )
                return False

        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            logging.warning(f"GE-Proton checksum verification failed: {e}")
            return False

    # ═══════════════════════════════════════════════════════════════════════════
    # SOBER, WAYDROID, COMMUNICATION TOOLS
    # ═══════════════════════════════════════════════════════════════════════════

    def install_sober(self):
        """Install Sober (Roblox on Linux) - """
        should_install = self.config.install_sober or \
                        self.prompt_install_or_update("Sober (Roblox on Linux)",
                                                     flatpak_id="org.vinegarhq.Sober")
        if should_install:
            self.banner("SOBER INSTALLATION")
            if not self.ensure_flatpak_ready():
                return
            success, _, _ = self.run_command(
                ["flatpak", "install", "-y", "flathub", "org.vinegarhq.Sober"],
                "Installing Sober", check=False
            )
            if success:
                print(f"{Color.GREEN}✓ Sober installed{Color.END}")
                print(f"{Color.CYAN}  Launch: flatpak run org.vinegarhq.Sober{Color.END}")
            else:
                print(f"{Color.YELLOW}⚠ Installation failed. See: https://sober.vinegarhq.org/{Color.END}")

    def install_waydroid(self):
        """
        Install Waydroid with dynamically resolved codename.

        Dynamic codename resolution.
        Includes Wayland session check and post-install configuration guidance.
        """
        should_install = self.config.install_waydroid or \
                        self.prompt_install_or_update("Waydroid (Android container)",
                                                     package_name="waydroid")
        if not should_install:
            return

        self.banner("WAYDROID INSTALLATION")

        print(f"{Color.YELLOW}⚠ Waydroid requires Wayland session and specific kernel modules{Color.END}")

        if not self.confirm("Continue with Waydroid installation?"):
            return

        wayland_session = os.environ.get('XDG_SESSION_TYPE', '').lower() == 'wayland'
        if not wayland_session:
            print(f"{Color.YELLOW}⚠ Waydroid works best on Wayland sessions{Color.END}")
            print(f"{Color.CYAN}  Current session: {os.environ.get('XDG_SESSION_TYPE', 'unknown')}{Color.END}")
            if not self.confirm("Install anyway?"):
                return

        # Dynamic codename resolution for Waydroid compatibility
        codename = self.get_waydroid_codename()
        if codename:
            print(f"{Color.CYAN}  System codename: {codename}{Color.END}")
        logging.info(f"Waydroid install: resolved codename = '{codename}'")

        # Download the Waydroid repo setup script first, then execute it
        waydroid_script = "/tmp/waydroid_repo_setup.sh"

        # Step 1: Download the script
        success, _, _ = self.run_command(
            ["wget", "-O", waydroid_script, "https://repo.waydro.id"],
            "Downloading Waydroid repository setup script",
            check=False,
            timeout=TIMEOUT_DOWNLOAD
        )

        if not success:
            print(f"{Color.YELLOW}⚠ Could not download Waydroid setup script{Color.END}")
            print(f"{Color.CYAN}  See: https://docs.waydro.id/usage/install-on-desktops{Color.END}")
            return

        # Step 2: Basic validation — ensure it's a shell script, not binary/HTML
        try:
            with open(waydroid_script, 'r') as f:
                first_line = f.readline().strip()
                script_content = f.read()

            if not first_line.startswith('#!') or 'html' in first_line.lower():
                print(f"{Color.RED}✗ Downloaded file is not a valid shell script{Color.END}")
                logging.error(f"Waydroid script validation failed: first line = '{first_line}'")
                os.remove(waydroid_script)
                return

            logging.info(f"Waydroid script validated: {len(script_content)} bytes, shebang: {first_line}")
        except (IOError, UnicodeDecodeError) as e:
            print(f"{Color.YELLOW}⚠ Could not validate downloaded script: {e}{Color.END}")
            if os.path.exists(waydroid_script):
                os.remove(waydroid_script)
            return

        # Step 3: Execute the downloaded script
        os.chmod(waydroid_script, 0o755)
        success, _, _ = self.run_command(
            ["bash", waydroid_script],
            "Adding Waydroid repository",
            check=False
        )

        # Cleanup the temp script
        if os.path.exists(waydroid_script):
            os.remove(waydroid_script)

        if not success:
            print(f"{Color.YELLOW}⚠ Waydroid repository setup failed{Color.END}")
            print(f"{Color.CYAN}  See: https://docs.waydro.id/usage/install-on-desktops{Color.END}")
            return

        # Step 4: Install Waydroid
        self.run_command(["apt-get", "update"], "Updating package lists", check=False)

        success, _, _ = self.run_command(
            ["apt-get", "install", "-y", "waydroid"],
            "Installing Waydroid",
            check=False
        )

        if not success:
            print(f"{Color.YELLOW}⚠ Waydroid installation failed{Color.END}")
            print(f"{Color.CYAN}  See: https://docs.waydro.id/usage/install-on-desktops{Color.END}")
            return

        print(f"{Color.GREEN}✓ Waydroid installed{Color.END}")
        print(f"{Color.YELLOW}Next steps:{Color.END}")
        print(f"  1. sudo waydroid init")
        print(f"  2. waydroid session start")
        print(f"  3. waydroid show-full-ui")

    def install_discord(self):
        """Install Discord - """
        should_install = self.config.install_discord or \
                        self.prompt_install_or_update("Discord", flatpak_id="com.discordapp.Discord")
        if should_install:
            self.banner("DISCORD INSTALLATION")
            if not self.ensure_flatpak_ready():
                return
            self.run_command(
                ["flatpak", "install", "-y", "flathub", "com.discordapp.Discord"],
                "Installing Discord"
            )

    def install_obs(self):
        """Install OBS Studio - """
        should_install = self.config.install_obs or \
                        self.prompt_install_or_update("OBS Studio", package_name="obs-studio")
        if should_install:
            self.banner("OBS STUDIO INSTALLATION")
            commands = [
                (["add-apt-repository", "ppa:obsproject/obs-studio", "-y"], "Adding OBS PPA"),
                (["apt-get", "update"], "Updating package lists"),
                (["apt-get", "install", "-y", "obs-studio"], "Installing OBS Studio")
            ]
            for cmd, desc in commands:
                self.run_command(cmd, desc)

    def install_mumble(self):
        """Install Mumble voice chat with pre-install detection."""
        # --- Pre-install detection ---
        if self.is_package_installed("mumble"):
            version = self.get_package_version("mumble")
            print(f"{Color.GREEN}✓ Mumble already installed "
                  f"(v{version}){Color.END}")
            if not (self.config.install_mumble or
                    self.confirm("Reinstall Mumble?")):
                return
        else:
            if not (self.config.install_mumble or
                    self.confirm("Install Mumble (voice chat)?")):
                return
        self.run_command(["apt-get", "install", "-y", "mumble"], "Installing Mumble")

    # ═══════════════════════════════════════════════════════════════════════════
    # PERFORMANCE TOOLS AND UTILITIES
    # ═══════════════════════════════════════════════════════════════════════════

    def install_mangohud(self):
        """Install MangoHud performance overlay with version-aware logic."""
        # --- Pre-install detection ---
        mangohud_installed = False
        mangohud_version = None

        if self.is_package_installed("mangohud"):
            mangohud_installed = True
            mangohud_version = self.get_package_version("mangohud")
        elif shutil.which("mangohud"):
            mangohud_installed = True

        if mangohud_installed:
            if mangohud_version:
                print(f"{Color.GREEN}✓ MangoHud already installed "
                      f"(v{mangohud_version}){Color.END}")
            else:
                print(f"{Color.GREEN}✓ MangoHud already installed{Color.END}")
            if not (self.config.install_mangohud or
                    self.confirm("Reinstall MangoHud?")):
                return
        else:
            if not (self.config.install_mangohud or
                    self.confirm("Install MangoHud (performance overlay)?")):
                return

        self.banner("MANGOHUD INSTALLATION")

        packages = ["mangohud", "mangohud:i386"]
        success, stdout, stderr = self.run_command(
            ["apt-get", "install", "-y"] + packages,
            "Installing MangoHud from default repos",
            check=False
        )

        if success:
            print(f"{Color.GREEN}✓ MangoHud installed{Color.END}")
            self.run_command(
                ["apt-get", "install", "-y", "goverlay"],
                "Installing Goverlay (optional)", check=False
            )
            return

        print(f"{Color.YELLOW}MangoHud not in default repos{Color.END}")

        # Check Ubuntu version before trying PPA
        try:
            version_check = self.system_info.distro_version
            major_version = float(version_check.split('.')[0] + '.' + version_check.split('.')[1])

            if major_version >= 24.04:
                print(f"{Color.YELLOW}⚠ MangoHud PPA not available for Ubuntu 24.04+{Color.END}")
                self.run_command(["apt-get", "update"], "Refreshing package lists")
                success, _, _ = self.run_command(
                    ["apt-get", "install", "-y"] + packages,
                    "Installing MangoHud after update", check=False
                )
                if not success:
                    print(f"{Color.CYAN}  Manual: https://github.com/flightlessmango/MangoHud{Color.END}")
                return
        except (ValueError, IndexError):
            pass

        # For Ubuntu < 24.04, try PPA
        ppa_success, _, _ = self.run_command(
            ["add-apt-repository", "ppa:flexiondotorg/mangohud", "-y"],
            "Adding MangoHud PPA", check=False
        )

        if ppa_success:
            self.run_command(["apt-get", "update"], "Updating package lists", check=False)
            self.run_command(
                ["apt-get", "install", "-y"] + packages,
                "Installing MangoHud from PPA", check=False
            )
        else:
            print(f"{Color.CYAN}  Manual: https://github.com/flightlessmango/MangoHud{Color.END}")

    def install_goverlay(self):
        """Install Goverlay (MangoHud GUI) with pre-install detection."""
        # --- Pre-install detection ---
        if self.is_package_installed("goverlay"):
            version = self.get_package_version("goverlay")
            print(f"{Color.GREEN}✓ Goverlay already installed "
                  f"(v{version}){Color.END}")
            if not (self.config.install_goverlay or
                    self.confirm("Reinstall Goverlay?")):
                return
        elif self.is_flatpak_installed("io.github.benjamimgois.goverlay"):
            print(f"{Color.GREEN}✓ Goverlay already installed (Flatpak){Color.END}")
            if not (self.config.install_goverlay or
                    self.confirm("Reinstall Goverlay?")):
                return
        else:
            if not (self.config.install_goverlay or
                    self.confirm("Install Goverlay (MangoHud GUI)?")):
                return
        self.run_command(["apt-get", "install", "-y", "goverlay"], "Installing Goverlay", check=False)

    def install_greenwithenv(self):
        """Install GreenWithEnvy (NVIDIA GPU control) - """
        should_install = self.config.install_greenwithenv or \
                        self.prompt_install_or_update("GreenWithEnvy (NVIDIA GPU control)",
                                                     flatpak_id="com.leinardi.gwe")
        if not should_install:
            return

        if self.hardware_info.gpu_vendor != GPUVendor.NVIDIA:
            print(f"{Color.YELLOW}⚠ GreenWithEnvy is designed for NVIDIA GPUs{Color.END}")
            if not self.confirm("Install anyway?"):
                return

        self.banner("GREENWITHENV INSTALLATION")

        if not self.ensure_flatpak_ready():
            return

        success, _, _ = self.run_command(
            ["flatpak", "install", "-y", "flathub", "com.leinardi.gwe"],
            "Installing GreenWithEnvy", check=False
        )

        if success:
            print(f"{Color.GREEN}✓ GreenWithEnvy installed{Color.END}")
            print(f"{Color.CYAN}  Launch: flatpak run com.leinardi.gwe{Color.END}")
        else:
            print(f"{Color.CYAN}  Manual: https://gitlab.com/leinardi/gwe{Color.END}")

    def install_vkbasalt(self):
        """Install vkBasalt (Vulkan post-processing) with pre-install detection."""
        # --- Pre-install detection ---
        vkbasalt_installed = False
        vkbasalt_version = None

        if self.is_package_installed("vkbasalt"):
            vkbasalt_installed = True
            vkbasalt_version = self.get_package_version("vkbasalt")
        elif Path("/usr/share/vulkan/implicit_layer.d/vkBasalt.json").exists():
            vkbasalt_installed = True

        if vkbasalt_installed:
            if vkbasalt_version:
                print(f"{Color.GREEN}✓ vkBasalt already installed "
                      f"(v{vkbasalt_version}){Color.END}")
            else:
                print(f"{Color.GREEN}✓ vkBasalt already installed{Color.END}")
            should_reinstall = self.config.install_vkbasalt or \
                              self.confirm("Reinstall vkBasalt?")
            if not should_reinstall:
                return
        else:
            should_install = self.config.install_vkbasalt or \
                            self.confirm("Install vkBasalt (Vulkan post-processing)?")
            if not should_install:
                return

        self.banner("VKBASALT INSTALLATION")

        success, _, _ = self.run_command(
            ["apt-get", "install", "-y", "vkbasalt"],
            "Installing vkBasalt", check=False
        )

        if not success:
            print(f"{Color.YELLOW}⚠ vkBasalt not in repos{Color.END}")
            print(f"{Color.CYAN}  Manual: https://github.com/DadSchoorse/vkBasalt{Color.END}")
            return

        # Create default config
        config_dir = REAL_USER_HOME / ".config" / "vkBasalt"
        config_file = config_dir / "vkBasalt.conf"

        if not config_file.exists():
            config_dir.mkdir(parents=True, exist_ok=True)

            default_config = """# vkBasalt Configuration
# Toggle effects in-game: Home key
toggleKey = Home

# Effects (uncomment to enable)
effects = cas
#effects = cas:fxaa
#effects = cas:smaa:lut

# CAS (Contrast Adaptive Sharpening) settings
casSharpness = 0.4

# FXAA settings
#fxaaQualitySubpix = 0.75
#fxaaQualityEdgeThreshold = 0.125

# SMAA settings
#smaaEdgeDetection = luma
#smaaThreshold = 0.05
"""
            if not self.config.dry_run:
                with open(config_file, 'w') as f:
                    f.write(default_config)

                uid, gid = get_real_user_uid_gid()
                os.chown(config_dir, uid, gid)
                os.chown(config_file, uid, gid)

                print(f"{Color.GREEN}✓ Configuration created: {config_file}{Color.END}")
                self._record_file_create(
                    str(config_file), "vkBasalt configuration file created"
                )

        print(f"\n{Color.BOLD}vkBasalt Usage:{Color.END}")
        print(f"  ENABLE_VKBASALT=1 %command%  (in Steam launch options)")
        print(f"  Toggle in-game: Press Home key")

    def show_reshade_info(self):
        """Show ReShade setup information - """
        if not (self.config.install_reshade_setup or self.confirm("Show ReShade setup information?")):
            return

        self.banner("RESHADE ON LINUX")

        print(f"{Color.BOLD}ReShade on Linux{Color.END}\n")
        print(f"{Color.CYAN}ReShade is a Windows tool, but you can achieve similar effects on Linux:{Color.END}\n")
        print(f"{Color.BOLD}1. vkBasalt (Recommended){Color.END}")
        print(f"   Native Linux Vulkan layer with CAS, FXAA, SMAA\n")
        print(f"{Color.BOLD}2. ReShade via Wine/Proton{Color.END}")
        print(f"   Copy ReShade files to game directory\n")
        print(f"{Color.BOLD}3. GShade (Community Fork){Color.END}")
        print(f"   GitHub: https://github.com/Mortalitas/GShade-Shaders\n")

        if self.confirm("Install vkBasalt now?"):
            self.install_vkbasalt()

    def install_mod_managers(self):
        """Install mod management tools with pre-install detection."""
        should_install = self.config.install_mod_managers or \
                        self.confirm("Install mod management tools?")
        if not should_install:
            return

        self.banner("MOD MANAGER INSTALLATION")

        print(f"{Color.BOLD}Available Mod Managers for Linux:{Color.END}\n")

        if self.confirm("Install Mod Organizer 2 (via Lutris)?"):
            print(f"{Color.CYAN}Mod Organizer 2 Setup:{Color.END}")
            print(f"  1. Install Lutris if not already installed")
            print(f"  2. Search Lutris for 'Mod Organizer 2'")
            print(f"  3. Follow the Lutris installation script\n")

        if self.confirm("Show Vortex Mod Manager instructions?"):
            print(f"{Color.CYAN}Vortex Mod Manager (via Proton):{Color.END}")
            print(f"  1. Download from https://www.nexusmods.com/about/vortex/")
            print(f"  2. Run through Proton/Wine\n")

        # --- r2modman pre-install detection ---
        r2modman_installed = self.is_flatpak_installed("com.thunderstore.r2modman")
        if r2modman_installed:
            version = self.get_flatpak_version("com.thunderstore.r2modman")
            if version:
                print(f"{Color.GREEN}✓ r2modman already installed "
                      f"(v{version}){Color.END}")
            else:
                print(f"{Color.GREEN}✓ r2modman already installed (Flatpak){Color.END}")
            if not self.confirm("Reinstall r2modman?"):
                return
        elif self.confirm("Install r2modman?"):
            print(f"{Color.CYAN}Installing r2modman via Flatpak...{Color.END}")
            if not self.ensure_flatpak_ready():
                return
            self.run_command(
                ["flatpak", "install", "-y", "flathub", "com.thunderstore.r2modman"],
                "Installing r2modman", check=False
            )

    # ═══════════════════════════════════════════════════════════════════════════
    # SYSTEM OPTIMIZATIONS
    # ═══════════════════════════════════════════════════════════════════════════

    def optimize_system(self):
        """Apply gaming system optimizations - """
        self.banner("SYSTEM OPTIMIZATIONS")
        self.current_phase = InstallationPhase.OPTIMIZATION

        print(f"{Color.CYAN}Applying gaming optimizations...{Color.END}")

        # Increase inotify watchers
        sysctl_settings = {
            'fs.inotify.max_user_watches': '524288',
            'vm.max_map_count': '2147483642',
        }

        sysctl_file = "/etc/sysctl.d/99-gaming.conf"
        sysctl_content = "# Gaming optimizations\n"
        for key, value in sysctl_settings.items():
            sysctl_content += f"{key}={value}\n"

        if not self.config.dry_run:
            try:
                with open(sysctl_file, 'w') as f:
                    f.write(sysctl_content)
                print(f"{Color.GREEN}✓ System tweaks written to {sysctl_file}{Color.END}")
                self.record_action(
                    action_type=ActionType.SYSCTL_WRITE,
                    description=f"Gaming sysctl config written to {sysctl_file}",
                    files=[sysctl_file],
                    reversal_commands=[
                        ["rm", "-f", sysctl_file],
                        ["sysctl", "--system"],
                    ],
                )
            except IOError as e:
                logging.error(f"Could not write sysctl config: {e}")

        self.run_command(
            ["sysctl", "--system"],
            "Applying sysctl settings",
            check=False
        )

        print(f"{Color.GREEN}✓ Gaming optimizations applied{Color.END}")

    def create_performance_script(self):
        """
        Create performance launcher script with correct multilib handling.

        Generates ~/launch-game.sh that properly wraps games with GameMode
        and MangoHud while avoiding LD_PRELOAD multilib conflicts that occur
        when 64-bit preload libraries are passed to 32-bit child processes
        (e.g., Steam's 32-bit runtime, wine32).

        Key design decisions:
        - Uses MANGOHUD=1 env var instead of 'mangohud' wrapper to avoid
          LD_PRELOAD /usr/$LIB/mangohud/libMangoHud.so path issues
        - Validates GameMode library presence before enabling gamemoderun
        - Creates default MangoHud config if missing
        - Steam-specific handling: sets launch options instead of wrapping
        """
        self.banner("PERFORMANCE LAUNCHER")

        script_path = REAL_USER_HOME / "launch-game.sh"
        mangohud_config_dir = REAL_USER_HOME / ".config" / "MangoHud"
        mangohud_config_file = mangohud_config_dir / "MangoHud.conf"

        # Create default MangoHud config if it doesn't exist
        if not mangohud_config_file.exists() and not self.config.dry_run:
            try:
                mangohud_config_dir.mkdir(parents=True, exist_ok=True)
                mangohud_default = (
                    "# MangoHud Configuration\n"
                    "# Created by Debian Gaming Setup Script\n"
                    "# See: https://github.com/flightlessmango/MangoHud\n"
                    "\n"
                    "# Display position (top-left, top-right, bottom-left, bottom-right)\n"
                    "position=top-left\n"
                    "\n"
                    "# Toggle overlay visibility\n"
                    "toggle_hud=Shift_R+F12\n"
                    "\n"
                    "# What to display\n"
                    "gpu_stats\n"
                    "gpu_temp\n"
                    "cpu_stats\n"
                    "cpu_temp\n"
                    "ram\n"
                    "fps\n"
                    "frametime=0\n"
                    "frame_timing\n"
                    "\n"
                    "# Appearance\n"
                    "background_alpha=0.4\n"
                    "font_size=20\n"
                    "round_corners=5\n"
                )
                with open(mangohud_config_file, 'w') as f:
                    f.write(mangohud_default)
                uid, gid = get_real_user_uid_gid()
                os.chown(mangohud_config_dir, uid, gid)
                os.chown(mangohud_config_file, uid, gid)
                print(f"{Color.GREEN}✓ Default MangoHud config created: {mangohud_config_file}{Color.END}")
                self._record_file_create(str(mangohud_config_file), "MangoHud config created")
            except (IOError, OSError) as e:
                logging.warning(f"Could not create MangoHud config: {e}")

        script_content = r'''#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# Gaming Performance Launcher — launch-game.sh
# Created by Debian Gaming Setup Script
#
# Usage:
#   ~/launch-game.sh <game-command> [args...]
#   ~/launch-game.sh steam
#   ~/launch-game.sh /path/to/game.exe  (via Wine/Proton)
#
# Features:
#   - CPU governor set to performance mode during gameplay
#   - GameMode integration (if installed) with multilib validation
#   - MangoHud overlay via MANGOHUD=1 env var (avoids LD_PRELOAD issues)
#   - Steam-specific handling to avoid 32-bit subprocess conflicts
# ═══════════════════════════════════════════════════════════════════

set -euo pipefail

# ── Color output ──────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

echo -e "${BOLD}=== Gaming Performance Mode ===${NC}"

# ── Validate arguments ────────────────────────────────────────────
if [ $# -eq 0 ] || [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo -e "${BOLD}Gaming Performance Launcher${NC}"
    echo -e "  Wraps game launches with CPU governor, GameMode, and MangoHud."
    echo ""
    echo -e "${YELLOW}Usage:${NC} $0 <game-command> [args...]"
    echo ""
    echo -e "${BOLD}Supported Launchers:${NC}"
    echo -e "  $0 steam              Launch Steam client"
    echo -e "  $0 lutris             Launch Lutris (auto-resolves Flatpak)"
    echo -e "  $0 heroic             Launch Heroic Games Launcher (auto-resolves Flatpak)"
    echo -e "  $0 discord            Launch Discord (auto-resolves Flatpak)"
    echo ""
    echo -e "${BOLD}Direct Game Launch:${NC}"
    echo -e "  $0 wine /path/to/game.exe      Windows game via Wine"
    echo -e "  $0 /path/to/native-game        Native Linux game"
    echo -e "  $0 gamescope -- %command%       Via Gamescope"
    echo ""
    echo -e "${BOLD}Enhancements Applied:${NC}"
    echo -e "  • CPU governor → performance (restored on exit)"
    echo -e "  • GameMode via gamemoderun (if installed + validated)"
    echo -e "  • MangoHud via MANGOHUD=1 env var (Shift+F12 to toggle)"
    echo ""
    echo -e "${BOLD}Steam Per-Game Config:${NC}"
    echo -e "  Right-click game → Properties → Launch Options:"
    echo -e "    ${CYAN}gamemoderun mangohud %command%${NC}"
    echo ""
    echo -e "See: ~/LAUNCHER_GUIDE.md for full documentation"
    exit 0
fi

GAME_CMD="$1"
shift
GAME_ARGS=("$@")
CLEANUP_TASKS=()

# ── Flatpak-aware command resolver ────────────────────────────────
# Resolves known app names to their Flatpak launch commands when the
# app was installed via Flatpak rather than native packages. Prevents
# "command not found" and URI errors (e.g., Lutris interpreting empty
# args as an invalid URI).
resolve_command() {
    local cmd="$1"
    case "$cmd" in
        lutris)
            if command -v lutris &>/dev/null; then
                echo "lutris"
            elif flatpak list --app 2>/dev/null | grep -q "net.lutris.Lutris"; then
                echo "flatpak run net.lutris.Lutris"
            else
                echo "$cmd"
            fi
            ;;
        heroic|heroic-games-launcher)
            if command -v heroic &>/dev/null; then
                echo "heroic"
            elif flatpak list --app 2>/dev/null | grep -q "com.heroicgameslauncher.hgl"; then
                echo "flatpak run com.heroicgameslauncher.hgl"
            else
                echo "$cmd"
            fi
            ;;
        discord)
            if command -v discord &>/dev/null; then
                echo "discord"
            elif flatpak list --app 2>/dev/null | grep -q "com.discordapp.Discord"; then
                echo "flatpak run com.discordapp.Discord"
            else
                echo "$cmd"
            fi
            ;;
        *)
            echo "$cmd"
            ;;
    esac
}

# Resolve the command (may expand to "flatpak run <app-id>")
RESOLVED_CMD=$(resolve_command "$GAME_CMD")
if [ "$RESOLVED_CMD" != "$GAME_CMD" ]; then
    echo -e "  ${CYAN}Resolved:${NC} $GAME_CMD → $RESOLVED_CMD"
fi

# ── Cleanup handler ───────────────────────────────────────────────
cleanup() {
    echo ""
    for task in "${CLEANUP_TASKS[@]}"; do
        eval "$task" 2>/dev/null || true
    done
    echo -e "${GREEN}Game session ended.${NC}"
}
trap cleanup EXIT

# ── CPU Governor ──────────────────────────────────────────────────
# Set to performance mode for the duration of the game session
GOVERNOR_PREV=""
if command -v cpupower &>/dev/null; then
    # Save current governor to restore later
    GOVERNOR_PREV=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null || echo "")
    if [ -n "$GOVERNOR_PREV" ]; then
        echo -e "  ${CYAN}CPU governor:${NC} $GOVERNOR_PREV → performance"
        sudo cpupower frequency-set -g performance &>/dev/null && \
            CLEANUP_TASKS+=("echo -e '  ${CYAN}CPU governor:${NC} restoring $GOVERNOR_PREV'; sudo cpupower frequency-set -g $GOVERNOR_PREV &>/dev/null")
    fi
elif [ -w "/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor" ]; then
    GOVERNOR_PREV=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null || echo "")
    if [ -n "$GOVERNOR_PREV" ] && [ "$GOVERNOR_PREV" != "performance" ]; then
        echo "performance" | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor &>/dev/null
        echo -e "  ${CYAN}CPU governor:${NC} $GOVERNOR_PREV → performance"
        CLEANUP_TASKS+=("echo '$GOVERNOR_PREV' | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor &>/dev/null")
    fi
fi

# ── GameMode ──────────────────────────────────────────────────────
# Only enable gamemoderun if:
#   1. gamemoderun binary exists
#   2. libgamemodeauto.so.0 is resolvable by the dynamic linker
# This prevents "cannot open shared object" errors for 32-bit children
USE_GAMEMODE=false
if command -v gamemoderun &>/dev/null; then
    # Verify the shared library is actually loadable
    if ldconfig -p 2>/dev/null | grep -q "libgamemodeauto.so.0"; then
        USE_GAMEMODE=true
        echo -e "  ${GREEN}GameMode:${NC} enabled (gamemoderun wrapper)"
    else
        echo -e "  ${YELLOW}GameMode:${NC} binary found but libgamemodeauto.so.0 missing from ldconfig"
        echo -e "    Try: sudo apt install libgamemode0 libgamemode0:i386"
    fi
else
    echo -e "  ${YELLOW}GameMode:${NC} not installed (optional)"
fi

# ── MangoHud ──────────────────────────────────────────────────────
# Use MANGOHUD=1 environment variable instead of the 'mangohud' wrapper.
# The 'mangohud' command sets LD_PRELOAD=/usr/$LIB/mangohud/libMangoHud.so
# which causes two problems:
#   1. $LIB doesn't expand correctly in all shell contexts
#   2. 64-bit preload path breaks 32-bit Steam/Wine child processes
# MANGOHUD=1 activates via the Vulkan implicit layer instead — no LD_PRELOAD.
USE_MANGOHUD=false
if command -v mangohud &>/dev/null || [ -f "/usr/share/vulkan/implicit_layer.d/MangoHud.x86_64.json" ]; then
    USE_MANGOHUD=true
    export MANGOHUD=1
    export MANGOHUD_DLSYM=1
    echo -e "  ${GREEN}MangoHud:${NC} enabled via MANGOHUD=1 (Shift+F12 to toggle)"

    # Check for config file
    CONFIG_FILE="${HOME}/.config/MangoHud/MangoHud.conf"
    if [ -f "$CONFIG_FILE" ]; then
        echo -e "    Config: $CONFIG_FILE"
    else
        echo -e "    ${YELLOW}No config file found at $CONFIG_FILE${NC}"
        echo -e "    Using defaults. See: https://github.com/flightlessmango/MangoHud#mangohudconf"
    fi
else
    echo -e "  ${YELLOW}MangoHud:${NC} not installed (optional)"
fi

# ── Steam-specific handling ───────────────────────────────────────
# When launching Steam directly, we avoid wrapping with gamemoderun
# because Steam launches many 32-bit child processes that break with
# 64-bit-only LD_PRELOAD. Instead, we set environment variables and
# instruct the user to use Steam's launch options for per-game config.
IS_STEAM=false
case "$(basename "$GAME_CMD")" in
    steam|steam-runtime)
        IS_STEAM=true
        echo ""
        echo -e "${BOLD}Steam Launch Notes:${NC}"
        echo -e "  MangoHud and GameMode are best configured per-game via Steam."
        echo -e "  Right-click game → Properties → Launch Options, then use:"
        if $USE_MANGOHUD && $USE_GAMEMODE; then
            echo -e "    ${CYAN}gamemoderun mangohud %command%${NC}"
        elif $USE_MANGOHUD; then
            echo -e "    ${CYAN}mangohud %command%${NC}"
        elif $USE_GAMEMODE; then
            echo -e "    ${CYAN}gamemoderun %command%${NC}"
        fi
        echo ""
        ;;
esac

# ── Launch ────────────────────────────────────────────────────────
echo -e "\n${BOLD}Launching:${NC} $RESOLVED_CMD ${GAME_ARGS[*]:-}"
echo "══════════════════════════════════════════════"

# Split RESOLVED_CMD into array for proper exec handling
# (e.g., "flatpak run net.lutris.Lutris" becomes 3 separate args)
read -ra LAUNCH_CMD <<< "$RESOLVED_CMD"

if $IS_STEAM; then
    # Launch Steam without gamemoderun wrapper to avoid multilib LD_PRELOAD
    # MANGOHUD=1 env var is already set and will be inherited
    if [ ${#GAME_ARGS[@]} -gt 0 ]; then
        exec "${LAUNCH_CMD[@]}" "${GAME_ARGS[@]}"
    else
        exec "${LAUNCH_CMD[@]}"
    fi
else
    # Non-Steam games: safe to wrap with gamemoderun since we validated the lib
    if $USE_GAMEMODE; then
        if [ ${#GAME_ARGS[@]} -gt 0 ]; then
            exec gamemoderun "${LAUNCH_CMD[@]}" "${GAME_ARGS[@]}"
        else
            exec gamemoderun "${LAUNCH_CMD[@]}"
        fi
    else
        if [ ${#GAME_ARGS[@]} -gt 0 ]; then
            exec "${LAUNCH_CMD[@]}" "${GAME_ARGS[@]}"
        else
            exec "${LAUNCH_CMD[@]}"
        fi
    fi
fi
'''

        if not self.config.dry_run:
            try:
                with open(script_path, 'w') as f:
                    f.write(script_content)
                os.chmod(script_path, 0o755)

                uid, gid = get_real_user_uid_gid()
                os.chown(script_path, uid, gid)

                print(f"{Color.GREEN}✓ Performance launcher created: {script_path}{Color.END}")
                print(f"{Color.CYAN}  Usage: ~/launch-game.sh steam{Color.END}")
                print(f"{Color.CYAN}         ~/launch-game.sh lutris{Color.END}")
                self._record_file_create(
                    str(script_path), "Performance launcher script created"
                )
            except IOError as e:
                logging.error(f"Could not create performance script: {e}")
        else:
            print(f"{Color.YELLOW}[DRY RUN] Would create: {script_path}{Color.END}")

    # ═══════════════════════════════════════════════════════════════════════════
    # INSTALLATION SUMMARY
    # ═══════════════════════════════════════════════════════════════════════════

    # ═══════════════════════════════════════════════════════════════════════════
    # POST-INSTALL HEALTH CHECK — NEW
    # ═══════════════════════════════════════════════════════════════════════════

    def post_install_health_check(self):
        """
        Verify installed components are actually working after installation.


        manifest to confirm packages are installed and key binaries exist.
        """
        self.banner("POST-INSTALL HEALTH CHECK")

        passed = 0
        failed = 0
        warnings = 0

        # Check APT packages from rollback manifest
        apt_packages = set()
        for action in self.rollback_actions:
            if action.action_type == ActionType.APT_INSTALL.value and action.success:
                apt_packages.update(action.packages)

        if apt_packages:
            print(f"{Color.BOLD}Verifying APT packages ({len(apt_packages)})...{Color.END}")
            for pkg in sorted(apt_packages):
                if self.is_package_installed(pkg):
                    passed += 1
                else:
                    print(f"  {Color.YELLOW}⚠{Color.END} {pkg}: not found after install")
                    warnings += 1
            print(f"  {Color.GREEN}✓ {passed} packages verified{Color.END}")
            if warnings:
                print(f"  {Color.YELLOW}⚠ {warnings} packages missing "
                      f"(may be virtual or renamed){Color.END}")

        # Check key binaries
        print(f"\n{Color.BOLD}Verifying key binaries...{Color.END}")
        key_binaries = {
            'steam': self.config.install_steam,
            'lutris': self.config.install_lutris,
            'wine': self.config.install_wine,
            'mangohud': self.config.install_mangohud,
            'gamemoded': self.config.install_gamemode,
        }

        for binary, was_requested in key_binaries.items():
            if not was_requested:
                continue
            if shutil.which(binary):
                print(f"  {Color.GREEN}✓{Color.END} {binary}")
                passed += 1
            else:
                print(f"  {Color.YELLOW}⚠{Color.END} {binary}: not in PATH")
                warnings += 1

        # Check Flatpak apps
        flatpak_apps = set()
        for action in self.rollback_actions:
            if action.action_type == ActionType.FLATPAK_INSTALL.value and action.success:
                flatpak_apps.update(action.packages)

        if flatpak_apps:
            print(f"\n{Color.BOLD}Verifying Flatpak apps ({len(flatpak_apps)})...{Color.END}")
            for app_id in sorted(flatpak_apps):
                if self.is_flatpak_installed(app_id):
                    print(f"  {Color.GREEN}✓{Color.END} {app_id}")
                    passed += 1
                else:
                    print(f"  {Color.RED}✗{Color.END} {app_id}: not installed")
                    failed += 1

        # Check GPU driver (if applicable)
        if self.hardware_info.gpu_vendor != GPUVendor.UNKNOWN:
            print(f"\n{Color.BOLD}Verifying GPU driver...{Color.END}")
            gpu_name = self.hardware_info.gpu_vendor.value

            if self.hardware_info.gpu_vendor == GPUVendor.NVIDIA:
                if shutil.which('nvidia-smi'):
                    success, stdout, _ = self.run_command(
                        ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"],
                        "", check=False
                    )
                    if success and stdout.strip():
                        print(f"  {Color.GREEN}✓{Color.END} NVIDIA driver: v{stdout.strip()}")
                        passed += 1
                    else:
                        print(f"  {Color.YELLOW}⚠{Color.END} NVIDIA: nvidia-smi present but no driver version")
                        warnings += 1
                else:
                    print(f"  {Color.YELLOW}⚠{Color.END} NVIDIA: nvidia-smi not found (reboot may be required)")
                    warnings += 1
            elif self.hardware_info.gpu_vendor == GPUVendor.AMD:
                # Check for AMDGPU kernel module
                success, stdout, _ = self.run_command(
                    ["lsmod"], "", check=False
                )
                if success and 'amdgpu' in stdout:
                    print(f"  {Color.GREEN}✓{Color.END} AMD: amdgpu module loaded")
                    passed += 1
                else:
                    print(f"  {Color.YELLOW}⚠{Color.END} AMD: amdgpu module not loaded (reboot may be needed)")
                    warnings += 1
            else:
                print(f"  {Color.GREEN}✓{Color.END} GPU type: {gpu_name}")
                passed += 1

        # Summary
        total = passed + failed + warnings
        print(f"\n{Color.BOLD}Health Check Summary:{Color.END}")
        print(f"  {Color.GREEN}✓ Passed:   {passed}{Color.END}")
        if warnings:
            print(f"  {Color.YELLOW}⚠ Warnings: {warnings}{Color.END}")
        if failed:
            print(f"  {Color.RED}✗ Failed:   {failed}{Color.END}")

        if failed == 0:
            print(f"\n{Color.GREEN}✓ Health check passed ({passed}/{total}){Color.END}")
        else:
            print(f"\n{Color.YELLOW}⚠ Some checks failed — review above{Color.END}")

        logging.info(
            f"Health check: {passed} passed, {warnings} warnings, {failed} failed"
        )

    def show_installation_summary(self):
        """Show installation summary - """
        self.banner("INSTALLATION SUMMARY")

        print(f"{Color.BOLD}Installed Components:{Color.END}\n")

        # GPU/VM drivers
        print(f"{Color.BOLD}Graphics Drivers:{Color.END}")

        try:
            result = subprocess.run(["nvidia-smi"], capture_output=True, text=True, timeout=TIMEOUT_QUICK)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Driver Version:' in line:
                        version = line.split('Driver Version:')[1].split()[0]
                        print(f"  ✓ NVIDIA Driver      {version}")
                        break
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        if self.is_package_installed("open-vm-tools"):
            version = self.get_package_version("open-vm-tools")
            print(f"  ✓ VMware Tools       {version if version else 'installed'}")

        if self.is_package_installed("virtualbox-guest-utils"):
            version = self.get_package_version("virtualbox-guest-utils")
            print(f"  ✓ VirtualBox Guest   {version if version else 'installed'}")

        if self.is_package_installed("mesa-vulkan-drivers"):
            version = self.get_package_version("mesa-vulkan-drivers")
            print(f"  ✓ Mesa Vulkan        {version if version else 'installed'}")

        print()

        # Gaming platforms and tools
        print(f"{Color.BOLD}Gaming Platforms:{Color.END}")

        components = {
            "Steam": "steam-installer", "GameMode": "gamemode",
            "Wine": "winehq-staging", "Winetricks": "winetricks",
            "OBS Studio": "obs-studio", "MangoHud": "mangohud",
            "Goverlay": "goverlay", "Mumble": "mumble",
            "vkBasalt": "vkbasalt", "Waydroid": "waydroid"
        }

        for name, package in components.items():
            if self.is_package_installed(package):
                version = self.get_package_version(package)
                if version and len(version) > 30:
                    version = version[:27] + "..."
                print(f"  ✓ {name:20} {version if version else 'installed'}")

        print()

        # Flatpak apps
        print(f"{Color.BOLD}Flatpak Applications:{Color.END}")

        flatpaks = {
            "Lutris": "net.lutris.Lutris",
            "Heroic Launcher": "com.heroicgameslauncher.hgl",
            "ProtonUp-Qt": "net.davidotek.pupgui2",
            "Discord": "com.discordapp.Discord",
            "Sober (Roblox)": "org.vinegarhq.Sober",
            "GreenWithEnvy": "com.leinardi.gwe"
        }

        has_flatpaks = False
        for name, app_id in flatpaks.items():
            if self.is_flatpak_installed(app_id):
                version = self.get_flatpak_version(app_id)
                if version and len(version) > 30:
                    version = version[:27] + "..."
                print(f"  ✓ {name:20} {version if version else 'installed'}")
                has_flatpaks = True

        if not has_flatpaks:
            print(f"  {Color.YELLOW}No Flatpak applications installed{Color.END}")

        print()

    # ═══════════════════════════════════════════════════════════════════════════
    # STATE MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════

    def load_installation_state(self):
        """Load previous installation state"""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, 'r') as f:
                    self.installation_state = json.load(f)
                logging.info(f"Loaded installation state: {len(self.installation_state)} entries")
            except (json.JSONDecodeError, IOError, OSError, KeyError) as e:
                logging.error(f"Could not load installation state: {e}")

    def save_installation_state(self):
        """
        Save current installation state with per-package tracking.

        Now includes a per-package inventory
        derived from rollback actions, tracking what was installed in each session.
        """
        try:
            self.installation_state['last_updated'] = datetime.now().isoformat()
            self.installation_state['distro'] = self.system_info.distro_name
            self.installation_state['version'] = self.system_info.distro_version
            self.installation_state['script_version'] = SCRIPT_VERSION
            self.installation_state['session_id'] = self._session_id

            apt_packages = []
            flatpak_apps = []
            files_created = []
            repos_added = []

            for action in self.rollback_actions:
                if not action.success:
                    continue
                if action.action_type == ActionType.APT_INSTALL.value:
                    apt_packages.extend(action.packages)
                elif action.action_type == ActionType.FLATPAK_INSTALL.value:
                    flatpak_apps.extend(action.packages)
                elif action.action_type == ActionType.FILE_CREATE.value:
                    files_created.extend(action.files)
                elif action.action_type == ActionType.REPO_ADD.value:
                    repos_added.extend(action.files)

            self.installation_state['installed_packages'] = {
                'apt': sorted(set(apt_packages)),
                'flatpak': sorted(set(flatpak_apps)),
            }
            self.installation_state['files_created'] = sorted(set(files_created))
            self.installation_state['repos_added'] = sorted(set(repos_added))
            self.installation_state['failed_operations'] = self.failed_operations
            self.installation_state['action_count'] = len(self.rollback_actions)

            if not self.config.dry_run:
                with open(STATE_FILE, 'w') as f:
                    json.dump(self.installation_state, f, indent=2)

                uid, gid = get_real_user_uid_gid()
                os.chown(STATE_FILE, uid, gid)

            logging.info(
                f"Installation state saved: {len(apt_packages)} apt packages, "
                f"{len(flatpak_apps)} flatpak apps, {len(files_created)} files"
            )
        except (IOError, OSError, TypeError) as e:
            logging.error(f"Could not save installation state: {e}")

    def perform_rollback(self):
        """
        Execute rollback of previous installation by processing actions in reverse.

        Full execution engine replacing stub.
        Loads the manifest, shows a summary, asks for confirmation, then
        processes each action's reversal commands in LIFO order.
        """
        self.banner("ROLLBACK ENGINE")

        # Load manifest (already done in __init__ for --rollback mode)
        if not self.rollback_actions:
            if not ROLLBACK_FILE.exists():
                print(f"{Color.YELLOW}No rollback manifest found{Color.END}")
                print(f"{Color.CYAN}  Nothing to rollback. Run the installer first.{Color.END}")
                return

            if not self.load_rollback_manifest():
                print(f"{Color.RED}Could not load rollback manifest{Color.END}")
                return

        if not self.rollback_actions:
            print(f"{Color.YELLOW}Rollback manifest is empty{Color.END}")
            return

        # Filter to only successful actions (no point undoing failed ones)
        reversible = [a for a in self.rollback_actions if a.success and a.reversal_commands]

        if not reversible:
            print(f"{Color.YELLOW}No reversible actions found in manifest{Color.END}")
            return

        # Display summary
        print(f"{Color.BOLD}Rollback Summary:{Color.END}\n")
        print(f"  Session:  {self._session_id}")
        print(f"  Actions:  {len(reversible)} reversible "
              f"(of {len(self.rollback_actions)} total)")
        print()

        # Group by type for readable display
        by_type = defaultdict(list)
        for action in reversible:
            by_type[action.action_type].append(action)

        type_labels = {
            ActionType.APT_INSTALL.value: "APT Packages",
            ActionType.FLATPAK_INSTALL.value: "Flatpak Applications",
            ActionType.REPO_ADD.value: "Repository Additions",
            ActionType.FILE_CREATE.value: "Created Files",
            ActionType.FILE_MODIFY.value: "Modified Files",
            ActionType.SYSCTL_WRITE.value: "System Config",
            ActionType.GE_PROTON_INSTALL.value: "GE-Proton",
        }

        for action_type, actions in by_type.items():
            label = type_labels.get(action_type, action_type)
            print(f"  {Color.CYAN}{label}:{Color.END}")
            for action in actions:
                pkg_info = ""
                if action.packages:
                    pkg_info = f" ({', '.join(action.packages[:5])})"
                    if len(action.packages) > 5:
                        pkg_info = pkg_info[:-1] + f", +{len(action.packages)-5} more)"
                print(f"    - {action.description}{pkg_info}")
            print()

        # Confirmation
        print(f"{Color.RED}{Color.BOLD}WARNING: Rollback will attempt to reverse ALL "
              f"actions listed above.{Color.END}")
        print(f"{Color.YELLOW}  This may remove packages, delete files, and revert "
              f"config changes.{Color.END}")
        print()

        if not self.confirm("Proceed with rollback?"):
            print("Rollback cancelled.")
            return

        # Offer dry-run preview
        if not self.config.auto_yes:
            if self.confirm("Show dry-run preview first (recommended)?"):
                self._rollback_dry_run(reversible)
                print()
                if not self.confirm("Proceed with actual rollback?"):
                    print("Rollback cancelled after preview.")
                    return

        # Execute rollback in reverse order (LIFO)
        print(f"\n{Color.BOLD}Executing rollback...{Color.END}\n")

        succeeded = 0
        failed = 0

        for action in reversed(reversible):
            print(f"  {Color.CYAN}Reversing: {action.description}{Color.END}")
            logging.info(f"Rollback: reversing [{action.action_type}] {action.description}")

            action_ok = True
            for reversal_cmd in action.reversal_commands:
                success, stdout, stderr = self.run_command(
                    reversal_cmd,
                    description=f"  Rollback: {' '.join(reversal_cmd[:4])}...",
                    check=False
                )
                if not success:
                    action_ok = False
                    logging.warning(
                        f"Rollback command failed: {' '.join(reversal_cmd)}: {stderr}"
                    )

            if action_ok:
                print(f"    {Color.GREEN}✓ Reversed{Color.END}")
                succeeded += 1
            else:
                print(f"    {Color.YELLOW}⚠ Partial/failed reversal{Color.END}")
                failed += 1

        # Run apt-get update once at the end if we removed any repos
        if any(a.action_type == ActionType.REPO_ADD.value for a in reversible):
            self.run_command(
                ["apt-get", "update"],
                "Updating package lists after rollback",
                check=False
            )

        # Summary
        print(f"\n{Color.BOLD}Rollback Complete:{Color.END}")
        print(f"  {Color.GREEN}✓ Succeeded: {succeeded}{Color.END}")
        if failed:
            print(f"  {Color.YELLOW}⚠ Failed: {failed}{Color.END}")
            print(f"  {Color.CYAN}Check logs for details: {LOG_FILE}{Color.END}")

        # Archive the manifest (rename, don't delete, for safety)
        if not self.config.dry_run:
            try:
                archive_path = str(ROLLBACK_FILE) + f".rolled_back_{self._session_id}"
                os.rename(str(ROLLBACK_FILE), archive_path)
                print(f"\n{Color.CYAN}Manifest archived: {archive_path}{Color.END}")
                logging.info(f"Rollback manifest archived to {archive_path}")
            except OSError as e:
                logging.warning(f"Could not archive manifest: {e}")

        print(f"\n{Color.YELLOW}Reboot recommended to apply all changes.{Color.END}")

    def _rollback_dry_run(self, actions: list):
        """
        Show what rollback would do without executing anything.


        """
        print(f"\n{Color.YELLOW}{'='*60}{Color.END}")
        print(f"{Color.YELLOW}DRY RUN — These commands would be executed:{Color.END}")
        print(f"{Color.YELLOW}{'='*60}{Color.END}\n")

        for i, action in enumerate(reversed(actions), 1):
            print(f"  {Color.BOLD}Step {i}: Reverse [{action.action_type}]{Color.END}")
            print(f"    {action.description}")
            for cmd in action.reversal_commands:
                print(f"    $ {' '.join(cmd)}")
            print()

    # ═══════════════════════════════════════════════════════════════════════════
    # FINAL STEPS
    # ═══════════════════════════════════════════════════════════════════════════

    def final_steps(self):
        """Display final instructions - """
        self.banner("SETUP COMPLETE")

        print(f"{Color.GREEN}✓ Gaming setup completed successfully!{Color.END}\n")
        print(f"{Color.BOLD}Installation performed for user: {REAL_USER}{Color.END}")
        print(f"{Color.BOLD}User home directory: {REAL_USER_HOME}{Color.END}\n")

        print(f"{Color.BOLD}IMPORTANT NEXT STEPS:{Color.END}\n")

        print(f"{Color.YELLOW}1. REBOOT YOUR SYSTEM{Color.END}")
        print("   Required for drivers and optimizations to take effect\n")

        vm_type = self.detect_virtualization()
        if vm_type:
            print(f"{Color.CYAN}VM-SPECIFIC NOTES ({vm_type}):{Color.END}")
            if 'vmware' in vm_type.lower():
                print("   • Enable 3D acceleration in VMware settings")
                print("   • Allocate at least 2GB video memory")
                print("   • Verify tools: vmware-toolbox-cmd -v")
            elif 'virtualbox' in vm_type.lower():
                print("   • Enable 3D acceleration in VirtualBox settings")
                print("   • Allocate maximum video memory (128MB+)")
                print("   • Verify additions: lsmod | grep vbox")
            print()

        print(f"{Color.YELLOW}2. VERIFY GPU/GRAPHICS{Color.END}")
        if vm_type:
            print("   Run: glxinfo | grep 'OpenGL renderer'")
        else:
            print("   - NVIDIA: Run 'nvidia-smi'")
            print("   - AMD/Intel: Run 'vulkaninfo' or 'glxinfo | grep OpenGL'")
        print()

        print(f"{Color.YELLOW}3. CONFIGURE STEAM{Color.END}")
        print("   - Settings → Steam Play → Enable Steam Play for all titles")
        print("   - Select: Proton Experimental or latest Proton version")
        print()

        print(f"{Color.YELLOW}4. INSTALL ADDITIONAL PROTON VERSIONS{Color.END}")
        print("   - Use ProtonUp-Qt to install Proton-GE\n")

        print(f"{Color.YELLOW}5. USE PERFORMANCE LAUNCHER{Color.END}")
        print(f"   ~/launch-game.sh steam\n")

        print(f"{Color.BOLD}Log file: {LOG_FILE}{Color.END}\n")

        if self.confirm("Reboot now?"):
            self.run_command(["reboot"], "Rebooting system")

    # ═══════════════════════════════════════════════════════════════════════════
    # FLOW CONTROL — CORRECTED
    # ═══════════════════════════════════════════════════════════════════════════

    def _is_interactive_mode(self) -> bool:
        """
        Determine if running in interactive mode (no CLI flags) or targeted mode.



        Interactive mode: No component-specific flags → prompt for everything.
        Targeted mode: At least one component flag → only install what was flagged.

        Returns:
            True if running in interactive mode
        """
        mode_flags = {
            'dry_run', 'yes', 'verbose', 'no_backup', 'skip_update',
            'rollback', 'cleanup'
        }

        if not hasattr(self, 'args') or not self.args:
            return True

        for key, value in vars(self.args).items():
            if key not in mode_flags and value is True:
                logging.info(f"Targeted mode: flag '--{key}' was set")
                return False

        logging.info("Interactive mode: no component flags detected, will prompt for all")
        return True

    # ═══════════════════════════════════════════════════════════════════════════
    # MAIN EXECUTION - CORRECTED FLOW CONTROL
    # ═══════════════════════════════════════════════════════════════════════════

    def run(self):
        """
        Main execution flow

        Executes all component installations in dependency-correct order
        Corrected interactive/targeted mode,
                  network connectivity check, removed 'or True' patterns
        """
        self.banner("DEBIAN GAMING SETUP")
        print(f"{Color.BOLD}Version {SCRIPT_VERSION} — Comprehensive Gaming Environment{Color.END}\n")

        if self.config.dry_run:
            print(f"{Color.YELLOW}{'='*60}{Color.END}")
            print(f"{Color.YELLOW}DRY RUN MODE - No changes will be made{Color.END}")
            print(f"{Color.YELLOW}{'='*60}{Color.END}\n")

        if not self.confirm("This will install gaming components. Continue?"):
            print("Installation cancelled.")
            sys.exit(0)

        interactive = self._is_interactive_mode()

        try:
            # Pre-flight: Network connectivity
            self.check_network_connectivity()

            # Pre-flight: System requirements
            self.check_system_requirements()

            # Core setup — Same order
            self.clean_broken_repos()
            self.update_system()
            self.enable_32bit_support()

            # System and hardware detection
            self.detect_system()
            gpu_type = self.detect_gpu()

            # GPU/VM driver installation — CORRECTED
            if gpu_type in ['vmware', 'virtualbox', 'kvm/qemu', 'vm']:
                if self.config.install_vm_tools or (
                    interactive and self.confirm(
                        f"Install {gpu_type} guest tools for better graphics?"
                    )
                ):
                    self.install_vm_tools(gpu_type)
            elif gpu_type == 'nvidia':
                if self.config.install_nvidia_drivers or (
                    interactive and self.confirm("Install NVIDIA drivers?")
                ):
                    self.install_nvidia_drivers()
            elif gpu_type == 'amd':
                if self.config.install_amd_drivers or (
                    interactive and self.confirm("Install AMD drivers?")
                ):
                    self.install_amd_drivers()
            elif gpu_type == 'intel':
                if self.config.install_intel_drivers or (
                    interactive and self.confirm("Install Intel drivers?")
                ):
                    self.install_intel_drivers()
            elif gpu_type == 'generic':
                print(f"{Color.YELLOW}Installing generic graphics support...{Color.END}")
                self.install_generic_vm_graphics()

            # Essential packages — CORRECTED
            if self.config.install_essential_packages or (
                interactive and self.confirm("Install essential gaming packages?")
            ):
                self.install_essential_packages()

            # Codecs — CORRECTED: was `or True`, now properly conditional
            if self.config.install_codecs or (
                interactive and self.confirm("Install multimedia codecs?")
            ):
                self.install_codecs()

            # Gaming platforms (use smart prompts from original)
            self.install_gaming_platforms()
            self.install_wine_proton()

            # Specialized platforms
            self.install_sober()
            self.install_waydroid()

            # Communication & streaming tools
            self.install_discord()
            self.install_obs()
            self.install_mumble()

            # Performance tools
            self.install_mangohud()
            self.install_goverlay()

            # GPU-specific utilities
            self.install_greenwithenv()

            # Visual enhancement
            self.install_vkbasalt()
            self.show_reshade_info()

            # Mod management
            self.install_mod_managers()

            # System optimizations — CORRECTED: was `or True`
            if self.config.apply_system_optimizations or (
                interactive and self.confirm("Apply gaming system optimizations?")
            ):
                self.optimize_system()

            # Performance launcher — CORRECTED: was `or True`
            if self.config.create_performance_launcher or (
                interactive and self.confirm("Create performance launcher script?")
            ):
                self.create_performance_script()

            # Post-install reporting
            self.show_installation_summary()

            self.post_install_health_check()

            # Set log file ownership
            try:
                uid, gid = get_real_user_uid_gid()
                if not self.config.dry_run:
                    os.chown(LOG_FILE, uid, gid)
            except (OSError, PermissionError) as e:
                logging.warning(f"Could not set ownership on log file: {e}")

            # Save state
            self.save_installation_state()

            # Final steps and reboot prompt
            self.final_steps()

        except KeyboardInterrupt:
            print(f"\n{Color.YELLOW}Installation interrupted by user{Color.END}")
            try:
                self.save_installation_state()
            except (IOError, OSError):
                pass  # Best-effort state save during interrupt cleanup
            sys.exit(1)
        except Exception as e:
            # This is the last-resort handler for the entire run() flow.
            # All inner try/except blocks use specific exception types.
            logging.error(f"Unexpected error: {e}", exc_info=True)
            print(f"{Color.RED}An error occurred: {e}{Color.END}")
            print(f"{Color.YELLOW}Check log file: {LOG_FILE}{Color.END}")
            try:
                self.save_installation_state()
            except (IOError, OSError):
                pass  # Best-effort state save during error cleanup
            sys.exit(1)

# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT AND MAIN FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """
    Entry point for the script

    Handles argument parsing and script initialization.
    Added --update, --self-update, --check-requirements dispatch.
    """
    args = parse_arguments()

    if hasattr(args, 'cleanup') and args.cleanup:
        print(f"{Color.CYAN}Cleaning up installation files...{Color.END}")
        sys.exit(0)

    setup = GamingSetup(args)

    if hasattr(args, 'rollback') and args.rollback:
        setup.perform_rollback()
        sys.exit(0)

    if hasattr(args, 'update') and args.update:
        setup.detect_system()
        setup.perform_update()
        sys.exit(0)

    if hasattr(args, 'self_update') and args.self_update:
        setup.check_self_update()
        sys.exit(0)

    if hasattr(args, 'check_requirements') and args.check_requirements:
        setup.detect_system()
        setup.check_system_requirements()
        sys.exit(0)

    setup.run()

if __name__ == "__main__":
    main()

# ═══════════════════════════════════════════════════════════════════════════════
# END OF debian_gaming_setup.py
# ═══════════════════════════════════════════════════════════════════════════════
