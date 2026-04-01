"""
═══════════════════════════════════════════════════════════════════════════════
Debian Gaming Setup Script — Test Configuration & Shared Fixtures
═══════════════════════════════════════════════════════════════════════════════

SYNOPSIS:
    pytest conftest providing shared fixtures for all test modules.

DESCRIPTION:
    Handles safe import of the main script (which has top-level side effects
    like directory creation and os.chown), provides mock configurations, and
    shared GamingSetup instances for testing.

VERSION: 3.1.0
"""

import importlib
import os
import sys
import types
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# ---------------------------------------------------------------------------
# Safe import of the main script
# ---------------------------------------------------------------------------
# The script runs top-level code (creates LOG_DIR, BACKUP_DIR, calls os.chown)
# so we must mock those before importing.

_MODULE = None


def _import_gaming_setup():
    """
    Import debian_gaming_setup.py safely by mocking top-level side effects.

    Returns the imported module object. Cached after first call.
    """
    global _MODULE
    if _MODULE is not None:
        return _MODULE

    project_root = Path(__file__).parent.parent
    script_path = project_root / "debian_gaming_setup.py"

    if not script_path.exists():
        pytest.skip("debian_gaming_setup.py not found in project root")

    # Add project root to sys.path for import
    sys.path.insert(0, str(project_root))

    # Create a temporary home directory that the script's top-level code
    # will use for LOG_DIR, BACKUP_DIR, and LOG_FILE
    import tempfile
    tmp_home = tempfile.mkdtemp(prefix="gaming_test_")
    log_dir = os.path.join(tmp_home, "gaming_setup_logs")
    backup_dir = os.path.join(tmp_home, "gaming_setup_backups")
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(backup_dir, exist_ok=True)

    # Mock side effects that occur at module level:
    # - os.chown (requires root)
    # - Use real temp dirs so FileHandler can open log files
    with patch("os.chown"), \
         patch("os.getuid", return_value=0), \
         patch("os.geteuid", return_value=0), \
         patch.dict(os.environ, {
             "SUDO_USER": "testuser",
             "HOME": tmp_home,
             "USER": "testuser",
         }):
        # Use importlib to import by file path
        spec = importlib.util.spec_from_file_location(
            "debian_gaming_setup", str(script_path)
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

    _MODULE = module
    return module


@pytest.fixture(scope="session")
def gaming_module():
    """
    Session-scoped fixture providing the imported gaming setup module.

    All classes, constants, and functions are accessible as attributes.
    """
    return _import_gaming_setup()


@pytest.fixture
def gaming_classes(gaming_module):
    """
    Fixture providing commonly used classes from the module.

    Returns a namespace-like dict with: GamingSetup, InstallationConfig,
    Color, GPUVendor, VMType, DistroFamily, ActionType, etc.
    """
    return types.SimpleNamespace(
        GamingSetup=gaming_module.GamingSetup,
        InstallationConfig=gaming_module.InstallationConfig,
        Color=gaming_module.Color,
        GPUVendor=gaming_module.GPUVendor,
        VMType=gaming_module.VMType,
        DistroFamily=gaming_module.DistroFamily,
        InstallationPhase=gaming_module.InstallationPhase,
        ActionType=gaming_module.ActionType,
        SystemInfo=gaming_module.SystemInfo,
        HardwareInfo=gaming_module.HardwareInfo,
        RollbackAction=gaming_module.RollbackAction,
        BackupEntry=gaming_module.BackupEntry,
    )


@pytest.fixture
def mock_args(gaming_module):
    """
    Fixture providing a minimal argparse.Namespace mimicking CLI defaults.

    All flags default to False, preset to None, dry_run to False.
    Patches sys.argv since parse_arguments() reads from it directly.
    """
    with patch("sys.argv", ["debian_gaming_setup.py"]):
        ns = gaming_module.parse_arguments()
    return ns


def _create_mock_setup(gaming_module, args):
    """Helper to create a GamingSetup instance with all side effects mocked."""
    with patch.object(gaming_module.GamingSetup, "check_root"), \
         patch.object(gaming_module.GamingSetup, "load_installation_state"), \
         patch.object(gaming_module.GamingSetup, "load_rollback_manifest"), \
         patch.object(gaming_module.GamingSetup, "_setup_signal_handlers"), \
         patch("os.chown"), \
         patch("os.makedirs"):
        setup = gaming_module.GamingSetup(args)
    return setup


@pytest.fixture
def mock_setup(gaming_module, mock_args):
    """
    Fixture providing a GamingSetup instance with mocked system interactions.

    Safe to use — all subprocess calls, file I/O, and root checks are mocked.
    """
    return _create_mock_setup(gaming_module, mock_args)


@pytest.fixture
def parse_version(gaming_module, mock_args):
    """Fixture providing direct access to _parse_version as a standalone callable."""
    setup = _create_mock_setup(gaming_module, mock_args)
    return setup._parse_version
