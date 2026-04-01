"""
═══════════════════════════════════════════════════════════════════════════════
Debian Gaming Setup Script — Unit Tests: Pure Functions
═══════════════════════════════════════════════════════════════════════════════

SYNOPSIS:
    Tests for functions with no or minimal side effects — version parsing,
    argument parsing, color management, enum/dataclass construction.

VERSION: 3.1.0
"""

import os
from unittest.mock import patch

import pytest


# ═══════════════════════════════════════════════════════════════════════════
# _parse_version() Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestParseVersion:
    """Tests for the semantic version parser."""

    def test_simple_version(self, parse_version):
        """Standard three-part version parses correctly."""
        assert parse_version("2.6.0") == (2, 6, 0)

    def test_two_part_version(self, parse_version):
        """Two-part version pads to three parts."""
        assert parse_version("3.0") == (3, 0, 0)

    def test_single_part_version(self, parse_version):
        """Single number version pads to three parts."""
        assert parse_version("5") == (5, 0, 0)

    def test_v_prefix_stripped(self, parse_version):
        """Leading 'v' is removed before parsing."""
        assert parse_version("v2.6.0") == (2, 6, 0)

    def test_hyphen_suffix_stripped(self, parse_version):
        """Hyphenated suffixes (e.g., -beta1) are stripped."""
        assert parse_version("2.6.0-beta1") == (2, 6, 0)

    def test_version_comparison_newer(self, parse_version):
        """Newer version compares greater."""
        assert parse_version("3.0.0") > parse_version("2.6.0")

    def test_version_comparison_equal(self, parse_version):
        """Equal versions compare equal."""
        assert parse_version("2.6.0") == parse_version("2.6.0")

    def test_version_comparison_older(self, parse_version):
        """Older version compares less."""
        assert parse_version("2.5.0") < parse_version("2.6.0")

    def test_version_comparison_minor(self, parse_version):
        """Minor version difference detected."""
        assert parse_version("2.7.0") > parse_version("2.6.9")

    def test_empty_string_returns_zero(self, parse_version):
        """Empty string returns (0, 0, 0) fallback."""
        result = parse_version("")
        assert result == (0, 0, 0)

    def test_malformed_version_no_crash(self, parse_version):
        """Malformed version string doesn't crash."""
        result = parse_version("not.a.version")
        # Should return a tuple gracefully
        assert isinstance(result, tuple)

    def test_v_prefix_only(self, parse_version):
        """String 'v' alone returns (0, 0, 0)."""
        result = parse_version("v")
        assert result == (0, 0, 0)


# ═══════════════════════════════════════════════════════════════════════════
# parse_arguments() Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestParseArguments:
    """Tests for CLI argument parser."""

    def test_default_args(self, gaming_module):
        """No arguments produces defaults (all False)."""
        with patch("sys.argv", ["debian_gaming_setup.py"]):
            args = gaming_module.parse_arguments()
        assert args.dry_run is False
        assert args.yes is False
        assert args.steam is False
        assert args.nvidia is False

    def test_dry_run_flag(self, gaming_module):
        """--dry-run flag sets dry_run to True."""
        with patch("sys.argv", ["debian_gaming_setup.py", "--dry-run"]):
            args = gaming_module.parse_arguments()
        assert args.dry_run is True

    def test_yes_short_flag(self, gaming_module):
        """-y flag sets yes to True."""
        with patch("sys.argv", ["debian_gaming_setup.py", "-y"]):
            args = gaming_module.parse_arguments()
        assert args.yes is True

    def test_steam_flag(self, gaming_module):
        """--steam flag enables Steam installation."""
        with patch("sys.argv", ["debian_gaming_setup.py", "--steam"]):
            args = gaming_module.parse_arguments()
        assert args.steam is True

    def test_nvidia_flag(self, gaming_module):
        """--nvidia flag enables NVIDIA driver installation."""
        with patch("sys.argv", ["debian_gaming_setup.py", "--nvidia"]):
            args = gaming_module.parse_arguments()
        assert args.nvidia is True

    def test_preset_standard(self, gaming_module):
        """--preset standard is accepted."""
        with patch("sys.argv", ["debian_gaming_setup.py", "--preset", "standard"]):
            args = gaming_module.parse_arguments()
        assert args.preset == "standard"

    def test_preset_choices(self, gaming_module):
        """Invalid preset is rejected."""
        with patch("sys.argv", ["debian_gaming_setup.py", "--preset", "invalid"]):
            with pytest.raises(SystemExit):
                gaming_module.parse_arguments()

    def test_rollback_flag(self, gaming_module):
        """--rollback flag is accepted."""
        with patch("sys.argv", ["debian_gaming_setup.py", "--rollback"]):
            args = gaming_module.parse_arguments()
        assert args.rollback is True

    def test_update_flag(self, gaming_module):
        """--update flag is accepted."""
        with patch("sys.argv", ["debian_gaming_setup.py", "--update"]):
            args = gaming_module.parse_arguments()
        assert args.update is True

    def test_multiple_flags(self, gaming_module):
        """Multiple flags can be combined."""
        with patch("sys.argv", ["debian_gaming_setup.py", "--steam", "--lutris", "-y", "--dry-run"]):
            args = gaming_module.parse_arguments()
        assert args.steam is True
        assert args.lutris is True
        assert args.yes is True
        assert args.dry_run is True


# ═══════════════════════════════════════════════════════════════════════════
# Color Class Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestColor:
    """Tests for the ANSI color utility class."""

    def test_color_codes_are_strings(self, gaming_classes):
        """All color attributes are strings."""
        assert isinstance(gaming_classes.Color.RED, str)
        assert isinstance(gaming_classes.Color.GREEN, str)
        assert isinstance(gaming_classes.Color.END, str)

    def test_color_codes_contain_escape(self, gaming_classes):
        """Color codes contain ANSI escape sequences."""
        assert "\033[" in gaming_classes.Color.RED
        assert "\033[" in gaming_classes.Color.GREEN

    def test_end_resets_formatting(self, gaming_classes):
        """END code is the reset sequence."""
        assert gaming_classes.Color.END == "\033[0m"


# ═══════════════════════════════════════════════════════════════════════════
# Enum Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestEnums:
    """Tests for StrEnum correctness."""

    def test_gpu_vendor_values(self, gaming_classes):
        """GPUVendor enum has expected members."""
        assert gaming_classes.GPUVendor.NVIDIA == "nvidia"
        assert gaming_classes.GPUVendor.AMD == "amd"
        assert gaming_classes.GPUVendor.INTEL == "intel"

    def test_gpu_vendor_is_string(self, gaming_classes):
        """StrEnum members are directly comparable to strings."""
        assert gaming_classes.GPUVendor.NVIDIA == "nvidia"
        assert isinstance(gaming_classes.GPUVendor.NVIDIA, str)

    def test_vm_type_values(self, gaming_classes):
        """VMType enum has expected members."""
        assert gaming_classes.VMType.VMWARE == "vmware"
        assert gaming_classes.VMType.NONE == "none"

    def test_action_type_values(self, gaming_classes):
        """ActionType enum has all 7 action types."""
        assert len(gaming_classes.ActionType) == 7
        assert gaming_classes.ActionType.APT_INSTALL == "apt_install"
        assert gaming_classes.ActionType.GE_PROTON_INSTALL == "ge_proton_install"

    def test_distro_family_values(self, gaming_classes):
        """DistroFamily enum has expected families."""
        assert gaming_classes.DistroFamily.UBUNTU == "ubuntu"
        assert gaming_classes.DistroFamily.DEBIAN == "debian"
        assert gaming_classes.DistroFamily.MINT == "mint"


# ═══════════════════════════════════════════════════════════════════════════
# Dataclass Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestDataclasses:
    """Tests for dataclass construction and defaults."""

    def test_installation_config_defaults(self, gaming_classes):
        """InstallationConfig has correct defaults."""
        config = gaming_classes.InstallationConfig()
        assert config.dry_run is False
        assert config.auto_yes is False
        assert config.create_backup is True
        assert config.enable_rollback is True

    def test_installation_config_field_count(self, gaming_classes):
        """InstallationConfig has the expected number of fields."""
        import dataclasses
        fields = dataclasses.fields(gaming_classes.InstallationConfig)
        # 42 fields as of v3.0.0 — allow tolerance for additions
        assert len(fields) >= 40

    def test_system_info_construction(self, gaming_classes):
        """SystemInfo dataclass constructs with defaults."""
        info = gaming_classes.SystemInfo()
        assert info.distro_name == "Unknown"
        assert info.is_wsl is False

    def test_hardware_info_construction(self, gaming_classes):
        """HardwareInfo dataclass constructs with defaults."""
        info = gaming_classes.HardwareInfo()
        assert info.gpu_vendor == gaming_classes.GPUVendor.UNKNOWN

    def test_rollback_action_construction(self, gaming_classes):
        """RollbackAction dataclass constructs correctly."""
        action = gaming_classes.RollbackAction(
            action_type="apt_install",
            description="test install",
            timestamp="2026-01-01T00:00:00",
            success=True
        )
        assert action.action_type == "apt_install"
        assert action.success is True


# ═══════════════════════════════════════════════════════════════════════════
# Constants Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestConstants:
    """Tests for module-level constants."""

    def test_script_version_format(self, gaming_module):
        """SCRIPT_VERSION follows semver format."""
        version = gaming_module.SCRIPT_VERSION
        parts = version.split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)

    def test_timeout_constants_positive(self, gaming_module):
        """All timeout constants are positive integers."""
        assert gaming_module.TIMEOUT_QUICK > 0
        assert gaming_module.TIMEOUT_NETWORK > 0
        assert gaming_module.TIMEOUT_API > 0
        assert gaming_module.TIMEOUT_DOWNLOAD > 0
        assert gaming_module.TIMEOUT_INSTALL > 0
        assert gaming_module.TIMEOUT_UPDATE > 0

    def test_timeout_ordering(self, gaming_module):
        """Timeouts are ordered from shortest to longest."""
        assert gaming_module.TIMEOUT_QUICK < gaming_module.TIMEOUT_NETWORK
        assert gaming_module.TIMEOUT_NETWORK < gaming_module.TIMEOUT_API
        assert gaming_module.TIMEOUT_API < gaming_module.TIMEOUT_DOWNLOAD
        assert gaming_module.TIMEOUT_DOWNLOAD < gaming_module.TIMEOUT_INSTALL
        assert gaming_module.TIMEOUT_INSTALL < gaming_module.TIMEOUT_UPDATE

    def test_max_response_bytes(self, gaming_module):
        """MAX_RESPONSE_BYTES is 1MB."""
        assert gaming_module.MAX_RESPONSE_BYTES == 1_048_576

    def test_github_constants(self, gaming_module):
        """GitHub constants match the actual repository."""
        assert gaming_module.GITHUB_REPO_OWNER == "Sandler73"
        assert gaming_module.GITHUB_REPO_NAME == "Debian-Gaming-Setup-Project"


# ═══════════════════════════════════════════════════════════════════════════
# get_real_user() Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestGetRealUser:
    """Tests for user context detection."""

    def test_returns_sudo_user(self, gaming_module):
        """Returns SUDO_USER when set."""
        with patch.dict(os.environ, {"SUDO_USER": "alice"}):
            result = gaming_module.get_real_user()
            assert result == "alice"

    def test_falls_back_to_user(self, gaming_module):
        """Falls back to USER when SUDO_USER not set."""
        env = {"USER": "bob"}
        with patch.dict(os.environ, env, clear=True):
            result = gaming_module.get_real_user()
            assert result == "bob"
