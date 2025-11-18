from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import ClassVar

from django.conf import settings
from django.templatetags.static import static
from django.utils.functional import lazy

from . import default_calico_settings


S_DEFAULTS = {
    'CONTENT_COMPONENTS': ['header', 'footer'],
    'DATE_FORMATS': ('%Y-%m-%d %H:%M', '%Y-%m-%d'),
    'FORCE_HTTP': False,
    'FORCE_HTTPS': True,
    'HAS_DB': False,
    'HOST': 'localhost',
    'LANGUAGES': [],
    'TAGS_PAGE': 'tags',
    'THUMBS': {
        'xs': (576, 576),
        'sm': (767, 767),
        'md': (991, 991),
        'lg': (1200, 768),
        'xl': (1400, 900),
        'xxl': (1920, 1080),
        'xxxl': None,
    },
    'THUMBS_SUBDIR': '_resized',
}

S_DEFAULTS.update(default_calico_settings())


def calico_setting(key, default=None):
    value = None
    if key == 'CONTENT_DIR':
        value = getattr(settings, f'CALICO_{key}', None)
    else:
        value = getattr(settings, f'CALICO_{key}', S_DEFAULTS.get(key))

    # Needed if app was not fully initialized yet
    if value is None:
        from calico import default_calico_settings

        c_settings = default_calico_settings()

        if key == 'CONTENT_DIR' and 'CONTENT_DIR' not in c_settings and default is None:
            value = Path(getattr(settings, 'BASE_DIR', Path.cwd())) / 'content'
        else:
            value = c_settings.get(key, default)
    return value


def date_from_str_func(date_str):
    for fmat in calico_setting('DATE_FORMATS'):
        if isinstance(date_str, date):
            return date_str

        if isinstance(date_str, datetime):
            return date_str.date

        try:
            return datetime.strptime(date_str, fmat)
        except ValueError:
            continue


def get_tags(author_slug):
    from .models import Page

    subdir = calico_setting('BLOG_DIR')
    tags = defaultdict(list)
    for post in Page.pages_in_dir(subdir=subdir):
        post.metadata['published_date'] = post.published_at
        post.metadata['url'] = post.url
        if 'tags' in post.metadata and (not author_slug or author_slug == post.metadata.get('author', None)):
            for tag in post.metadata['tags']:
                tags[tag].append(post)
    return sorted(tags.items(), key=lambda x: -len(x[1]))


def unique_extend(orig, lst):
    orig.extend([p for p in lst if p not in orig])


class Singleton(type):
    _instances: ClassVar[dict] = {}  # intentionally mutable

    def __call__(cls, *args, **kwargs):
        kwhash = tuple(kwargs.items())
        ahash = tuple(args)
        instance = cls._instances.get((cls, ahash, kwhash))

        if settings.DEBUG or not instance:
            instance = super().__call__(*args, **kwargs)
            cls._instances[(cls, ahash, kwhash)] = instance

        return instance


class Extractor(metaclass=Singleton):
    def __init__(self, page):
        self.page = page
        self.data = page.get_metadata()

    def __getattr__(self, prop):
        rv = self.data[prop] if prop in self.data else getattr(self.page, prop)

        if isinstance(rv, str) and rv.startswith('_'):
            method, *args = rv.split('::')
            return getattr(self, f'extract{method}')(*args)

        return rv

    def get(self, prop, default=None):
        try:
            return getattr(self, prop)
        except AttributeError:
            return default

    def extract_dir(self, index=0):
        *page_path, _file = self.page.slug.split('/')
        if index >= len(page_path):
            return None
        return page_path[-1 - index]


_lazy_static = lazy(static, str)


def static_or_not(value):
    return value if value.startswith(('http', '//')) else _lazy_static(value)
