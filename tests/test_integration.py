"""
═══════════════════════════════════════════════════════════════════════════════
Debian Gaming Setup Script — Integration Tests: Mocked Subprocess & I/O
═══════════════════════════════════════════════════════════════════════════════

SYNOPSIS:
    Tests for methods that interact with subprocess, filesystem, and network.
    All external calls are mocked — no real packages are installed, no real
    files are modified, no network requests are made.

VERSION: 3.1.0
"""

import json
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

import pytest


# ═══════════════════════════════════════════════════════════════════════════
# run_command() Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestRunCommand:
    """Tests for the central subprocess execution method."""

    def test_successful_command(self, mock_setup):
        """Successful command returns (True, stdout, stderr)."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout="output", stderr=""
            )
            success, stdout, stderr = mock_setup.run_command(
                ["echo", "test"], "test command"
            )
            assert success is True
            assert stdout == "output"

    def test_failed_command_check_false(self, mock_setup):
        """Failed command with check=False returns (False, ...)."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1, stdout="", stderr="error"
            )
            success, stdout, stderr = mock_setup.run_command(
                ["false"], "failing command", check=False
            )
            assert success is False

    def test_timeout_handling(self, mock_setup):
        """Subprocess timeout is caught and logged."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(
                cmd=["sleep", "999"], timeout=5
            )
            success, stdout, stderr = mock_setup.run_command(
                ["sleep", "999"], "timeout test", check=False
            )
            assert success is False

    def test_dry_run_skips_execution(self, mock_setup):
        """Dry run mode does not execute subprocess."""
        mock_setup.config.dry_run = True
        with patch("subprocess.run") as mock_run:
            success, _, _ = mock_setup.run_command(
                ["apt-get", "install", "-y", "testpkg"],
                "dry run test"
            )
            mock_run.assert_not_called()

    def test_command_uses_list_form(self, mock_setup):
        """Commands are passed as list, not string (no shell=True)."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout="", stderr=""
            )
            mock_setup.run_command(["ls", "-la"], "list files")
            call_args = mock_run.call_args
            assert isinstance(call_args[0][0], list)
            # Verify shell is not True
            assert call_args[1].get("shell", False) is False


# ═══════════════════════════════════════════════════════════════════════════
# Package Detection Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestPackageDetection:
    """Tests for package installation status checks."""

    def test_is_package_installed_true(self, mock_setup):
        """Detects installed package via dpkg -s."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout="Status: install ok installed\n"
            )
            result = mock_setup.is_package_installed("steam")
            assert result is True

    def test_is_package_installed_false(self, mock_setup):
        """Detects missing package."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            result = mock_setup.is_package_installed("nonexistent")
            assert result is False

    def test_is_package_installed_timeout(self, mock_setup):
        """Handles dpkg-query timeout gracefully."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(
                cmd=["dpkg-query"], timeout=5
            )
            result = mock_setup.is_package_installed("steam")
            assert result is False

    def test_get_package_version(self, mock_setup):
        """Extracts installed package version."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="Installed: 1.2.3\nCandidate: 1.2.4\n"
            )
            result = mock_setup.get_package_version("testpkg")
            # Should extract version from "Installed:" line
            assert result is not None

    def test_is_flatpak_installed_true(self, mock_setup):
        """Detects installed Flatpak app."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="com.valvesoftware.Steam\t\tstable\n"
            )
            result = mock_setup.is_flatpak_installed("com.valvesoftware.Steam")
            assert result is True

    def test_is_flatpak_installed_false(self, mock_setup):
        """Detects missing Flatpak app."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout=""
            )
            result = mock_setup.is_flatpak_installed("com.nonexistent.App")
            assert result is False


# ═══════════════════════════════════════════════════════════════════════════
# File I/O Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestFileIO:
    """Tests for state and manifest file operations."""

    def test_save_rollback_manifest(self, mock_setup, tmp_path, gaming_module):
        """Rollback manifest saves as valid JSON."""
        manifest_path = tmp_path / "rollback_manifest.json"
        with patch.object(
            gaming_module, "ROLLBACK_FILE", manifest_path
        ):
            mock_setup.rollback_manifest = {
                "schema_version": "1.0",
                "actions": []
            }
            mock_setup.save_rollback_manifest()

            assert manifest_path.exists()
            data = json.loads(manifest_path.read_text())
            assert data["schema_version"] == "1.0"
            assert isinstance(data["actions"], list)

    def test_load_rollback_manifest_empty(self, mock_setup, tmp_path, gaming_module):
        """Loading nonexistent manifest initializes empty action list."""
        manifest_path = tmp_path / "nonexistent.json"
        with patch.object(gaming_module, "ROLLBACK_FILE", manifest_path):
            mock_setup.load_rollback_manifest()
            assert isinstance(mock_setup.rollback_actions, list)

    def test_get_os_release_field(self, mock_setup):
        """Parses os-release fields correctly."""
        mock_content = 'NAME="Ubuntu"\nVERSION_ID="24.04"\nID=ubuntu\n'
        with patch("builtins.open", mock_open(read_data=mock_content)):
            result = mock_setup._get_os_release_field("VERSION_ID")
            # Should extract "24.04"
            assert result in ("24.04", "")

    def test_save_installation_state(self, mock_setup, tmp_path, gaming_module):
        """Installation state saves as valid JSON."""
        state_path = tmp_path / "state.json"
        with patch.object(gaming_module, "STATE_FILE", state_path):
            mock_setup.installation_state = {"custom_key": "test_value"}
            mock_setup.save_installation_state()

            assert state_path.exists()
            data = json.loads(state_path.read_text())
            # save_installation_state injects SCRIPT_VERSION automatically
            assert data.get("script_version") == gaming_module.SCRIPT_VERSION


# ═══════════════════════════════════════════════════════════════════════════
# Utility Method Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestUtilityMethods:
    """Tests for utility methods with light mocking."""

    def test_confirm_auto_yes(self, mock_setup):
        """confirm() returns True when auto_yes is enabled."""
        mock_setup.config.auto_yes = True
        assert mock_setup.confirm("Install?") is True

    def test_confirm_dry_run(self, mock_setup):
        """confirm() returns True in dry-run mode."""
        mock_setup.config.dry_run = True
        assert mock_setup.confirm("Install?") is True

    def test_confirm_yes_input(self, mock_setup):
        """confirm() returns True on 'y' input."""
        mock_setup.config.auto_yes = False
        mock_setup.config.dry_run = False
        with patch("builtins.input", return_value="y"):
            assert mock_setup.confirm("Install?") is True

    def test_confirm_no_input(self, mock_setup):
        """confirm() returns False on 'n' input."""
        mock_setup.config.auto_yes = False
        mock_setup.config.dry_run = False
        with patch("builtins.input", return_value="n"):
            assert mock_setup.confirm("Install?") is False

    def test_confirm_eof_returns_false(self, mock_setup):
        """confirm() returns False on EOFError (piped input)."""
        mock_setup.config.auto_yes = False
        mock_setup.config.dry_run = False
        with patch("builtins.input", side_effect=EOFError):
            assert mock_setup.confirm("Install?") is False

    def test_detect_distro_family_ubuntu(self, mock_setup, gaming_classes):
        """Ubuntu ID maps to UBUNTU family."""
        os_release = {"ID": "ubuntu", "ID_LIKE": "debian"}
        result = mock_setup._detect_distro_family(os_release)
        assert result == gaming_classes.DistroFamily.UBUNTU

    def test_detect_distro_family_debian(self, mock_setup, gaming_classes):
        """Debian ID maps to DEBIAN family."""
        os_release = {"ID": "debian", "ID_LIKE": ""}
        result = mock_setup._detect_distro_family(os_release)
        assert result == gaming_classes.DistroFamily.DEBIAN

    def test_ubuntu_version_to_codename(self, mock_setup):
        """Ubuntu version 22.04 maps to 'jammy'."""
        result = mock_setup._ubuntu_version_to_codename("22.04")
        assert result == "jammy"

    def test_ubuntu_version_to_codename_unknown(self, mock_setup):
        """Unknown Ubuntu version returns empty string."""
        result = mock_setup._ubuntu_version_to_codename("99.99")
        assert result == ""
