"""Test calico run command."""

import pytest

from calico.cmd import run


@pytest.mark.slow
def test_run_imports_successfully(initialized_site, monkeypatch):
    """Test that 'calico run' imports and initializes without errors.

    Note: This is a basic smoke test only.
    Full integration testing would require starting server in background
    and checking it responds, which is complex for smoke tests.
    """
    monkeypatch.chdir(initialized_site)

    # For now, just verify the command can be imported and is callable
    assert run is not None
    assert callable(run)


def test_run_command_exists():
    """Test that run command is properly defined."""
    from calico import cmd

    # Verify run command exists in the cmd module
    assert hasattr(cmd, 'run')
    assert callable(cmd.run)
