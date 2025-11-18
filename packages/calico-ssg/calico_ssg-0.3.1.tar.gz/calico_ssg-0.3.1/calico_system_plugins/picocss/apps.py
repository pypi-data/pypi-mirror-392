from django.apps import AppConfig

from calico import hook


class PicoCssConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'calico_system_plugins.picocss'


@hook
def declare_theme():
    return [('base_theme', PicoCssConfig.name)]


@hook
def calico_css(theme):
    if PicoCssConfig.name not in theme:
        return []

    return [('default_css', [
        'https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css',
        'css/pico-calico.css',
    ])]


@hook
def calico_js(theme):
    if PicoCssConfig.name not in theme:
        return []

    return [('alpinejs', 'https://cdn.jsdelivr.net/npm/alpinejs@3.14.1/dist/cdn.min.js')]
