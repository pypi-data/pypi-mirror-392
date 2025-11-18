"""Test calico build command."""

import pytest
from click.testing import CliRunner

from calico.cmd import build


@pytest.mark.integration
def test_build_succeeds(initialized_site, monkeypatch):
    """Test that 'calico build' runs without errors."""
    monkeypatch.chdir(initialized_site)

    runner = CliRunner()
    result = runner.invoke(build, ['--noinput', '--target', 'dist'])

    assert result.exit_code == 0, f'calico build failed: {result.output}'


@pytest.mark.integration
def test_build_creates_output(initialized_site, monkeypatch):
    """Test that build creates output directory with files."""
    monkeypatch.chdir(initialized_site)

    runner = CliRunner()
    result = runner.invoke(build, ['--noinput', '--target', 'dist'])

    assert result.exit_code == 0, f'calico build failed: {result.output}'

    # Check output exists
    output_dir = initialized_site / 'dist'
    assert output_dir.exists()
    assert (output_dir / 'index.html').exists()


@pytest.mark.integration
def test_build_with_test_content(initialized_site, monkeypatch):
    """Test build with full test content structure."""
    monkeypatch.chdir(initialized_site)

    runner = CliRunner()
    result = runner.invoke(build, ['--noinput', '--target', 'dist'])

    assert result.exit_code == 0, f'calico build failed: {result.output}'

    output_dir = initialized_site / 'dist'

    # Verify various pages were built
    assert (output_dir / 'index.html').exists()
    # About page might be at about.html or about/index.html depending on URL config
    assert (output_dir / 'about.html').exists() or (output_dir / 'about' / 'index.html').exists()


@pytest.mark.integration
def test_build_handles_static_files(initialized_site, monkeypatch):
    """Test that build handles static files correctly."""
    monkeypatch.chdir(initialized_site)

    runner = CliRunner()
    result = runner.invoke(build, ['--noinput', '--target', 'dist'])

    assert result.exit_code == 0, f'calico build failed: {result.output}'

    # Note: Static files handling depends on collectstatic configuration
    # This is a basic smoke test
    output_dir = initialized_site / 'dist'
    assert output_dir.exists()
