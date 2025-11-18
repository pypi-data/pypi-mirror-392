from django.apps import AppConfig

from calico import hook


class SearchConfig(AppConfig):
    name = 'calico_system_plugins.search'
    verbose_name = 'Calico Search Plugin'


@hook
def installed_apps():
    return ['calico_system_plugins.search']


@hook
def calico_js(theme):
    return [
        ('search_lunr', 'js/lunr.min.js'),
        ('search_app', 'js/search.js'),
    ]


@hook
def calico_defaults():
    return {
        'SEARCH_EXCLUDE_PATTERNS': [],
        'SEARCH_FIELDS': ['title', 'content', 'excerpt', 'tags'],
        'SEARCH_REF_FIELD': 'url',
        'SEARCH_BOOST': {
            'title': 10,
            'excerpt': 5,
            'tags': 5,
            'content': 1
        }
    }


@hook
def urlpatterns():
    # Import inside the hook to avoid circular imports
    from django_distill import distill_path

    from .views import SearchIndexView

    return [
        distill_path(
            'calico-lunr.json',
            SearchIndexView.as_view(),
            name='search_index',
            distill_func=lambda: None,
            distill_file='calico-lunr.json'
        ),
    ]
