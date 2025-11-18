import os
import sys
from copy import copy
from pathlib import Path

import djp
from django.urls import include
from dotenv import load_dotenv
from nanodjango.app import Django, exec_manage
from nanodjango.exceptions import ConfigurationError, UsageError
from nanodjango.urls import urlpatterns

import calico

from .mappers import mapper
from .utils import S_DEFAULTS


def env_true(val):
    return val in (True, 'true', 'True', 'TRUE', 1, '1')


CALICO_BASE = Path(calico.__file__).parent
BASEDIR = Path(os.getcwd())
BUILTIN_PLUGIN_DIRS = {
    'calico_system_plugins': CALICO_BASE.parent / 'calico_system_plugins',
}

SETTINGS = {
    'SECRET_KEY': 'unused',
    'PUBLIC_DIR': BASEDIR / 'public',
    'ND_APP_NAME': 'calico_site',
    'ROOT_URLCONF': 'calico.urls',
    'ADMIN_URL': None,
    'STATICFILES_DIRS': [BASEDIR / 'static', BASEDIR / 'public'],
    'PLUGIN_HOOKSPECS': [
        'djp.hookspec',
        'calico.hookspec',
    ],
    'PLUGIN_MANAGER': calico.pm,
    'LANGUAGES': [('en-us', 'English')],
    'MARKDOWN_DEUX_STYLES': {
        'default': {
            'extras': {
                'cuddled-lists': True,
                'fenced-code-blocks': None,
                'html-classes': {'pre': 'prettyprint'},
                'nofollow': True,
                'strike': True,
                'tables': True,
                'target-blank-links': True,
                'task_list': True,
            },
            'safe_mode': False,
        }
    },
    'CALICO_LANGUAGES': [
        ('', 'English'),
    ],
    'ANGLES': {
        'mappers': mapper,
        'default_mapper': 'calico.mappers.map_component',
        'wrap_tags': False,
        'component_folder': 'widgets',
        'initial_tag_regex': r'(dj-|cc-|\$)',
    },
    'STORAGES': {
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
        },
        'staticfiles': {
            'BACKEND': 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage',
        },
    },
}

C_SETTINGS = {
    'INSTALLED_APPS': (
        'django.contrib.sitemaps',
        'django.contrib.staticfiles',
        'markdown_deux',
        'django_distill',
        'calico',
    ),
    'MIDDLEWARE': (
        'django.middleware.security.SecurityMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ),
}


class Calico(Django):
    def __init__(
        self,
        theme=None,
        plugins=None,
        exclude_plugins=None,
        css=None,
        js=None,
        EXTRA_APPS=None,
        DEBUG=True,
        prevent_whitenoise=False,
        **_settings,
    ):
        load_dotenv('.env')
        debug = env_true(os.environ.get('DEBUG', DEBUG))

        settings = copy(_settings)
        settings['DEBUG'] = debug

        # Default Django settings for calico
        for key, val in SETTINGS.items():
            settings.setdefault(key, val)

        # Clico specific default settings
        for k, val in S_DEFAULTS.items():
            key = f'CALICO_{k}'
            settings.setdefault(key, val)

        # Minimun INSTALLED_APPS and MIDDLEWARE for calico
        installed = settings.get('INSTALLED_APPS', list(C_SETTINGS['INSTALLED_APPS']))
        middleware = settings.get('MIDDLEWARE', list(C_SETTINGS['MIDDLEWARE']))

        if debug:
            # In development, we want the browser to auto_reload
            installed += [
                'django_browser_reload',
            ]
        elif not prevent_whitenoise:
            # In production (build_time), we most likely want to use whitenoise
            installed = ['whitenoise.runserver_nostatic', *installed]

        if plugins is None:
            # Automatic gathering of plugins
            builtin_plugins = calico.get_plugins_in_dirs(BUILTIN_PLUGIN_DIRS)
            pip_plugins = calico.get_pip_installed_plugins(group='djp')
            user_plugins = calico.get_plugins_in_dirs({'plugins': BASEDIR / 'plugins'})
            all_plugins = {**builtin_plugins, **pip_plugins, **user_plugins}
        else:
            all_plugins = plugins

        settings.setdefault('PLUGINS', calico.load_plugins(all_plugins, exclude_plugins=exclude_plugins or []))

        # Grabbing extra default settings from installed plugins
        for key, val in calico.default_calico_settings().items():
            settings.setdefault(key, val)

        # A theme can be a combination of multiple themes
        if theme is None:
            theme = calico.available_themes()
        elif isinstance(theme, str):
            theme = [theme]
        self._theme = theme

        # Themes should always be loaded first as they are likely to override calico or apps
        # templates
        installed = theme + installed
        if EXTRA_APPS:
            installed += EXTRA_APPS

        settings.setdefault('INSTALLED_APPS', installed + djp.installed_apps())
        settings.setdefault('MIDDLEWARE', djp.middleware(middleware))
        settings.setdefault(
            'TEMPLATES',
            [
                {
                    'BACKEND': 'django.template.backends.django.DjangoTemplates',
                    'DIRS': [],
                    'OPTIONS': {
                        'context_processors': [
                            'django.template.context_processors.debug',
                            *calico.get_list_from_hook('context_processors'),
                        ],
                        'loaders': [
                            (
                                'django.template.loaders.cached.Loader',
                                [
                                    'dj_angles.template_loader.Loader',
                                    'django.template.loaders.filesystem.Loader',
                                    'django.template.loaders.app_directories.Loader',
                                    *calico.get_list_from_hook('template_loaders'),
                                ],
                            )
                        ],
                        'builtins': [
                            'calico.templatetags.calico',
                            'yak.templatetags.yak',
                            'markdown_deux.templatetags.markdown_deux_tags',
                            'django.templatetags.static',
                            *calico.auto_load_tags(),
                        ],
                    },
                }
            ],
        )

        for media in ('js', 'css'):
            if (override := locals()[media]) and hasattr(settings, f'CALICO_{media.upper()}_URLS'):
                raise ConfigurationError(f"Don't pass both {media} and CALICO_{media.upper()}_URLS, prefer {media}")

            setattr(self, f'_{media}', override)
            settings.setdefault(f'CALICO_{media.upper()}_URLS', calico.calico_media(media, theme, extra=override))

        super().__init__(**settings)

        if debug:
            self.route('__reload__/', include=include('django_browser_reload.urls'))

        self.route('', include=include('calico.urls'))

    def _prestart(self, host):
        """
        Common steps before start() and serve().
        Mostly copied from nanodjango with database-related steps run conditionally.

        Returns:
            (host: str, port: int)
        """

        from django.conf import settings

        from .utils import calico_setting

        # Be helpful and check sys.argv for the host in case the script is run directly
        if host is None:
            if len(sys.argv) > 2:
                raise UsageError('Usage: start [HOST]')
            elif len(sys.argv) == 2:
                host = sys.argv[1]
            else:
                host = '0:8000'

        port = 8000
        if ':' in host:
            host, _port = host.split(':')
            port = int(_port)
        elif not host:
            host = '0'

        if getattr(settings, 'DATABASES', None) and calico_setting('HAS_DB'):
            exec_manage('makemigrations', self.app_name)
            exec_manage('migrate')

            if 'django.contrib.auth' in settings.INSTALLED_APPS:
                from django.contrib.auth import get_user_model

                User = get_user_model()
                if User.objects.count() == 0:
                    exec_manage('createsuperuser')

        return host, port

    def _prepare(self, is_prod=False):
        """
        Perform any final setup for this project after it has been imported:

        * detect if it has been run directly; if so, register it as an app
        * register the admin site
        * if in production mode, collectstatic into STATIC_ROOT
        * if in development mode, extend urls to serve media files
        """
        from django import urls as django_urls
        from django.conf.urls.static import static
        from django.contrib import admin
        from django.db.models import Model

        # Check if this is being called from click commands or directly
        if self.app_name not in sys.modules:
            # Hasn't been run through the ``nanodjango`` or ``calico`` command
            if '__main__' not in sys.modules or getattr(sys.modules['__main__'], self.instance_name) != self:
                # Doesn't look like it was run directly either
                raise UsageError('App module not initialised')

            # Run directly, so register app module so Django won't try to load it again
            sys.modules[self.app_name] = sys.modules['__main__']

        # If there are no models in this app, remove it from the migrations
        if not any(
            isinstance(obj, type) and issubclass(obj, Model)
            for obj in self.app_module.__dict__.values()
            if getattr(obj, '__module__', None) == self.app_name
        ):
            from django.conf import settings

            if self.app_name in settings.MIGRATION_MODULES:
                del settings.MIGRATION_MODULES[self.app_name]

        # Register the admin site
        admin_url = self.settings.ADMIN_URL
        if admin_url or self.has_admin:
            if admin_url is None:
                admin_url = 'admin/'
            if not isinstance(admin_url, str) or not admin_url.endswith('/'):
                raise ConfigurationError('settings.ADMIN_URL must be a string path ending in /')
            urlpatterns.append(django_urls.path(admin_url.removeprefix('/'), admin.site.urls))

        # Register the API, if defined
        if self._api:
            self.route(self.settings.API_URL, include=self._api.urls)

        # serve media
        if self.settings.MEDIA_ROOT and Path(self.settings.MEDIA_ROOT).exists():
            urlpatterns.extend(static(self.settings.MEDIA_URL, document_root=self.settings.MEDIA_ROOT))

        self._prepared = True
