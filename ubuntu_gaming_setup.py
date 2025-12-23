#!/usr/bin/env python3
"""
Ubuntu 24.04.3 Gaming Setup Script
Automates installation and configuration of gaming components
"""

import os
import sys
import subprocess
import platform
import logging
from pathlib import Path
from datetime import datetime
import pwd

# Detect the actual user (not root)
def get_real_user():
    """Get the actual user who invoked sudo"""
    sudo_user = os.environ.get('SUDO_USER')
    if sudo_user:
        return sudo_user
    return os.environ.get('USER', 'root')

def get_real_user_home():
    """Get the home directory of the actual user"""
    real_user = get_real_user()
    try:
        return Path(pwd.getpwnam(real_user).pw_dir)
    except:
        return Path.home()

def get_real_user_uid_gid():
    """Get UID and GID of the actual user"""
    real_user = get_real_user()
    try:
        pw_record = pwd.getpwnam(real_user)
        return pw_record.pw_uid, pw_record.pw_gid
    except:
        return os.getuid(), os.getgid()

# Setup logging in user's home directory
REAL_USER = get_real_user()
REAL_USER_HOME = get_real_user_home()
LOG_DIR = REAL_USER_HOME / "gaming_setup_logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / f"gaming_setup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Set proper ownership for log directory
try:
    uid, gid = get_real_user_uid_gid()
    os.chown(LOG_DIR, uid, gid)
except:
    pass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

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

class GamingSetup:
    """Main class for Ubuntu gaming setup"""
    
    def __init__(self):
        self.check_root()
        self.check_ubuntu_version()
        
    def check_root(self):
        """Verify script is run with sudo privileges"""
        if os.geteuid() != 0:
            print(f"{Color.RED}This script must be run with sudo privileges{Color.END}")
            print(f"Usage: sudo python3 {sys.argv[0]}")
            sys.exit(1)
    
    def check_ubuntu_version(self):
        """Verify Ubuntu version"""
        try:
            with open('/etc/os-release', 'r') as f:
                os_info = f.read()
                if 'Ubuntu' not in os_info:
                    print(f"{Color.YELLOW}Warning: This script is designed for Ubuntu 24.04.3{Color.END}")
                    if not self.confirm("Continue anyway?"):
                        sys.exit(0)
        except Exception as e:
            logging.error(f"Could not verify OS version: {e}")
    
    def run_command(self, cmd, description="", check=True, shell=False, env=None):
        """Execute shell command with logging"""
        if description:
            logging.info(description)
            print(f"{Color.CYAN}>>> {description}{Color.END}")
        
        try:
            # Set default environment with DEBIAN_FRONTEND=noninteractive
            if env is None:
                env = os.environ.copy()
                env['DEBIAN_FRONTEND'] = 'noninteractive'
            
            if shell:
                result = subprocess.run(cmd, shell=True, check=check, 
                                      capture_output=True, text=True, env=env,
                                      timeout=300)  # 5 minute timeout
            else:
                result = subprocess.run(cmd, check=check, 
                                      capture_output=True, text=True, env=env,
                                      timeout=300)  # 5 minute timeout
            
            if result.stdout:
                logging.debug(result.stdout)
            if result.returncode == 0:
                logging.info(f"SUCCESS: {description}")
                return True
            else:
                logging.warning(f"Command returned non-zero: {result.returncode}")
                return False
                
        except subprocess.TimeoutExpired:
            logging.error(f"TIMEOUT: {description} (exceeded 5 minutes)")
            print(f"{Color.RED}Command timed out: {description}{Color.END}")
            return False
        except subprocess.CalledProcessError as e:
            logging.error(f"FAILED: {description}")
            logging.error(f"Error: {e.stderr}")
            if check:
                print(f"{Color.RED}Error executing: {description}{Color.END}")
                print(f"{Color.RED}{e.stderr}{Color.END}")
            return False
    
    def confirm(self, question):
        """Ask user for confirmation"""
        while True:
            response = input(f"{Color.YELLOW}{question} (y/n): {Color.END}").lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            print("Please answer 'y' or 'n'")
    
    def clean_broken_repos(self):
        """Clean up broken repository configurations"""
        print(f"{Color.YELLOW}Checking for broken repositories...{Color.END}")
        
        # Try to update, if it fails due to broken repos, try to fix
        result = self.run_command(
            ["apt-get", "update"],
            "Testing repository configuration",
            check=False
        )
        
        if not result:
            print(f"{Color.YELLOW}Found broken repositories, attempting cleanup...{Color.END}")
            
            # Common fix: remove problematic PPA list files
            ppa_dir = "/etc/apt/sources.list.d/"
            if os.path.exists(ppa_dir):
                for file in os.listdir(ppa_dir):
                    if "lutris" in file.lower():
                        file_path = os.path.join(ppa_dir, file)
                        try:
                            os.remove(file_path)
                            print(f"{Color.GREEN}Removed broken repository: {file}{Color.END}")
                        except Exception as e:
                            logging.error(f"Could not remove {file}: {e}")
            
            # Try update again
            self.run_command(
                ["apt-get", "update"],
                "Updating after repository cleanup",
                check=False
            )
    
    def is_package_installed(self, package_name):
        """Check if a package is installed"""
        try:
            result = subprocess.run(
                ["dpkg", "-l", package_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0 and 'ii' in result.stdout
        except:
            return False
    
    def get_package_version(self, package_name):
        """Get installed package version"""
        try:
            result = subprocess.run(
                ["dpkg-query", "-W", "-f=${Version}", package_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return None
    
    def get_available_version(self, package_name):
        """Get available package version from repos"""
        try:
            result = subprocess.run(
                ["apt-cache", "policy", package_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Candidate:' in line:
                        return line.split(':')[1].strip()
        except:
            pass
        return None
    
    def is_flatpak_installed(self, app_id):
        """Check if a Flatpak app is installed"""
        try:
            result = subprocess.run(
                ["flatpak", "list", "--app"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return app_id in result.stdout
        except:
            return False
    
    def get_flatpak_version(self, app_id):
        """Get installed Flatpak version"""
        try:
            result = subprocess.run(
                ["flatpak", "info", app_id],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Version:' in line:
                        return line.split(':')[1].strip()
        except:
            pass
        return None
    
    def check_updates_available(self, package_name):
        """Check if updates are available for a package"""
        installed = self.get_package_version(package_name)
        available = self.get_available_version(package_name)
        
        if installed and available and installed != available:
            return True, installed, available
        return False, installed, available
    
    def prompt_install_or_update(self, software_name, package_name=None, flatpak_id=None):
        """Smart prompt that checks installation status and offers update"""
        
        is_installed = False
        current_version = None
        available_version = None
        update_available = False
        
        # Check package installation
        if package_name:
            is_installed = self.is_package_installed(package_name)
            if is_installed:
                current_version = self.get_package_version(package_name)
                available_version = self.get_available_version(package_name)
                update_available = current_version != available_version
        
        # Check Flatpak installation
        if flatpak_id and not is_installed:
            is_installed = self.is_flatpak_installed(flatpak_id)
            if is_installed:
                current_version = self.get_flatpak_version(flatpak_id)
        
        # Build prompt based on status
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
    
    def show_installation_summary(self):
        """Show summary of installed gaming components"""
        self.banner("INSTALLATION SUMMARY")
        
        print(f"{Color.BOLD}Installed Components:{Color.END}\n")
        
        # Check GPU/VM drivers
        print(f"{Color.BOLD}Graphics Drivers:{Color.END}")
        
        # NVIDIA check
        try:
            result = subprocess.run(["nvidia-smi"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Driver Version:' in line:
                        version = line.split('Driver Version:')[1].split()[0]
                        print(f"  ✅ NVIDIA Driver      {version}")
                        break
        except:
            pass
        
        # VMware check
        if self.is_package_installed("open-vm-tools"):
            version = self.get_package_version("open-vm-tools")
            print(f"  ✅ VMware Tools       {version if version else 'installed'}")
        
        # VirtualBox check
        if self.is_package_installed("virtualbox-guest-utils"):
            version = self.get_package_version("virtualbox-guest-utils")
            print(f"  ✅ VirtualBox Guest   {version if version else 'installed'}")
        
        # Mesa check (AMD/Intel)
        if self.is_package_installed("mesa-vulkan-drivers"):
            version = self.get_package_version("mesa-vulkan-drivers")
            print(f"  ✅ Mesa Vulkan        {version if version else 'installed'}")
        
        print()
        
        # Gaming platforms
        print(f"{Color.BOLD}Gaming Platforms:{Color.END}")
        
        components = {
            "Steam": "steam-installer",
            "GameMode": "gamemode",
            "Wine": "winehq-staging",
            "Winetricks": "winetricks",
            "OBS Studio": "obs-studio"
        }
        
        for name, package in components.items():
            if self.is_package_installed(package):
                version = self.get_package_version(package)
                if version and len(version) > 30:
                    version = version[:27] + "..."
                print(f"  ✅ {name:20} {version if version else 'installed'}")
        
        print()
        
        # Flatpak apps
        print(f"{Color.BOLD}Flatpak Applications:{Color.END}")
        
        flatpaks = {
            "Lutris": "net.lutris.Lutris",
            "Heroic Launcher": "com.heroicgameslauncher.hgl",
            "ProtonUp-Qt": "net.davidotek.pupgui2",
            "Discord": "com.discordapp.Discord"
        }
        
        has_flatpaks = False
        for name, app_id in flatpaks.items():
            if self.is_flatpak_installed(app_id):
                version = self.get_flatpak_version(app_id)
                if version and len(version) > 30:
                    version = version[:27] + "..."
                print(f"  ✅ {name:20} {version if version else 'installed'}")
                has_flatpaks = True
        
        if not has_flatpaks:
            print(f"  {Color.YELLOW}No Flatpak applications installed{Color.END}")
        
        print()
    
    def banner(self, text):
        """Display section banner"""
        print(f"\n{Color.BOLD}{Color.HEADER}{'='*60}{Color.END}")
        print(f"{Color.BOLD}{Color.HEADER}{text.center(60)}{Color.END}")
        print(f"{Color.BOLD}{Color.HEADER}{'='*60}{Color.END}\n")
    
    def update_system(self):
        """Update system packages"""
        self.banner("SYSTEM UPDATE")
        
        commands = [
            (["apt-get", "update"], "Updating package lists"),
            (["apt-get", "upgrade", "-y"], "Upgrading installed packages"),
            (["apt-get", "autoremove", "-y"], "Removing unnecessary packages"),
            (["apt-get", "autoclean"], "Cleaning package cache")
        ]
        
        for cmd, desc in commands:
            self.run_command(cmd, desc)
    
    def detect_gpu(self):
        """Detect GPU type"""
        self.banner("GPU DETECTION")
        
        # First check if running in a VM
        vm_type = self.detect_virtualization()
        if vm_type:
            print(f"{Color.YELLOW}⚠ Virtual Machine Detected: {vm_type}{Color.END}")
            print(f"{Color.CYAN}Virtual GPU drivers will be handled by VM guest tools{Color.END}")
            logging.info(f"Running in {vm_type} VM")
            return vm_type.lower()
        
        try:
            # Check actual GPU hardware via lspci
            result = subprocess.run(['lspci'], capture_output=True, text=True)
            lspci_output = result.stdout.lower()
            
            # Filter lspci to only VGA/3D/Display lines to avoid false positives
            # from Intel CPUs, network cards, etc.
            gpu_lines = []
            for line in lspci_output.split('\n'):
                if any(keyword in line for keyword in ['vga', '3d', 'display']):
                    gpu_lines.append(line)
            
            gpu_info = ' '.join(gpu_lines).lower()
            
            # Also check OpenGL renderer for more accurate detection
            gl_info = ""
            try:
                gl_result = subprocess.run(['glxinfo'], capture_output=True, text=True, timeout=5)
                if gl_result.returncode == 0:
                    # Extract just the renderer line
                    for line in gl_result.stdout.split('\n'):
                        if 'OpenGL renderer' in line:
                            gl_info = line.lower()
                            break
            except:
                pass
            
            logging.info(f"GPU detection - lspci VGA: {gpu_info}")
            logging.info(f"GPU detection - GL renderer: {gl_info}")
            
            # Check for virtual/emulated GPUs first (shouldn't happen if VM detection worked)
            if any(vm_indicator in gpu_info or vm_indicator in gl_info 
                   for vm_indicator in ['vmware', 'virtualbox', 'qxl', 'virtio', 'svga3d']):
                print(f"{Color.YELLOW}⚠ Virtual GPU detected{Color.END}")
                logging.info("Virtual GPU detected in hardware scan")
                return 'generic'
            
            # Check for NVIDIA (most specific)
            if 'nvidia' in gpu_info or 'nvidia' in gl_info:
                print(f"{Color.GREEN}✓ NVIDIA GPU detected{Color.END}")
                logging.info("NVIDIA GPU detected")
                return 'nvidia'
            
            # Check for AMD/Radeon
            if any(amd_indicator in gpu_info or amd_indicator in gl_info
                   for amd_indicator in ['amd', 'radeon', 'ati']):
                print(f"{Color.GREEN}✓ AMD GPU detected{Color.END}")
                logging.info("AMD GPU detected")
                return 'amd'
            
            # Check for Intel (least specific, check last)
            # Only match if we see Intel in actual GPU context, not just "intel" mention
            if ('intel' in gpu_info and any(gpu_term in gpu_info 
                for gpu_term in ['graphics', 'hd', 'iris', 'uhd', 'arc'])):
                print(f"{Color.GREEN}✓ Intel GPU detected{Color.END}")
                logging.info("Intel GPU detected")
                return 'intel'
            
            # If we found GPU lines but couldn't identify vendor
            if gpu_lines:
                print(f"{Color.YELLOW}! Generic/Unknown GPU detected{Color.END}")
                print(f"{Color.CYAN}  GPU info: {gpu_lines[0] if gpu_lines else 'unknown'}{Color.END}")
                logging.info(f"Unknown GPU type: {gpu_lines}")
                return 'generic'
            
            # No GPU detected at all
            print(f"{Color.YELLOW}! No GPU detected{Color.END}")
            return 'unknown'
                
        except Exception as e:
            logging.error(f"GPU detection failed: {e}")
            return 'unknown'
    
    def detect_virtualization(self):
        """Detect if running in a virtual machine and which type"""
        try:
            # Method 1: systemd-detect-virt (most reliable)
            result = subprocess.run(['systemd-detect-virt'], 
                                  capture_output=True, text=True, timeout=5)
            virt_type = result.stdout.strip()
            
            if virt_type and virt_type != 'none':
                # Map common virtualization types to friendly names
                virt_map = {
                    'vmware': 'VMware',
                    'kvm': 'KVM',
                    'qemu': 'QEMU',
                    'virtualbox': 'VirtualBox',
                    'oracle': 'VirtualBox',
                    'microsoft': 'Hyper-V',
                    'xen': 'Xen',
                    'bochs': 'Bochs',
                    'parallels': 'Parallels'
                }
                return virt_map.get(virt_type.lower(), virt_type)
        except:
            pass
        
        try:
            # Method 2: Check dmesg for hypervisor
            result = subprocess.run(['dmesg'], capture_output=True, text=True, timeout=5)
            dmesg = result.stdout.lower()
            
            if 'vmware' in dmesg:
                return 'VMware'
            elif 'virtualbox' in dmesg:
                return 'VirtualBox'
            elif 'hypervisor detected' in dmesg:
                return 'VM'
        except:
            pass
        
        try:
            # Method 3: Check lspci for virtual graphics
            result = subprocess.run(['lspci'], capture_output=True, text=True, timeout=5)
            lspci = result.stdout.lower()
            
            if 'vmware' in lspci:
                return 'VMware'
            elif 'virtualbox' in lspci:
                return 'VirtualBox'
            elif 'qxl' in lspci or 'virtio' in lspci:
                return 'KVM/QEMU'
        except:
            pass
        
        return None
    
    def install_nvidia_drivers(self):
        """Install NVIDIA proprietary drivers"""
        self.banner("NVIDIA DRIVER INSTALLATION")
        
        # Check if already installed
        nvidia_installed = self.is_package_installed("nvidia-driver-550") or \
                          self.is_package_installed("nvidia-driver-545") or \
                          self.is_package_installed("nvidia-driver-535")
        
        if nvidia_installed:
            try:
                result = subprocess.run(["nvidia-smi"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    # Extract driver version from nvidia-smi output
                    for line in result.stdout.split('\n'):
                        if 'Driver Version:' in line:
                            version = line.split('Driver Version:')[1].split()[0]
                            print(f"{Color.GREEN}✓ NVIDIA drivers already installed (version: {version}){Color.END}")
                            break
                    else:
                        print(f"{Color.GREEN}✓ NVIDIA drivers already installed{Color.END}")
                    
                    if not self.confirm("Reinstall NVIDIA drivers?"):
                        return
            except:
                print(f"{Color.YELLOW}⚠ NVIDIA drivers installed but not loaded{Color.END}")
                if not self.confirm("Reinstall NVIDIA drivers?"):
                    return
        
        print("Installing NVIDIA driver (latest stable)...")
        
        commands = [
            (["apt-get", "install", "-y", "ubuntu-drivers-common"], "Installing driver manager"),
            (["ubuntu-drivers", "autoinstall"], "Installing recommended NVIDIA drivers"),
            (["apt-get", "install", "-y", "nvidia-settings", "nvidia-prime"], "Installing NVIDIA utilities")
        ]
        
        for cmd, desc in commands:
            self.run_command(cmd, desc)
        
        print(f"{Color.YELLOW}Note: System reboot required for NVIDIA drivers to take effect{Color.END}")
    
    def install_amd_drivers(self):
        """Install AMD drivers"""
        self.banner("AMD DRIVER INSTALLATION")
        
        print("AMD drivers are typically included in the Linux kernel.")
        print("Installing Mesa drivers and Vulkan support...")
        
        packages = [
            "mesa-vulkan-drivers",
            "mesa-vulkan-drivers:i386",
            "libvulkan1",
            "libvulkan1:i386",
            "vulkan-tools",
            "mesa-utils"
        ]
        
        self.run_command(
            ["apt-get", "install", "-y"] + packages,
            "Installing AMD Mesa and Vulkan drivers"
        )
    
    def install_intel_drivers(self):
        """Install Intel drivers"""
        self.banner("INTEL DRIVER INSTALLATION")
        
        print("Installing Intel graphics drivers...")
        
        packages = [
            "mesa-vulkan-drivers",
            "mesa-vulkan-drivers:i386",
            "libvulkan1",
            "libvulkan1:i386",
            "intel-media-va-driver",
            "i965-va-driver"
        ]
        
        self.run_command(
            ["apt-get", "install", "-y"] + packages,
            "Installing Intel graphics drivers"
        )
    
    def install_vm_tools(self, vm_type):
        """Install VM guest tools based on hypervisor type"""
        self.banner("VM GUEST TOOLS INSTALLATION")
        
        print(f"{Color.CYAN}Detected {vm_type} - Installing guest tools...{Color.END}")
        
        if 'vmware' in vm_type.lower():
            self.install_vmware_tools()
        elif 'virtualbox' in vm_type.lower():
            self.install_virtualbox_tools()
        elif 'kvm' in vm_type.lower() or 'qemu' in vm_type.lower():
            self.install_kvm_tools()
        else:
            print(f"{Color.YELLOW}Generic VM detected - installing basic 3D acceleration{Color.END}")
            self.install_generic_vm_graphics()
    
    def install_vmware_tools(self):
        """Install VMware guest tools"""
        print(f"{Color.CYAN}Installing VMware Tools (open-vm-tools)...{Color.END}")
        
        packages = [
            "open-vm-tools",
            "open-vm-tools-desktop",
            "mesa-utils",
            "mesa-utils-extra",
            "libgl1-mesa-dri",
            "libgl1-mesa-dri:i386"
        ]
        
        self.run_command(
            ["apt-get", "install", "-y"] + packages,
            "Installing VMware guest tools and graphics"
        )
        
        print(f"{Color.GREEN}✓ VMware Tools installed{Color.END}")
        print(f"{Color.YELLOW}Note: For better 3D performance, enable 3D acceleration in VMware settings{Color.END}")
    
    def install_virtualbox_tools(self):
        """Install VirtualBox guest additions"""
        print(f"{Color.CYAN}Installing VirtualBox Guest Additions...{Color.END}")
        
        packages = [
            "virtualbox-guest-utils",
            "virtualbox-guest-x11",
            "virtualbox-guest-dkms",
            "mesa-utils"
        ]
        
        self.run_command(
            ["apt-get", "install", "-y"] + packages,
            "Installing VirtualBox guest additions"
        )
        
        print(f"{Color.GREEN}✓ VirtualBox Guest Additions installed{Color.END}")
    
    def install_kvm_tools(self):
        """Install KVM/QEMU guest tools"""
        print(f"{Color.CYAN}Installing KVM/QEMU guest tools...{Color.END}")
        
        packages = [
            "qemu-guest-agent",
            "spice-vdagent",
            "xserver-xorg-video-qxl",
            "mesa-utils"
        ]
        
        self.run_command(
            ["apt-get", "install", "-y"] + packages,
            "Installing KVM/QEMU guest tools"
        )
        
        print(f"{Color.GREEN}✓ KVM/QEMU tools installed{Color.END}")
    
    def install_generic_vm_graphics(self):
        """Install generic VM graphics support"""
        packages = [
            "mesa-utils",
            "mesa-utils-extra",
            "libgl1-mesa-dri",
            "libgl1-mesa-dri:i386",
            "mesa-vulkan-drivers",
            "mesa-vulkan-drivers:i386"
        ]
        
        self.run_command(
            ["apt-get", "install", "-y"] + packages,
            "Installing generic VM graphics drivers"
        )
    
    def enable_32bit_support(self):
        """Enable 32-bit architecture support (required for many games)"""
        self.banner("32-BIT ARCHITECTURE SUPPORT")
        
        self.run_command(
            ["dpkg", "--add-architecture", "i386"],
            "Enabling i386 architecture"
        )
        self.run_command(["apt-get", "update"], "Updating package lists")
    
    def install_gaming_platforms(self):
        """Install Steam, Lutris, and other gaming platforms"""
        self.banner("GAMING PLATFORMS")
        
        # Install Steam
        if self.prompt_install_or_update("Steam", package_name="steam-installer"):
            print(f"{Color.CYAN}Installing Steam...{Color.END}")
            self.run_command(
                ["apt-get", "install", "-y", "steam-installer"],
                "Installing Steam"
            )
        
        # Install Lutris
        if self.prompt_install_or_update("Lutris", flatpak_id="net.lutris.Lutris"):
            print(f"{Color.CYAN}Installing Lutris...{Color.END}")
            print(f"{Color.YELLOW}Note: Installing via Flatpak (PPA not yet available for Ubuntu 24.04){Color.END}")
            
            # Ensure Flatpak is installed
            if not self.is_package_installed("flatpak"):
                self.run_command(
                    ["apt-get", "install", "-y", "flatpak"],
                    "Installing Flatpak"
                )
            
            # Add Flathub if not already added
            self.run_command(
                ["flatpak", "remote-add", "--if-not-exists", "flathub", 
                 "https://flathub.org/repo/flathub.flatpakrepo"],
                "Adding Flathub repository",
                check=False
            )
            
            # Install Lutris via Flatpak
            self.run_command(
                ["flatpak", "install", "-y", "flathub", "net.lutris.Lutris"],
                "Installing Lutris"
            )
        
        # Install GameMode
        if self.prompt_install_or_update("GameMode", package_name="gamemode"):
            # Install both 64-bit and 32-bit libraries for compatibility
            packages = ["gamemode", "libgamemode0", "libgamemode0:i386"]
            self.run_command(
                ["apt-get", "install", "-y"] + packages,
                "Installing GameMode with 32-bit and 64-bit libraries"
            )
        
        # Install Heroic Games Launcher (for Epic/GOG)
        if self.prompt_install_or_update("Heroic Games Launcher", flatpak_id="com.heroicgameslauncher.hgl"):
            print(f"{Color.CYAN}Installing Heroic Games Launcher...{Color.END}")
            self.install_heroic()
    
    def install_heroic(self):
        """Install Heroic Games Launcher via Flatpak"""
        # Install Flatpak if not present
        self.run_command(
            ["apt-get", "install", "-y", "flatpak"],
            "Installing Flatpak"
        )
        
        # Add Flathub repository
        self.run_command(
            ["flatpak", "remote-add", "--if-not-exists", "flathub", 
             "https://flathub.org/repo/flathub.flatpakrepo"],
            "Adding Flathub repository"
        )
        
        # Install Heroic
        self.run_command(
            ["flatpak", "install", "-y", "flathub", "com.heroicgameslauncher.hgl"],
            "Installing Heroic Games Launcher"
        )
    
    def install_wine_proton(self):
        """Install Wine and Proton compatibility layers"""
        self.banner("WINE & COMPATIBILITY LAYERS")
        
        if self.prompt_install_or_update("Wine (Windows compatibility)", package_name="winehq-staging"):
            print(f"{Color.CYAN}Installing Wine...{Color.END}")
            commands = [
                (["mkdir", "-pm755", "/etc/apt/keyrings"], "Creating keyring directory"),
                ("wget -O /etc/apt/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key", 
                 "Downloading WineHQ key", True, True),
                ("wget -NP /etc/apt/sources.list.d/ https://dl.winehq.org/wine-builds/ubuntu/dists/noble/winehq-noble.sources",
                 "Adding WineHQ repository", True, True),
                (["apt-get", "update"], "Updating package lists"),
                ("apt-get install -y --install-recommends winehq-staging", "Installing Wine Staging", True, True)
            ]
            
            for item in commands:
                if len(item) == 2:
                    cmd, desc = item
                    shell = False
                elif len(item) == 4:
                    cmd, desc, _, shell = item
                else:
                    continue
                    
                self.run_command(cmd, desc, shell=shell)
        
        if self.prompt_install_or_update("Winetricks (Wine configuration tool)", package_name="winetricks"):
            self.run_command(
                ["apt-get", "install", "-y", "winetricks"],
                "Installing Winetricks"
            )
        
        # ProtonUp-Qt for managing Proton versions
        if self.prompt_install_or_update("ProtonUp-Qt (Proton version manager)", flatpak_id="net.davidotek.pupgui2"):
            self.run_command(
                ["flatpak", "install", "-y", "flathub", "net.davidotek.pupgui2"],
                "Installing ProtonUp-Qt"
            )
    
    def install_essential_packages(self):
        """Install essential gaming packages and libraries"""
        self.banner("ESSENTIAL PACKAGES")
        
        packages = [
            # Core libraries
            "build-essential",
            "git",
            "curl",
            "wget",
            
            # Graphics libraries
            "libgl1-mesa-dri:i386",
            "mesa-vulkan-drivers",
            "mesa-vulkan-drivers:i386",
            
            # Audio
            "pulseaudio",
            "pavucontrol",
            
            # Controllers
            "joystick",
            "jstest-gtk",
            
            # Fonts
            "fonts-liberation",
            "fonts-wine",
            
            # Performance tools
            "linux-cpupower",
            
            # Additional tools
            "xboxdrv",
            "antimicrox"
        ]
        
        self.run_command(
            ["apt-get", "install", "-y"] + packages,
            "Installing essential packages"
        )
    
    def install_codecs(self):
        """Install multimedia codecs"""
        self.banner("MULTIMEDIA CODECS")
        
        if self.confirm("Install multimedia codecs?"):
            print(f"{Color.CYAN}Pre-accepting license agreements...{Color.END}")
            
            # Pre-accept EULA for ttf-mscorefonts-installer
            eula_commands = [
                "echo ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true | debconf-set-selections",
            ]
            
            for cmd in eula_commands:
                self.run_command(cmd, "Pre-accepting Microsoft fonts EULA", shell=True, check=False)
            
            # Install with non-interactive frontend
            env_cmd = "DEBIAN_FRONTEND=noninteractive apt-get install -y ubuntu-restricted-extras"
            self.run_command(
                env_cmd,
                "Installing Ubuntu restricted extras (codecs)",
                shell=True
            )
    
    def optimize_system(self):
        """Apply gaming optimizations"""
        self.banner("SYSTEM OPTIMIZATIONS")
        
        if self.confirm("Apply gaming optimizations?"):
            # Increase file watchers (for games like Star Citizen)
            print(f"{Color.CYAN}Increasing inotify watchers...{Color.END}")
            with open('/etc/sysctl.d/99-gaming.conf', 'w') as f:
                f.write("# Gaming optimizations\n")
                f.write("fs.inotify.max_user_watches=524288\n")
                f.write("vm.max_map_count=2147483642\n")
            
            self.run_command(["sysctl", "-p", "/etc/sysctl.d/99-gaming.conf"],
                           "Applying sysctl optimizations")
            
            # Enable performance governor
            if self.confirm("Set CPU governor to performance mode?"):
                packages = ["cpufrequtils"]
                self.run_command(
                    ["apt-get", "install", "-y"] + packages,
                    "Installing CPU frequency utilities"
                )
                
                # Create systemd service for performance governor
                governor_service = """[Unit]
Description=Set CPU Governor to Performance
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/usr/bin/cpufreq-set -r -g performance

[Install]
WantedBy=multi-user.target
"""
                with open('/etc/systemd/system/cpu-performance.service', 'w') as f:
                    f.write(governor_service)
                
                commands = [
                    (["systemctl", "daemon-reload"], "Reloading systemd"),
                    (["systemctl", "enable", "cpu-performance.service"], "Enabling performance governor service")
                ]
                for cmd, desc in commands:
                    self.run_command(cmd, desc)
    
    def install_discord(self):
        """Install Discord"""
        if self.prompt_install_or_update("Discord", flatpak_id="com.discordapp.Discord"):
            self.banner("DISCORD INSTALLATION")
            
            print(f"{Color.CYAN}Installing Discord via Flatpak...{Color.END}")
            self.run_command(
                ["flatpak", "install", "-y", "flathub", "com.discordapp.Discord"],
                "Installing Discord"
            )
    
    def install_obs(self):
        """Install OBS Studio for streaming/recording"""
        if self.prompt_install_or_update("OBS Studio (for streaming/recording)", package_name="obs-studio"):
            self.banner("OBS STUDIO INSTALLATION")
            
            commands = [
                (["add-apt-repository", "ppa:obsproject/obs-studio", "-y"], "Adding OBS PPA"),
                (["apt-get", "update"], "Updating package lists"),
                (["apt-get", "install", "-y", "obs-studio"], "Installing OBS Studio")
            ]
            
            for cmd, desc in commands:
                self.run_command(cmd, desc)
    
    def create_performance_script(self):
        """Create a gaming performance launcher script"""
        self.banner("PERFORMANCE LAUNCHER")
        
        if self.confirm("Create gaming performance launcher script?"):
            # User's home directory script
            user_script_path = REAL_USER_HOME / "launch-game.sh"
            
            # System-wide script location
            system_script_path = Path("/usr/local/bin/launch-game")
            
            script_content = """#!/bin/bash
# Gaming Performance Launcher
# Usage: ./launch-game.sh <game_command>
# Or: launch-game <game_command> (if installed system-wide)

# Color codes for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Function to safely set CPU governor
set_cpu_governor() {
    local governor="$1"
    
    # Check if cpupower is available (preferred)
    if command_exists cpupower; then
        sudo cpupower frequency-set -g "$governor" &> /dev/null
        return $?
    # Fallback to cpufreq-set if available
    elif command_exists cpufreq-set; then
        sudo cpufreq-set -r -g "$governor" &> /dev/null
        return $?
    fi
    
    return 1
}

echo "======================================"
echo "  Gaming Performance Launcher"
echo "======================================"

# Check if game command provided
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: No game command provided${NC}"
    echo "Usage: $0 <game_command>"
    echo "Example: $0 steam"
    echo "Example: $0 lutris"
    exit 1
fi

# Enable GameMode if available
GAMEMODE=""
if command_exists gamemoderun; then
    GAMEMODE="gamemoderun"
    echo -e "${GREEN}✓${NC} GameMode: ENABLED"
else
    echo -e "${YELLOW}!${NC} GameMode: Not available (install with: sudo apt install gamemode)"
fi

# Try to set CPU governor to performance
echo -n "CPU Governor: "
if set_cpu_governor "performance"; then
    echo -e "${GREEN}PERFORMANCE${NC}"
    GOVERNOR_CHANGED=1
else
    echo -e "${YELLOW}UNCHANGED${NC} (run 'sudo cpupower frequency-set -g performance' manually)"
    GOVERNOR_CHANGED=0
fi

# Set process scheduling (best effort, non-critical)
NICE_CMD=""
# Don't use nice -n -10 as it requires root and causes permission errors
# Instead use nice -n -5 which works for regular users
if command_exists nice; then
    NICE_CMD="nice -n -5"
fi

echo "======================================"
echo "Launching: $@"
echo "======================================"
echo ""

# Launch the game with optimizations
$GAMEMODE $NICE_CMD "$@"
EXIT_CODE=$?

echo ""
echo "======================================"
echo "Game exited with code: $EXIT_CODE"
echo "======================================"

# Restore CPU governor if we changed it
if [ $GOVERNOR_CHANGED -eq 1 ]; then
    echo -n "Restoring CPU Governor: "
    if set_cpu_governor "ondemand" || set_cpu_governor "powersave"; then
        echo -e "${GREEN}RESTORED${NC}"
    else
        echo -e "${YELLOW}UNCHANGED${NC} (will reset on reboot)"
    fi
fi

exit $EXIT_CODE
"""
            
            # Create in user's home directory
            with open(user_script_path, 'w') as f:
                f.write(script_content)
            
            os.chmod(user_script_path, 0o755)
            
            # Set proper ownership
            try:
                uid, gid = get_real_user_uid_gid()
                os.chown(user_script_path, uid, gid)
            except Exception as e:
                logging.warning(f"Could not set ownership on user script: {e}")
            
            print(f"{Color.GREEN}✓ Performance launcher created: {user_script_path}{Color.END}")
            print(f"  Usage: {user_script_path} <game_command>")
            
            # Optionally create system-wide version
            if self.confirm("Also install system-wide as 'launch-game' command?"):
                try:
                    with open(system_script_path, 'w') as f:
                        f.write(script_content)
                    os.chmod(system_script_path, 0o755)
                    print(f"{Color.GREEN}✓ System-wide launcher installed{Color.END}")
                    print(f"  Usage: launch-game <game_command>")
                except Exception as e:
                    logging.error(f"Could not create system-wide script: {e}")
                    print(f"{Color.YELLOW}Could not create system-wide script, but user script is available{Color.END}")
            
            # Offer to configure passwordless sudo for CPU governor
            if self.confirm("Configure passwordless sudo for CPU governor? (Recommended)"):
                self.configure_cpufreq_sudo()
    
    def configure_cpufreq_sudo(self):
        """Configure passwordless sudo for CPU frequency management"""
        sudoers_file = Path("/etc/sudoers.d/gaming-cpufreq")
        
        # Determine which tool is available
        cpufreq_tools = []
        if subprocess.run(["which", "cpupower"], capture_output=True).returncode == 0:
            cpufreq_tools.append("/usr/bin/cpupower")
        if subprocess.run(["which", "cpufreq-set"], capture_output=True).returncode == 0:
            cpufreq_tools.append("/usr/bin/cpufreq-set")
        
        if not cpufreq_tools:
            print(f"{Color.YELLOW}⚠ No CPU frequency tools found{Color.END}")
            print(f"  Installing cpupower...")
            self.run_command(
                ["apt-get", "install", "-y", "linux-cpupower"],
                "Installing CPU power management tools"
            )
            cpufreq_tools = ["/usr/bin/cpupower"]
        
        # Build sudoers content
        sudoers_lines = [
            f"# Allow {REAL_USER} to manage CPU frequency for gaming",
            f"# Created by Ubuntu Gaming Setup Script",
            ""
        ]
        
        for tool in cpufreq_tools:
            sudoers_lines.append(f"{REAL_USER} ALL=(ALL) NOPASSWD: {tool}")
        
        sudoers_content = "\n".join(sudoers_lines) + "\n"
        
        try:
            # Create sudoers file
            with open(sudoers_file, 'w') as f:
                f.write(sudoers_content)
            
            # Set correct permissions (sudoers files must be 0440)
            os.chmod(sudoers_file, 0o440)
            
            # Validate sudoers file
            result = subprocess.run(
                ["visudo", "-c", "-f", str(sudoers_file)],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                print(f"{Color.GREEN}✓ Passwordless sudo configured for CPU governor{Color.END}")
                print(f"  {REAL_USER} can now run CPU frequency tools without password")
                for tool in cpufreq_tools:
                    print(f"    - {tool}")
            else:
                # Remove invalid file
                sudoers_file.unlink()
                print(f"{Color.YELLOW}⚠ Sudoers configuration failed validation, removed{Color.END}")
                logging.error(f"Sudoers validation failed: {result.stderr}")
        
        except Exception as e:
            logging.error(f"Could not configure sudoers: {e}")
            print(f"{Color.YELLOW}⚠ Could not configure passwordless sudo{Color.END}")
            print(f"  You can manually run: sudo cpupower frequency-set -g performance")
    
    def final_steps(self):
        """Display final instructions"""
        self.banner("SETUP COMPLETE")
        
        print(f"{Color.GREEN}✓ Ubuntu gaming setup completed successfully!{Color.END}\n")
        print(f"{Color.BOLD}Installation performed for user: {REAL_USER}{Color.END}")
        print(f"{Color.BOLD}User home directory: {REAL_USER_HOME}{Color.END}\n")
        
        print(f"{Color.BOLD}IMPORTANT NEXT STEPS:{Color.END}\n")
        
        print(f"{Color.YELLOW}1. REBOOT YOUR SYSTEM{Color.END}")
        print("   Required for drivers and optimizations to take effect\n")
        
        # Check if VM
        vm_type = self.detect_virtualization()
        if vm_type:
            print(f"{Color.CYAN}VM-SPECIFIC NOTES ({vm_type}):{Color.END}")
            if 'vmware' in vm_type.lower():
                print("   • Enable 3D acceleration in VMware settings")
                print("   • Allocate at least 2GB video memory for better performance")
                print("   • Verify tools: vmware-toolbox-cmd -v")
            elif 'virtualbox' in vm_type.lower():
                print("   • Enable 3D acceleration in VirtualBox settings")
                print("   • Allocate maximum video memory (128MB+)")
                print("   • Verify additions: lsmod | grep vbox")
            print()
        
        print(f"{Color.YELLOW}2. VERIFY GPU/GRAPHICS{Color.END}")
        if vm_type:
            print("   Run: glxinfo | grep 'OpenGL renderer'")
            print(f"   Should show: {vm_type} graphics")
        else:
            print("   - NVIDIA: Run 'nvidia-smi' to verify driver")
            print("   - AMD/Intel: Run 'vulkaninfo' or 'glxinfo | grep OpenGL'")
        print()
        
        print(f"{Color.YELLOW}3. CONFIGURE STEAM{Color.END}")
        print("   - Enable Proton: Settings → Steam Play → Enable Steam Play for all titles")
        print("   - Select: Proton Experimental or latest Proton version")
        if vm_type:
            print(f"   {Color.CYAN}Note: Some games may have reduced performance in VMs{Color.END}")
        print()
        
        print(f"{Color.YELLOW}4. INSTALL ADDITIONAL PROTON VERSIONS{Color.END}")
        print("   - Use ProtonUp-Qt to install Proton-GE for better compatibility\n")
        
        print(f"{Color.YELLOW}5. USE PERFORMANCE LAUNCHER{Color.END}")
        user_launcher = REAL_USER_HOME / "launch-game.sh"
        if user_launcher.exists():
            print(f"   User script: {user_launcher} <game>")
        if Path("/usr/local/bin/launch-game").exists():
            print(f"   System-wide: launch-game <game>")
        print()
        
        if vm_type:
            print(f"{Color.CYAN}VM GAMING TIPS:{Color.END}")
            print("   • Start with lightweight/indie games to test performance")
            print("   • 2D games typically run very well in VMs")
            print("   • 3D games depend heavily on host GPU passthrough")
            print("   • Check ProtonDB for VM-specific compatibility notes\n")
        
        print(f"{Color.CYAN}FILES CREATED:{Color.END}")
        print(f"   Logs: {LOG_DIR}")
        print(f"   Latest log: {LOG_FILE}")
        if user_launcher.exists():
            print(f"   Performance launcher: {user_launcher}")
        if Path("/usr/local/bin/launch-game").exists():
            print(f"   System launcher: /usr/local/bin/launch-game")
        print()
        
        if self.confirm("Reboot now?"):
            print(f"{Color.GREEN}Rebooting system...{Color.END}")
            self.run_command(["reboot"], "Rebooting system")
        else:
            print(f"{Color.YELLOW}Remember to reboot before gaming!{Color.END}")
    
    def run(self):
        """Main execution flow"""
        print(f"{Color.BOLD}{Color.HEADER}")
        print("╔════════════════════════════════════════════════════════════╗")
        print("║        Ubuntu 24.04.3 Gaming Setup Script                 ║")
        print("║                                                            ║")
        print("║  This script will install and configure:                  ║")
        print("║  • GPU Drivers (NVIDIA/AMD/Intel) or VM Tools             ║")
        print("║  • Gaming Platforms (Steam, Lutris, Heroic)               ║")
        print("║  • Wine & Proton Compatibility                            ║")
        print("║  • System Optimizations                                   ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print(f"{Color.END}\n")
        
        print(f"{Color.CYAN}Running as root, installing for user: {Color.BOLD}{REAL_USER}{Color.END}")
        print(f"{Color.CYAN}User home directory: {REAL_USER_HOME}{Color.END}")
        print(f"{Color.CYAN}Logs will be saved to: {LOG_DIR}{Color.END}\n")
        
        if not self.confirm("Continue with installation?"):
            print("Installation cancelled.")
            sys.exit(0)
        
        try:
            # Core setup
            self.update_system()
            self.enable_32bit_support()
            
            # GPU/VM detection and driver installation
            gpu_type = self.detect_gpu()
            
            # Handle VM guest tools
            if gpu_type in ['vmware', 'virtualbox', 'kvm/qemu', 'vm']:
                if self.confirm(f"Install {gpu_type} guest tools for better graphics performance?"):
                    self.install_vm_tools(gpu_type)
            # Handle physical GPU drivers
            elif gpu_type == 'nvidia':
                if self.confirm("Install NVIDIA drivers?"):
                    self.install_nvidia_drivers()
            elif gpu_type == 'amd':
                if self.confirm("Install AMD drivers?"):
                    self.install_amd_drivers()
            elif gpu_type == 'intel':
                if self.confirm("Install Intel drivers?"):
                    self.install_intel_drivers()
            elif gpu_type == 'generic':
                print(f"{Color.YELLOW}Installing generic graphics support...{Color.END}")
                self.install_generic_vm_graphics()
            
            # Gaming components
            self.install_essential_packages()
            self.install_codecs()
            self.install_gaming_platforms()
            self.install_wine_proton()
            
            # Optional components
            self.install_discord()
            self.install_obs()
            
            # Optimizations
            self.optimize_system()
            self.create_performance_script()
            
            # Show what was installed
            self.show_installation_summary()
            
            # Set proper ownership on log file
            try:
                uid, gid = get_real_user_uid_gid()
                os.chown(LOG_FILE, uid, gid)
            except Exception as e:
                logging.warning(f"Could not set ownership on log file: {e}")
            
            # Completion
            self.final_steps()
            
        except KeyboardInterrupt:
            print(f"\n{Color.YELLOW}Installation interrupted by user{Color.END}")
            sys.exit(1)
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            print(f"{Color.RED}An error occurred. Check log file: {LOG_FILE}{Color.END}")
            sys.exit(1)

def main():
    """Entry point"""
    setup = GamingSetup()
    setup.run()

if __name__ == "__main__":
    main()
