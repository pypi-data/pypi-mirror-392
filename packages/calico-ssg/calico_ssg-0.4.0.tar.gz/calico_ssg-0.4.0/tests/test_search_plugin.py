"""Test search plugin functionality."""

import json
from pathlib import Path


def test_search_plugin_importable():
    """Test that search plugin can be imported."""
    from calico_system_plugins import search

    assert search is not None


def test_search_plugin_has_apps_config():
    """Test that search plugin has Django AppConfig."""
    from calico_system_plugins.search import apps

    assert hasattr(apps, 'SearchConfig')


def test_search_plugin_hooks():
    """Test that search plugin implements expected hooks."""
    from calico_system_plugins.search import apps

    # Test installed_apps hook
    assert hasattr(apps, 'installed_apps')
    installed = apps.installed_apps()
    assert 'calico_system_plugins.search' in installed

    # Test calico_js hook
    assert hasattr(apps, 'calico_js')
    js_files = apps.calico_js(theme='pico')
    assert len(js_files) == 2
    assert any('lunr.min.js' in str(item) for item in js_files)
    assert any('search.js' in str(item) for item in js_files)

    # Test calico_defaults hook
    assert hasattr(apps, 'calico_defaults')
    defaults = apps.calico_defaults()
    assert 'SEARCH_EXCLUDE_PATTERNS' in defaults
    assert 'SEARCH_FIELDS' in defaults
    assert 'SEARCH_REF_FIELD' in defaults
    assert 'SEARCH_BOOST' in defaults

    # Test urlpatterns hook
    assert hasattr(apps, 'urlpatterns')
    patterns = apps.urlpatterns()
    assert len(patterns) > 0


def test_search_templates_exist():
    """Test that search widget templates exist."""
    import calico_system_plugins.search

    plugin_path = Path(calico_system_plugins.search.__file__).parent
    widget_template = plugin_path / 'templates' / 'widgets' / 'search.html'

    assert widget_template.exists()


def test_search_static_files_exist():
    """Test that search static files exist."""
    import calico_system_plugins.search

    plugin_path = Path(calico_system_plugins.search.__file__).parent

    # Check JavaScript files
    lunr_js = plugin_path / 'static' / 'js' / 'lunr.min.js'
    search_js = plugin_path / 'static' / 'js' / 'search.js'

    assert lunr_js.exists()
    assert search_js.exists()

    # Verify lunr.min.js is not empty and looks like minified JS
    lunr_content = lunr_js.read_text()
    assert len(lunr_content) > 1000  # Should be substantial
    assert 'lunr' in lunr_content.lower()

    # Verify search.js exists and has expected functions
    search_content = search_js.read_text()
    assert 'fetch' in search_content or 'XMLHttpRequest' in search_content
    assert 'lunr' in search_content


def test_search_index_builds(initialized_site, tmp_path):
    """Test that search index is generated when building a site."""
    import subprocess

    # Build the site
    output_dir = tmp_path / 'output'
    result = subprocess.run(
        ['calico', 'build', '--target', str(output_dir), '--noinput'],
        cwd=initialized_site,
        capture_output=True,
        text=True,
    )

    # Build should succeed
    assert result.returncode == 0, f"Build failed: {result.stderr}"

    # Check that search index was generated
    search_index = output_dir / 'calico-lunr.json'
    assert search_index.exists(), "Search index file not generated"

    # Verify index structure
    index_data = json.loads(search_index.read_text())
    assert 'schema' in index_data
    assert 'documents' in index_data

    # Verify schema
    schema = index_data['schema']
    assert 'fields' in schema
    assert 'ref' in schema
    assert 'boost' in schema

    # Verify we have some documents
    documents = index_data['documents']
    assert len(documents) > 0

    # Check document structure
    doc = documents[0]
    assert 'id' in doc
    assert 'url' in doc
    assert 'title' in doc
    assert 'content' in doc
