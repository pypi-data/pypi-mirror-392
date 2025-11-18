from pluggy import HookspecMarker


hook_def = HookspecMarker('djp')


@hook_def
def declare_theme():
    """
    Returns a list of available_themes.
    One or more of those themes will be at the top of INSTALLED_APPS.
    """


@hook_def
def auto_load_tags():
    """
    Returns a list of templatetags that should be automatically loaded by
    Django's template engine.
    """


@hook_def
def calico_css(theme):
    """
    returns a mapping of names css files to load on each page
    """


@hook_def
def calico_js(theme):
    """
    returns a mapping of named js files to load on each page
    """


@hook_def
def calico_defaults():
    """
    returns a mapping of default settings
    """


@hook_def
def context_processors():
    """
    returns a list of extra context processors
    """


@hook_def
def template_loaders():
    """
    returns a list of extra template loaders
    """


@hook_def
def site_groupings():
    """
    returns a mapping of extra site collections
    """
