"""Test calico init command."""

from click.testing import CliRunner

from calico.cmd import init


def test_init_creates_structure(temp_site_dir):
    """Test that 'calico init' creates expected directory structure."""
    runner = CliRunner()
    result = runner.invoke(init, ['--target', str(temp_site_dir)])

    assert result.exit_code == 0, f'calico init failed: {result.output}'

    # Check expected files/directories exist
    assert (temp_site_dir / 'content').exists()
    assert (temp_site_dir / 'content' / 'index.md').exists()
    assert (temp_site_dir / 'website.py').exists()
    assert (temp_site_dir / 'public' / '.gitkeep').exists()


def test_init_creates_content_files(temp_site_dir):
    """Test that init creates basic content files."""
    runner = CliRunner()
    result = runner.invoke(init, ['--target', str(temp_site_dir)])

    assert result.exit_code == 0

    # Check site.yml exists
    assert (temp_site_dir / 'content' / 'site.yml').exists()

    # Check header area
    assert (temp_site_dir / 'content' / '_header').exists()


def test_init_creates_public_directory(temp_site_dir):
    """Test that init creates public directory with .gitkeep."""
    runner = CliRunner()
    result = runner.invoke(init, ['--target', str(temp_site_dir)])

    assert result.exit_code == 0
    # Check that public directory with .gitkeep exists (for build output)
    assert (temp_site_dir / 'public' / '.gitkeep').exists()
