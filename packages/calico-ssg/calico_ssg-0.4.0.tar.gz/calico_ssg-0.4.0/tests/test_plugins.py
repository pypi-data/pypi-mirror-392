"""Test plugin system."""


def test_system_plugins_importable():
    """Test that system plugins can be imported."""
    from calico_system_plugins import blog, collections, picocss

    assert blog is not None
    assert collections is not None
    assert picocss is not None


def test_blog_plugin_has_apps_config():
    """Test that blog plugin has Django AppConfig."""
    from calico_system_plugins.blog import apps

    assert hasattr(apps, 'BlogConfig')


def test_picocss_plugin_has_apps_config():
    """Test that picocss plugin has Django AppConfig."""
    from calico_system_plugins.picocss import apps

    assert hasattr(apps, 'PicoCssConfig')


def test_collections_plugin_has_apps_config():
    """Test that collections plugin has Django AppConfig."""
    from calico_system_plugins.collections import apps

    assert hasattr(apps, 'CollectionsConfig')
