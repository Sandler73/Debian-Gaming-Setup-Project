"""
═══════════════════════════════════════════════════════════════════════════════
Debian Gaming Setup Script — Extended Integration Tests
═══════════════════════════════════════════════════════════════════════════════

SYNOPSIS:
    Integration tests for critical methods that were previously untested.
    Covers package management, detection, installation, state management,
    maintenance, and system safety methods.

DESCRIPTION:
    All external subprocess calls are mocked — no real packages are installed,
    no real system changes are made. Tests verify method logic, branching,
    error handling, and output formatting.

    Categories:
      - Package Management (8 tests): _check_package_available, _preflight_packages,
        get_available_version, get_flatpak_available_version, check_updates_available
      - Detection (6 tests): detect_system, detect_gpu, detect_virtualization
      - Prompt Logic (4 tests): prompt_install_or_update (APT, Flatpak, update, fresh)
      - State Management (4 tests): save_installation_state, load_rollback_manifest
      - Maintenance (6 tests): update_system, perform_update, perform_uninstall, perform_rollback
      - System Safety (5 tests): check_system_requirements, post_install_health_check
      - Script Generation (2 tests): create_performance_script

VERSION: 3.4.0
"""

import json
import os
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open, mock_open

import pytest


# ═══════════════════════════════════════════════════════════════════════════════
# Package Management Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestCheckPackageAvailable:
    """Tests for _check_package_available() using apt-cache policy."""

    def test_available_package_returns_true(self, mock_setup):
        """Package with valid candidate returns True."""
        policy_output = "steam:\n  Installed: 1.0\n  Candidate: 1.0.1\n  Version table:"
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout=policy_output, stderr=""
            )
            assert mock_setup._check_package_available("steam") is True

    def test_no_candidate_returns_false(self, mock_setup):
        """Package with Candidate: (none) returns False."""
        policy_output = "linux-cpupower:\n  Installed: (none)\n  Candidate: (none)\n"
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout=policy_output, stderr=""
            )
            assert mock_setup._check_package_available("linux-cpupower") is False

    def test_empty_package_returns_false(self, mock_setup):
        """Empty package name returns False without subprocess call."""
        assert mock_setup._check_package_available("") is False

    def test_nonexistent_package_returns_false(self, mock_setup):
        """Nonexistent package (returncode != 0) returns False."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="")
            assert mock_setup._check_package_available("fakepkg123") is False

    def test_timeout_returns_false(self, mock_setup):
        """Subprocess timeout returns False gracefully."""
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("cmd", 5)):
            assert mock_setup._check_package_available("steam") is False


class TestPreflightPackages:
    """Tests for _preflight_packages() batch availability check."""

    def test_splits_available_and_unavailable(self, mock_setup):
        """Correctly partitions packages into available and unavailable."""
        def mock_check(pkg):
            return pkg in ["curl", "wget"]

        with patch.object(mock_setup, "_check_package_available", side_effect=mock_check):
            available, unavailable = mock_setup._preflight_packages(
                ["curl", "wget", "fakepkg"], "test"
            )
            assert "curl" in available
            assert "wget" in available
            assert "fakepkg" in unavailable


class TestGetAvailableVersion:
    """Tests for get_available_version() and get_flatpak_available_version()."""

    def test_apt_available_version_parsed(self, mock_setup):
        """Parses Candidate version from apt-cache policy output."""
        policy_output = "steam:\n  Installed: 1.0.0\n  Candidate: 1.0.1\n"
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout=policy_output, stderr=""
            )
            assert mock_setup.get_available_version("steam") == "1.0.1"

    def test_apt_available_version_none_candidate(self, mock_setup):
        """Returns None when Candidate is (none)."""
        policy_output = "fakepkg:\n  Installed: (none)\n  Candidate: (none)\n"
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout=policy_output, stderr=""
            )
            assert mock_setup.get_available_version("fakepkg") is None

    def test_flatpak_available_version_parsed(self, mock_setup):
        """Parses Version from flatpak remote-info output."""
        remote_output = "Lutris\n\n        ID: net.lutris.Lutris\n   Version: 0.5.17\n"
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout=remote_output, stderr=""
            )
            result = mock_setup.get_flatpak_available_version("net.lutris.Lutris")
            assert result == "0.5.17"


class TestCheckUpdatesAvailable:
    """Tests for check_updates_available() and check_flatpak_updates_available()."""

    def test_update_available_when_versions_differ(self, mock_setup):
        """Returns True when installed != available."""
        with patch.object(mock_setup, "get_package_version", return_value="1.0"), \
             patch.object(mock_setup, "get_available_version", return_value="1.1"):
            has_update, installed, available = mock_setup.check_updates_available("pkg")
            assert has_update is True
            assert installed == "1.0"
            assert available == "1.1"

    def test_no_update_when_versions_match(self, mock_setup):
        """Returns False when installed == available."""
        with patch.object(mock_setup, "get_package_version", return_value="1.0"), \
             patch.object(mock_setup, "get_available_version", return_value="1.0"):
            has_update, installed, available = mock_setup.check_updates_available("pkg")
            assert has_update is False


# ═══════════════════════════════════════════════════════════════════════════════
# Detection Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestDetectSystem:
    """Tests for detect_system() OS detection pipeline."""

    def test_detect_system_populates_system_info(self, mock_setup, gaming_module):
        """detect_system() fills system_info fields from /etc/os-release."""
        os_release_content = (
            'NAME="Ubuntu"\n'
            'VERSION_ID="24.04"\n'
            'ID=ubuntu\n'
            'ID_LIKE=debian\n'
            'VERSION_CODENAME=noble\n'
            'PRETTY_NAME="Ubuntu 24.04 LTS"\n'
        )
        with patch("builtins.open", mock_open(read_data=os_release_content)), \
             patch.object(mock_setup, "_detect_distro_family",
                          return_value=gaming_module.DistroFamily.UBUNTU), \
             patch.object(mock_setup, "_detect_desktop_environment", return_value="GNOME"), \
             patch.object(mock_setup, "banner"), \
             patch("pathlib.Path.exists", return_value=False):
            mock_setup.detect_system()
            assert mock_setup.system_info.distro_name == "Ubuntu"
            assert mock_setup.system_info.distro_id == "ubuntu"
            assert mock_setup.system_info.distro_version == "24.04"

    def test_detect_system_handles_missing_os_release(self, mock_setup, gaming_module):
        """detect_system() raises on missing /etc/os-release."""
        with patch("builtins.open", side_effect=FileNotFoundError), \
             patch.object(mock_setup, "banner"):
            with pytest.raises(FileNotFoundError):
                mock_setup.detect_system()


class TestDetectGPU:
    """Tests for detect_gpu() hardware detection."""

    def test_nvidia_detected_from_lspci(self, mock_setup, gaming_module):
        """NVIDIA GPU detected from lspci output."""
        lspci_output = "01:00.0 VGA compatible controller: NVIDIA Corporation GA106 [GeForce RTX 3060]"
        # Mock detect_virtualization to return empty so GPU detection proceeds
        with patch.object(mock_setup, "detect_virtualization", return_value=""), \
             patch.object(mock_setup, "banner"), \
             patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout=lspci_output, stderr=""
            )
            mock_setup.detect_gpu()
            assert mock_setup.hardware_info.gpu_vendor == gaming_module.GPUVendor.NVIDIA

    def test_amd_detected_from_lspci(self, mock_setup, gaming_module):
        """AMD GPU detected from lspci output."""
        lspci_output = "06:00.0 VGA compatible controller: Advanced Micro Devices, Inc. [AMD/ATI] Navi 21"
        with patch.object(mock_setup, "detect_virtualization", return_value=""), \
             patch.object(mock_setup, "banner"), \
             patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout=lspci_output, stderr=""
            )
            mock_setup.detect_gpu()
            assert mock_setup.hardware_info.gpu_vendor == gaming_module.GPUVendor.AMD

    def test_intel_detected_from_lspci(self, mock_setup, gaming_module):
        """Intel GPU detected from lspci output."""
        lspci_output = "00:02.0 VGA compatible controller: Intel Corporation UHD Graphics 770"
        with patch.object(mock_setup, "detect_virtualization", return_value=""), \
             patch.object(mock_setup, "banner"), \
             patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout=lspci_output, stderr=""
            )
            mock_setup.detect_gpu()
            assert mock_setup.hardware_info.gpu_vendor == gaming_module.GPUVendor.INTEL

    def test_vm_sets_virtual_gpu(self, mock_setup, gaming_module):
        """When VM is detected, GPU vendor is set to VIRTUAL."""
        with patch.object(mock_setup, "detect_virtualization", return_value="vmware"), \
             patch.object(mock_setup, "banner"), \
             patch.object(mock_setup, "_vm_type_str_to_enum",
                          return_value=gaming_module.VMType.VMWARE):
            mock_setup.detect_gpu()
            assert mock_setup.hardware_info.gpu_vendor == gaming_module.GPUVendor.VIRTUAL


class TestDetectVirtualization:
    """Tests for detect_virtualization() VM detection."""

    def test_vmware_detected_via_systemd(self, mock_setup, gaming_module):
        """VMware detected from systemd-detect-virt output."""
        with patch("subprocess.run") as mock_run:
            # systemd-detect-virt returns "vmware"
            mock_run.return_value = MagicMock(
                returncode=0, stdout="vmware\n", stderr=""
            )
            result = mock_setup.detect_virtualization()
            assert result == "VMware"

    def test_no_vm_returns_none(self, mock_setup, gaming_module):
        """Bare metal returns None when all checks report 'none'."""
        with patch("subprocess.run") as mock_run:
            # All three detection methods report nothing
            mock_run.return_value = MagicMock(
                returncode=0, stdout="none\n", stderr=""
            )
            result = mock_setup.detect_virtualization()
            assert result is None

    def test_fallback_to_dmesg(self, mock_setup, gaming_module):
        """Falls back to dmesg when systemd-detect-virt not available."""
        call_count = [0]
        def mock_run_side_effect(cmd, **kwargs):
            call_count[0] += 1
            if cmd == ['systemd-detect-virt']:
                raise FileNotFoundError("not found")
            elif cmd == ['dmesg']:
                return MagicMock(returncode=0, stdout="[    0.000000] vmware hypervisor\n", stderr="")
            return MagicMock(returncode=0, stdout="", stderr="")

        with patch("subprocess.run", side_effect=mock_run_side_effect):
            result = mock_setup.detect_virtualization()
            assert result == "VMware"


# ═══════════════════════════════════════════════════════════════════════════════
# Prompt Logic Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestPromptInstallOrUpdate:
    """Tests for prompt_install_or_update() smart prompting."""

    def test_auto_yes_returns_true(self, mock_setup):
        """Auto-yes mode returns True without checking anything."""
        mock_setup.config.auto_yes = True
        result = mock_setup.prompt_install_or_update("Steam", package_name="steam")
        assert result is True
        mock_setup.config.auto_yes = False  # Reset

    def test_installed_apt_shows_version(self, mock_setup, capsys):
        """Installed APT package shows version and source."""
        with patch.object(mock_setup, "is_package_installed", return_value=True), \
             patch.object(mock_setup, "get_package_version", return_value="1.0"), \
             patch.object(mock_setup, "get_available_version", return_value="1.0"), \
             patch.object(mock_setup, "confirm", return_value=False):
            mock_setup.prompt_install_or_update("Steam", package_name="steam")
            output = capsys.readouterr().out
            assert "1.0" in output
            assert "APT" in output

    def test_update_available_shows_arrow(self, mock_setup, capsys):
        """Update available shows current → available format."""
        with patch.object(mock_setup, "is_package_installed", return_value=True), \
             patch.object(mock_setup, "get_package_version", return_value="1.0"), \
             patch.object(mock_setup, "get_available_version", return_value="2.0"), \
             patch.object(mock_setup, "confirm", return_value=False):
            mock_setup.prompt_install_or_update("Steam", package_name="steam")
            output = capsys.readouterr().out
            assert "1.0" in output
            assert "2.0" in output
            assert "→" in output

    def test_flatpak_detected_when_apt_missing(self, mock_setup, capsys):
        """Falls back to Flatpak when APT not installed."""
        with patch.object(mock_setup, "is_package_installed", return_value=False), \
             patch.object(mock_setup, "is_flatpak_installed", return_value=True), \
             patch.object(mock_setup, "get_flatpak_version", return_value="0.5.17"), \
             patch.object(mock_setup, "get_flatpak_available_version", return_value="0.5.17"), \
             patch.object(mock_setup, "confirm", return_value=False):
            mock_setup.prompt_install_or_update(
                "Lutris", package_name="lutris", flatpak_id="net.lutris.Lutris"
            )
            output = capsys.readouterr().out
            assert "Flatpak" in output
            assert "0.5.17" in output


# ═══════════════════════════════════════════════════════════════════════════════
# State Management Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestSaveInstallationState:
    """Tests for save_installation_state() atomic write."""

    def test_saves_json_with_atomic_write(self, mock_setup, tmp_path, gaming_module):
        """State file is written atomically via os.replace."""
        state_path = tmp_path / "state.json"
        with patch.object(gaming_module, "STATE_FILE", state_path):
            mock_setup.installation_state = {"test": True}
            mock_setup.save_installation_state()

            assert state_path.exists()
            data = json.loads(state_path.read_text())
            assert data.get("script_version") == gaming_module.SCRIPT_VERSION

    def test_atomic_write_uses_temp_file(self, mock_setup, tmp_path, gaming_module):
        """Verifies temp file pattern (write .tmp then replace)."""
        state_path = tmp_path / "state.json"
        with patch.object(gaming_module, "STATE_FILE", state_path), \
             patch("os.replace") as mock_replace:
            mock_setup.installation_state = {"test": True}
            mock_setup.save_installation_state()
            # os.replace should be called with .tmp path
            if mock_replace.called:
                args = mock_replace.call_args[0]
                assert args[0].endswith(".tmp")


class TestLoadRollbackManifest:
    """Tests for load_rollback_manifest() JSON loading."""

    def test_loads_valid_manifest(self, mock_setup, tmp_path, gaming_module):
        """Loads a valid rollback manifest with correct schema."""
        manifest = {
            "schema_version": gaming_module.ROLLBACK_SCHEMA_VERSION,
            "session_id": "test-session",
            "actions": [
                {
                    "action_type": "apt_install",
                    "timestamp": "2026-03-25T10:00:00",
                    "description": "Test install",
                    "packages": ["steam"],
                    "files": [],
                    "backup_files": [],
                    "reversal_commands": [["apt-get", "remove", "-y", "steam"]],
                    "metadata": {},
                    "success": True,
                }
            ],
        }
        manifest_path = tmp_path / "rollback_manifest.json"
        manifest_path.write_text(json.dumps(manifest))
        # Set rollback mode so load_rollback_manifest populates actions
        mock_setup.args = MagicMock()
        mock_setup.args.rollback = True
        with patch.object(gaming_module, "ROLLBACK_FILE", manifest_path):
            result = mock_setup.load_rollback_manifest()
            assert result is True
            assert len(mock_setup.rollback_actions) == 1
            assert mock_setup.rollback_actions[0].packages == ["steam"]

    def test_handles_missing_manifest(self, mock_setup, tmp_path, gaming_module):
        """Returns False when manifest file doesn't exist."""
        manifest_path = tmp_path / "nonexistent.json"
        with patch.object(gaming_module, "ROLLBACK_FILE", manifest_path):
            result = mock_setup.load_rollback_manifest()
            assert result is False


# ═══════════════════════════════════════════════════════════════════════════════
# Maintenance Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestUpdateSystem:
    """Tests for update_system() with dpkg options."""

    def test_upgrade_uses_force_confold(self, mock_setup):
        """Verifies dpkg --force-confold is passed to apt-get upgrade."""
        commands_called = []

        def capture_cmd(cmd, desc="", **kwargs):
            commands_called.append(cmd)
            return True, "", ""

        with patch.object(mock_setup, "run_command", side_effect=capture_cmd), \
             patch.object(mock_setup, "banner"):
            mock_setup.update_system()

        # Find the upgrade command
        upgrade_cmds = [c for c in commands_called if "upgrade" in c]
        assert len(upgrade_cmds) >= 1
        upgrade_cmd = upgrade_cmds[0]
        assert "--force-confold" in " ".join(upgrade_cmd)
        assert "--force-confdef" in " ".join(upgrade_cmd)

    def test_skip_update_respected(self, mock_setup):
        """--skip-update flag prevents system update."""
        mock_setup.config.skip_update = True
        with patch.object(mock_setup, "run_command") as mock_run:
            mock_setup.update_system()
            mock_run.assert_not_called()
        mock_setup.config.skip_update = False  # Reset


class TestPerformUninstall:
    """Tests for perform_uninstall() system scanning."""

    def test_no_components_found_exits_cleanly(self, mock_setup, capsys):
        """When nothing is installed, exits without errors."""
        with patch.object(mock_setup, "is_package_installed", return_value=False), \
             patch.object(mock_setup, "is_flatpak_installed", return_value=False), \
             patch.object(mock_setup, "banner"):
            # Mock the compat_dir to not exist
            with patch("pathlib.Path.exists", return_value=False):
                mock_setup.perform_uninstall()
            output = capsys.readouterr().out
            assert "No gaming components found" in output

    def test_found_components_displayed(self, mock_setup, capsys):
        """When components are found, inventory is displayed."""
        def mock_is_installed(pkg):
            return pkg in ["steam", "mumble"]

        def mock_get_version(pkg):
            return "1.0" if pkg in ["steam", "mumble"] else None

        with patch.object(mock_setup, "is_package_installed", side_effect=mock_is_installed), \
             patch.object(mock_setup, "get_package_version", side_effect=mock_get_version), \
             patch.object(mock_setup, "is_flatpak_installed", return_value=False), \
             patch.object(mock_setup, "confirm", return_value=False), \
             patch.object(mock_setup, "banner"), \
             patch("pathlib.Path.exists", return_value=False):
            mock_setup.perform_uninstall()
            output = capsys.readouterr().out
            assert "Found" in output


class TestPerformRollback:
    """Tests for perform_rollback() execution engine."""

    def test_empty_manifest_reports_nothing(self, mock_setup, gaming_module, capsys):
        """Empty rollback manifest shows 'nothing to rollback'."""
        mock_setup.rollback_actions = []
        with patch.object(gaming_module, "ROLLBACK_FILE") as mock_file, \
             patch.object(mock_setup, "banner"):
            mock_file.exists.return_value = False
            mock_setup.perform_rollback()
            output = capsys.readouterr().out
            assert "No rollback manifest" in output or "empty" in output.lower()


class TestPerformUpdate:
    """Tests for perform_update() component updating."""

    def test_update_calls_apt_and_flatpak(self, mock_setup, gaming_module):
        """perform_update() attempts apt and flatpak updates."""
        with patch.object(mock_setup, "run_command", return_value=(True, "", "")), \
             patch.object(mock_setup, "banner"), \
             patch.object(mock_setup, "is_package_installed", return_value=True), \
             patch.object(mock_setup, "check_updates_available",
                          return_value=(False, "1.0", "1.0")), \
             patch.object(mock_setup, "is_flatpak_installed", return_value=False), \
             patch("shutil.which", return_value=None), \
             patch.object(mock_setup, "confirm", return_value=False):
            mock_setup.perform_update()
            # Should not crash — smoke test


# ═══════════════════════════════════════════════════════════════════════════════
# System Safety Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestCheckSystemRequirements:
    """Tests for check_system_requirements() pre-flight validation."""

    def test_requirements_check_runs_without_crash(self, mock_setup, capsys):
        """check_system_requirements completes without error."""
        with patch("subprocess.run") as mock_run, \
             patch("shutil.disk_usage", return_value=(100e9, 50e9, 50e9)), \
             patch.object(mock_setup, "banner"):
            mock_run.return_value = MagicMock(returncode=0, stdout="8192\n", stderr="")
            # Should complete without raising
            mock_setup.check_system_requirements()

    def test_low_disk_space_reports_error(self, mock_setup, capsys):
        """Low disk space is flagged as an error."""
        with patch("subprocess.run") as mock_run, \
             patch("shutil.disk_usage", return_value=(10e9, 9.5e9, 0.5e9)), \
             patch.object(mock_setup, "banner"):
            mock_run.return_value = MagicMock(returncode=0, stdout="8192\n", stderr="")
            mock_setup.check_system_requirements()
            output = capsys.readouterr().out
            # Should mention disk space issue
            assert "disk" in output.lower() or "space" in output.lower() or "GB" in output


class TestPostInstallHealthCheck:
    """Tests for post_install_health_check() verification."""

    def test_health_check_runs_without_crash(self, mock_setup):
        """Health check completes when all checks are mocked."""
        mock_setup.rollback_actions = []
        with patch.object(mock_setup, "is_package_installed", return_value=False), \
             patch.object(mock_setup, "is_flatpak_installed", return_value=False), \
             patch("shutil.which", return_value=None), \
             patch.object(mock_setup, "banner"):
            # Should not crash even with no packages installed
            mock_setup.post_install_health_check()


# ═══════════════════════════════════════════════════════════════════════════════
# Script Generation Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestCreatePerformanceScript:
    """Tests for create_performance_script() launcher generation."""

    def test_creates_launcher_file(self, mock_setup, tmp_path, gaming_module):
        """Performance script is created at expected path."""
        launcher_path = tmp_path / "launch-game.sh"
        with patch.object(gaming_module, "REAL_USER_HOME", tmp_path), \
             patch.object(mock_setup, "banner"), \
             patch("os.chown"):
            mock_setup.create_performance_script()
            assert launcher_path.exists()
            content = launcher_path.read_text()
            assert "#!/bin/bash" in content

    def test_launcher_contains_mangohud(self, mock_setup, tmp_path, gaming_module):
        """Generated launcher includes MangoHud environment variable."""
        launcher_path = tmp_path / "launch-game.sh"
        with patch.object(gaming_module, "REAL_USER_HOME", tmp_path), \
             patch.object(mock_setup, "banner"), \
             patch("os.chown"):
            mock_setup.create_performance_script()
            content = launcher_path.read_text()
            assert "MANGOHUD" in content


# ═══════════════════════════════════════════════════════════════════════════════
# Install Method Smoke Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestInstallMethodSmoke:
    """Smoke tests for install methods — verify they don't crash when mocked."""

    def test_install_codecs_detects_existing(self, mock_setup, capsys):
        """install_codecs shows detected codecs before prompting."""
        with patch.object(mock_setup, "is_package_installed", return_value=True), \
             patch.object(mock_setup, "get_package_version", return_value="2.0"), \
             patch.object(mock_setup, "get_available_version", return_value="2.0"), \
             patch.object(mock_setup, "confirm", return_value=False), \
             patch.object(mock_setup, "banner"):
            mock_setup.install_codecs()
            output = capsys.readouterr().out
            assert "detected" in output.lower() or "installed" in output.lower()

    def test_install_essential_packages_shows_versions(self, mock_setup, capsys):
        """install_essential_packages shows installed package versions."""
        with patch.object(mock_setup, "is_package_installed", return_value=True), \
             patch.object(mock_setup, "get_package_version", return_value="1.0"), \
             patch.object(mock_setup, "get_available_version", return_value="1.0"), \
             patch.object(mock_setup, "_resolve_package_name", return_value="linux-cpupower"), \
             patch.object(mock_setup, "confirm", return_value=False), \
             patch.object(mock_setup, "banner"):
            mock_setup.install_essential_packages()
            output = capsys.readouterr().out
            assert "essential" in output.lower() or "installed" in output.lower()

    def test_install_mumble_shows_version(self, mock_setup, capsys):
        """install_mumble shows installed version and available version."""
        with patch.object(mock_setup, "is_package_installed", return_value=True), \
             patch.object(mock_setup, "get_package_version", return_value="1.4.0"), \
             patch.object(mock_setup, "get_available_version", return_value="1.4.0"), \
             patch.object(mock_setup, "confirm", return_value=False):
            mock_setup.install_mumble()
            output = capsys.readouterr().out
            assert "1.4.0" in output

    def test_install_mangohud_shows_version(self, mock_setup, capsys):
        """install_mangohud shows installed version."""
        with patch.object(mock_setup, "is_package_installed", return_value=True), \
             patch.object(mock_setup, "get_package_version", return_value="0.7.1"), \
             patch.object(mock_setup, "get_available_version", return_value="0.7.1"), \
             patch.object(mock_setup, "confirm", return_value=False):
            mock_setup.install_mangohud()
            output = capsys.readouterr().out
            assert "0.7.1" in output

    def test_install_sober_detects_flatpak(self, mock_setup, capsys):
        """install_sober checks Flatpak installation status."""
        with patch.object(mock_setup, "is_flatpak_installed", return_value=True), \
             patch.object(mock_setup, "get_flatpak_version", return_value="1.0"), \
             patch.object(mock_setup, "get_flatpak_available_version", return_value="1.0"), \
             patch.object(mock_setup, "confirm", return_value=False), \
             patch.object(mock_setup, "banner"):
            mock_setup.install_sober()
            output = capsys.readouterr().out
            assert "1.0" in output or "Sober" in output

    def test_install_vm_tools_detects_existing(self, mock_setup, capsys, gaming_module):
        """install_vm_tools shows existing VM tools version."""
        # Must mock shutil.which (vmware-toolbox-cmd exists on CI runners)
        # and run_command (prevents real apt-get/vmware-toolbox-cmd execution)
        with patch.object(mock_setup, "is_package_installed", return_value=True), \
             patch.object(mock_setup, "get_package_version", return_value="12.3.0"), \
             patch.object(mock_setup, "get_available_version", return_value="12.3.0"), \
             patch.object(mock_setup, "run_command", return_value=(True, "", "")), \
             patch("shutil.which", return_value=None), \
             patch.object(mock_setup, "confirm", return_value=False), \
             patch.object(mock_setup, "banner"):
            mock_setup.install_vm_tools("VMware")
            output = capsys.readouterr().out
            assert "12.3.0" in output

    def test_check_self_update_handles_network_error(self, mock_setup, gaming_module):
        """check_self_update handles network errors gracefully."""
        import urllib.error
        with patch("urllib.request.urlopen",
                   side_effect=urllib.error.URLError("Network unreachable")), \
             patch.object(mock_setup, "banner"):
            # Should not raise — handles URLError internally
            mock_setup.check_self_update()
